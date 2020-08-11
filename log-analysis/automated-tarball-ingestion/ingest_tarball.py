import argparse
import os
import shutil
import yaml
import subprocess
from pathlib import Path
from copy import deepcopy
import zipfile
import tarfile
import fnmatch

from helper_classes.filebeat_yml import FilebeatYML

from elasticsearch import Elasticsearch
es = Elasticsearch()

project_root_path = os.path.dirname(os.path.realpath(__file__))
tarballs_to_ingest_dir_path = f"{project_root_path}/log-tarballs-to-ingest"

class IngestTarball:
    """
    Class to model a single tarball's ingestion process

    Currently only support running for a single tarball at a time
    """
    client_name = ""
    tarball_filename = ""

    hostnames = []

    # whatever directory was archived
    archived_dir_name = ""

    debug_mode = False

    # set to true if you want to clear out all filebeat-* indices in ES AND rm -rf the filebeat registry at /var/lib/filebeat/registry/filebeat/*
    clean_out_filebeat_first = False

    def __init__(self, tarball_filename, client_name, **kwargs):
        self.tarball_filename = tarball_filename

        # absolute path to the tar ball
        self.tarball_path = f"{tarballs_to_ingest_dir_path}/{self.tarball_filename}"

        # the name of the client (or some sort of human readable identifier for them), e.g., example-company
        self.client_name = client_name

        """
        We generate the incident time and use it as an incident_id
        - We want it to be unique for this file but ideally the same for everytime the file runs (ie idempotent)
        - Consequently we will grab metadata from the tarball itself and use as the incident_id
        - modified time will be something like 1596785608.063104 (unix timestamp)
        - since moving counts as modifying, will be when we put the tarball into the log-tarballs-to-ingest folder
        """
        tarball_modified_time = os.path.getmtime(self.tarball_path)
        self.incident_id = tarball_modified_time

        # where we will set the logs for this client (so each client has their own dir)
        self.path_for_client = f"{project_root_path}/logs-for-client/{self.client_name}" 

        self.base_filepath_for_logs = f"{self.path_for_client}/incident-{self.incident_id}"

        # where we will extract the tarball to (temporarily)
        self.extract_dest_path = f"{self.base_filepath_for_logs}/tmp"

        # relative path from parent dir (the root of the tarball) to the nodes
        self.path_to_nodes_dir = "nodes"

        self.filebeat_yml = FilebeatYML(project_root_path=project_root_path, base_filepath_for_logs=self.base_filepath_for_logs, path_for_client=self.path_for_client, **kwargs)

        ##################
        # other options
        ##################
        self.clean_out_filebeat_first = kwargs.get("clean_out_filebeat_first", False)
        self.clean_up_on_finish = kwargs.get("clean_up_on_finish", False)

    ###################################################
    # the operations we run when ingesting the tarball
    ###################################################

    def extract_tarball(self):
        """
        Unzips the tar ball to tmp folder, before we place files where they need to go
        - We want to extract our tarball into a directory namespaced for this tarball
            * that way, if we ever run this ingest_tarball job at the same time as other jobs for other clients or same client but other tarballs, we don't want simultaneous jobs to collide or mess up each other. 
            * That's why we're still using base_filepath_for_logs and not just some random dir as extract destination
        """

        # tmp folder before positioning them where we want them
        shutil.unpack_archive(self.tarball_path, self.extract_dest_path)

        # get the archived directory's name
        print("self.extract_dest_path", self.extract_dest_path)
        for child in os.listdir(self.extract_dest_path):
            # there should only be one, the archived directory. If ran before, also maybe a filebeat.yml
            if not os.path.isdir(os.path.join(self.extract_dest_path, child)):
                # skip this
                # required since we add our filebeat.yml to this dir later, so if we want this script to be idempotent skip all non-dirs
                print("skipping child", child)
                continue

            self.archived_dir_name = child
            break

        print("self.archived_dir_name is:", self.archived_dir_name)

    def position_log_files(self):
        """
        put all log files where we want them
        """
        # there should be a parent directory called "nodes"
        nodes_dir = os.path.join(self.extract_dest_path, self.archived_dir_name, self.path_to_nodes_dir)

        # "nodes" has several subdirectories, one directory per node in their cluster
        all_dirs_for_nodes = os.listdir(nodes_dir)

        # iterate over each node's directory and put their logs where they should go
        for dir_for_node in all_dirs_for_nodes:
            # original hostname where the logs were genereated. Can be domain name or ip addr. Used to identify that C* node and distinguish it from other nodes in the client's cluster
            if not os.path.isdir(os.path.join(nodes_dir, dir_for_node)):
                # not a directory, skip it. there must be some random files in here
                continue

            # get node's hostname from the directory name (ie the final part of the path)
            hostname = os.path.basename(os.path.normpath(dir_for_node))
            self.hostnames.append(hostname)

            # iterate over our log_type_definitions, and set all the paths we need into our yml

            for key, log_type_def in self.filebeat_yml.log_type_definitions.items():
                if log_type_def.get("path_to_logs_source", None) is None:
                    # we're not supporting yet
                    continue

                # for now, just assume all are cassandra logs (which is probably wrong)
                # move the files for this node and log_type
                self.position_log_files_for_node(hostname, log_type_def, nodes_dir)

    # NOTE not using currently. Only if we want all files everywhere. Currently we're just targeting the /logs dir
    def position_log_files_for_node(self, hostname, log_type_def, nodes_dir, **kwargs):
        """
        For a directory that contains logs for a single node and a single log_type_def of that node:
        put to each individual log files that were extracted from the tarball into the place they should go
        - just goes into <node_hostname>/logs/cassandra (or whatever our self.path_to_cassandra_logs is) and grabs those logs
        """
        # now we want to move them from original_dir to where filebeat will find them

        # all the files in the tmp directory we just made will be moved from source to dest
        source_dir = os.path.join(nodes_dir, log_type_def["path_to_logs_source"].replace("<hostname>", hostname))
        dest_dir_path = os.path.join(
            self.base_filepath_for_logs,
            log_type_def["path_to_logs_dest"].replace("<hostname>", hostname)
        )

        # make sure dir exists, especially important for spark and solr logs
        if not os.path.isdir(source_dir):
            print("host", hostname, "doesn't have directory so skipping", source_dir)
            # continue
            return

        # if zipped, unzip
        # TODO consider using shutil.unpack_archive since it seems to handle all kinds just fine
        if log_type_def.get("zipped", False):
            all_files = os.listdir(source_dir)
            # Not necessarily zipped, since often zipped files are mixed in with unzipped in these dirs. 
            if log_type_def["zip_format"] == "zip":
                pattern = log_type_def.get("zip_extension_regex", "*.zip")
                unzipper = zipfile.ZipFile

            elif log_type_def["zip_format"] == "tar":
                unzipper = tarfile.TarFile
                # might need to add just .tars and others here too TODO
                pattern = log_type_def.get("zip_extension_regex", "*.tar.gz")

            # unzip all zipped files
            # https://stackoverflow.com/a/30591949/6952495
            # TODO if we need to, could go recursive right here. But if we do, make sure all logs still end up in source_dir so they're easy to grab in the next step
            for filename in fnmatch.filter(all_files, pattern):
                zipfile_path = os.path.join(source_dir, filename)
                with unzipper(zipfile_path, 'r') as zip_ref:

                    # just putting in the parent dir, so all logs will end up in one place
                    zip_ref.extractall(source_dir)

        # these should all be unzipped at this point
        all_files = os.listdir(source_dir)

        # TODO filter out filenames that don't match our regex ?? doesn't seem super necessary, since filebeat will filter. This would only save diskspace for us
        for filename in all_files:
            # filename should be str and not include path, e.g., `gc.log.0.current` 
            source_path = os.path.join(source_dir, filename)

            # make sure the directory exists
            Path(dest_dir_path).mkdir(parents=True, exist_ok=True)

            # if specify the filename, then will overwrite what's there, which is what we want for idempotency
            dest_path = os.path.join(dest_dir_path, filename)

            # move it
            shutil.move(source_path, dest_path)

    def generate_filebeat_yml(self):
        """
        generates a filebeat.yml file for this tarball's logs
        See docs on filebeat_yml.generate for more
        """
        self.filebeat_yml.hostnames = self.hostnames
        self.filebeat_yml.generate()

    def clear_filebeat_indices_and_registry(self):
        # ignore 404 and 400
        # es.indices.delete(index='filebeat-*', ignore=[400, 404])

        if self.clean_out_filebeat_first:
            print("clearing filebeat indices")
            es.indices.delete(index='filebeat-*')

            # this makes sure filebeat will re-ingest all files when it runs again
            print("clearing filebeat registry")
            # check=True means throw errors if they happen
            subprocess.run("sudo rm -rf /var/lib/filebeat/registry/filebeat", shell=True, check=True)

        else:
            print("Option to clear filebeat indices and registry not set, continuing on.")

    def run_filebeat(self, **kwargs):
        """
        NOTE assumes that rest of ELK stack is already running
        """
        if kwargs.get("run_with_docker", False):
            # TODO currently not supported
            pass
        else:
            # -e        Logs to stderr and disables syslog/file output.
            # -d "*"    Enable debugging for all components
            # --c       Specifies the configuration file to use for Filebeat

            start_filebeat_cmd = f'sudo filebeat -e -d "*" --c {self.filebeat_yml.file_path}'
            # same thing, but more conservative logging
            # start_filebeat_cmd = f'sudo filebeat -e --c {self.filebeat_yml.file_path}'

            print(f"Running filebeat command: {start_filebeat_cmd}")

            # TODO error handle this
            os.system(start_filebeat_cmd)


    def cleanup(self, successful):
        """
        Does whatever needs to be done after the job is successful, or after the job failed for that matter
        for now archiving tarball, but in the future maybe not
        - the individual log files can be left where they were, since unless filebeat is reset, it shouldn't run on those files again 
        - though it might be worth revisiting this; maybe change this and delete these later, especially if client doesn't want us to keep anything. But that would probably be done by another job, after all analysis is completed
        """
        if successful:
            if self.clean_up_on_finish:
                # remove everything we generated using this script
                shutil.rmtree(self.path_for_client)
        else:
            # this is it for now
            print("failed to ingest tarball")

    ###################################################
    # do it all
    ###################################################
    def run(self):
        successful = False
        try:
            print("\n=== Extracting tarball ===")
            self.extract_tarball()
            print("\n=== Positioning Log files ===")
            self.position_log_files()
            print("\n=== Generating filebeat yml ===")
            self.generate_filebeat_yml()
            print("\n=== Clearing Filebeat data (?) ===")
            self.clear_filebeat_indices_and_registry()
            print("\n=== Running Filebeat ===")
            self.run_filebeat()
            successful = True

        except Exception as e:
            # currently not catching
            successful = False
            raise e

        # no matter what, cleanup
        print("=== Cleaning up ===")
        self.cleanup(successful)

        if successful:
            print("Success.")

if __name__ == '__main__':
    """
    Instructions:
    1) Place a log tarball in `./log-tarballs-to-ingest/` (currently not automating, you have to do this manually)

    2)- Run script passing in args to provide metadata about the tarball
        Args:
            - tarball_filename: filename of our tarball
            - client_name: (make this consistent for the company, for every company there should only be one)

    Call like:
        python3 ingest_tarball.py example-logs.tar.gz my-company 123.456.789.101
    """
    parser = argparse.ArgumentParser(
        description='Converting Stats Form TXT TO CSV Format',
        usage='{tarball_filename} {company_name}')
    parser.add_argument('tarball_filename', type=str, help='name of archive file (e.g., tarball-for-my-client.tar.gz). Can be .tar.gz or .zip')
    parser.add_argument('client_name', type=str, help='name of client')
    parser.add_argument('--clean-out-filebeat-first', dest='clean_out_filebeat_first', action='store_true')
    parser.set_defaults(clean_out_filebeat_first=False)
    parser.add_argument('--debug-mode', dest='debug_mode', action='store_true')
    parser.set_defaults(debug_mode=False)
    parser.add_argument('--custom-config', 
                        dest='custom_config',
                        action='append',
                        nargs=2,
                        metavar=('config_key', 'config_value'),
                        help='Add whatever custom config you want for generating the filebeat.yml. Can be used multiple times. E.g., `--custom-config output.elasticsearch.hostname 127.0.0.1 --custom-config kibana.hostname 123.456.789.101 --custom-config output.kibana.enabled false --custom-config processors.2.timestamp.ignore_failure false`. Use integers (as in the example above) for array indices. This will override any other setting, since it sets fields after everything else.'
                        )
    parser.set_defaults(custom_config=[])
    parser.add_argument('--cleanup-on-finish', dest='clean_up_on_finish', action='store_true', help="If runs successfully, clears out everything created except for the original tarball")
    parser.set_defaults(debug_mode=False)

    args = parser.parse_args()

    options = {
        "clean_out_filebeat_first": args.clean_out_filebeat_first,
        "clean_up_on_finish": args.clean_up_on_finish,
        "debug_mode": args.debug_mode,
        "custom_config": args.custom_config,
    }

    ingestTarball = IngestTarball(args.tarball_filename, args.client_name, **options)
    ingestTarball.run()
