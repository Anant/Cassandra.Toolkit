import argparse
import os
import shutil
import yaml
import subprocess
from pathlib import Path

from elasticsearch import Elasticsearch
es = Elasticsearch()

dir_path = os.path.dirname(os.path.realpath(__file__))
tarballs_to_ingest_dir_path = f"{dir_path}/log-tarballs-to-ingest"

class IngestTarball:
    """
    Class to model a single tarball's ingestion process

    Currently only support running for a single tarball at a time
    """
    client_name = ""
    tarball_filename = ""

    # whether we have to go in and unzip child directories as well (ie they have zips inside of zips)
    # TODO have to handle these
    has_child_zips = False

    hostnames = []

    # whatever directory was archived
    archived_dir_name = ""

    debug_mode = False

    # set to true if you want to clear out all filebeat-* indices in ES AND rm -rf the filebeat registry at /var/lib/filebeat/registry/filebeat/*
    clean_out_filebeat_first = False

    """
    all metadata related to a given log 
    - main key:      (e.g., cassandra.main) is arbitrarily chosen for use in this script. Will be referred to generally using var `log_type` in this script.
    - tags:          should match what we have tagged in filebeat.template.yml filebeat.inputs field exactly, so this definition can find that filebeat.input field
    - path_to_logs_source:  path from base path for this tarball to the direct parent directory that holds these logs (if there are logs nested within subdirectories, make a new log_type_definitions key for those). Will replace all names within <> dynamically.
    - path_to_logs_dest:  path to where we want these so filebeat can find them
    - log_regex:     regex to use to find all these logs that we want from that parent directory

    To not do a certain kind of log, just put None in the path_to_logs and we'll skip it. Or comment the whole thing out of course.

    ADDING A NEW LOG TYPE
    - add a definition here with all the keys
    - add the fields in filebeat.template.yml as well
    """
    log_type_definitions = {
        "cassandra.main": {
            "path_to_logs_source": "<hostname>/logs/cassandra",
            "path_to_logs_dest": "<hostname>/logs/cassandra",
            "tags": ["cassandra","main"],
            "log_regex": "<self.base_filepath_for_logs>/<hostname>/cassandra/system.log*",
        },
        "system": {
            # NOTE: This is for a finding system logs, not cassandra logs
            "path_to_logs": None, # TODO set this when we have a path
            "tags": ["system","messages"],
            "log_regex": "<self.base_filepath_for_logs>/<hostname>/system/*.test",
        },
        "spark": {
            "path_to_logs": None, # TODO
            "tags": [],
            "log_regex": "",
        },
    }

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
        self.path_for_client = f"{dir_path}/logs-for-client/{self.client_name}" # /{self.hostname}/{self.log_type}"

        self.base_filepath_for_logs = f"{self.path_for_client}/incident-{self.incident_id}"

        # where the filebeat.yml will go
        self.filebeat_yml_path = os.path.join(self.base_filepath_for_logs, 'tmp', 'filebeat.yaml')

        # where we will extract the tarball to (temporarily)
        self.extract_dest_path = f"{self.base_filepath_for_logs}/tmp"

        # relative path from parent dir (the root of the tarball) to the nodes
        self.path_to_nodes_dir = "nodes"

        # how to get from the nodes dir to our logs. Hopefully there's only one per node...

        ##################
        # other options
        ##################
        if kwargs.get("debug_mode", False):
            # does things such as setting filebeat.yml so we don't output to ES, but to console instead
            self.debug_mode = True

        if kwargs.get("clean_out_filebeat_first", False):
            self.clean_out_filebeat_first = True


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

            for key, log_type_def in self.log_type_definitions.items():
                if log_type_def.get("path_to_logs", None) is None:
                    # we're not supporting yet
                    continue

                # for now, just assume all are cassandra logs (which is probably wrong)
                log_type = key

                # move the files for this node and log_type
                self.position_log_files_for_node(logs_dir, hostname, log_type)

    # NOTE not using currently. Only if we want all files everywhere. Currently we're just targeting the /logs dir
    def position_log_files_for_node(self, hostname, log_type_def, **kwargs):
        """
        For a directory that contains logs for a single node and a single log_type_def of that node:
        put to each individual log files that were extracted from the tarball into the place they should go
        IF DOING TARGETTED (default)
        - just goes into <node_hostname>/logs/cassandra (or whatever our self.path_to_cassandra_logs is) and grabs those logs


        IF DOING RECURSIVELY (pass in recursive=True)
        - recursively loops through directories, starting with where files were extracted into.
        - if they are in a subdirectory, the subdirectories will be flattened out so all files will be in same directory: <self.base_filepath_for_logs>/<hostname>/<log_type>
        - At the end, since we're not moving the whole directory over but each file, there will be one dir only, tmp/, and all the *.log or gc.log.* files in there.
        - For first loop, source_dir will be the node's root dir. After that, it will be each subdirectory recursively
        - NOTE make sure logs don't overwrite each other if they have the same name, but from different dir!
        """
        # now we want to move them from original_dir to where filebeat will find them

        # all the files in the tmp directory we just made will be moved from source to dest
        source_dir = os.path.join(nodes_dir, log_type_def["path_to_logs_source"].replace("<hostname>", hostname))
        dest_dir_path = os.path.join(self.base_filepath_for_logs, log_type_def["path_to_logs_dest"])
        source_dir = os.path.join(nodes_dir, log_type_def["path_to_logs_source"].replace("<hostname>", hostname))

        all_files = os.listdir(source_dir)

        for filename in all_files:
            # filename should be str, e.g., `gc.log.0.current` 

            # filter out filenames that don't match our regex
            #
            source_path = os.path.join(source_dir, filename)

            # make sure the directory exists
            Path(dest_dir_path).mkdir(parents=True, exist_ok=True)

            # if specify the filename, then will overwrite what's there, which is what we want for idempotency
            dest_path = os.path.join(dest_dir_path, filename)

            # move it
            shutil.move(source_path, dest_path)

    def generate_filebeat_yml(self, **kwargs):
        """
        generates a filebeat.yml file for this tarball's logs
        - sets the filename on this IngestTarball instance
        - converts our base yml file to dict, then adds fields, then converts back.
        - That way, we have something that's easy to test and query against (a dict) in the middle
        - Also allows us to maintain a single yml template that matches what filebeat.ymls normally look like (filebeat.template.yml) as our starting point

        Options:
        - debug_mode : Boolean. If True, won't output to es, will output to console
        """
        template_path = os.path.join(dir_path, "config-templates/filebeat.template.yml")

        template_yaml_as_dict = None
        with open(template_path, 'r') as stream:
            try:
                # convert to dict
                # no need to load, so just safe_load
                template_yaml_as_dict = yaml.safe_load(stream)

            except yaml.YAMLError as e:
                print(e)
                raise e

        # add the paths to the dict
        filebeat_inputs = template_yaml_as_dict["filebeat.inputs"]

        # iterate over the input definitions we have in our filebeat.template.yml
        # eventually we could build the whle filebeat_input in here and not rely on the template so much, but not doing that yet
        for fb_input in filebeat_inputs:
            # add one path per hostname
            if fb_input["paths"] is None:
                fb_input["paths"] = []

            for hostname in self.hostnames:
                print("one is", hostname)
                # iterate over our log_type_definitions, and set all the paths we need into our yml
                for key, log_type_def in self.log_type_definitions.items():
                    if fb_input["tags"] == log_type_def["tags"]:
                        # then this is the right log_type_def, so let's use it

                        fb_input["paths"].append(
                            log_type_def["log_regex"].replace("<self.base_filepath_for_logs>", self.base_filepath_for_logs).replace("<hostname>", hostname)
                        )
                    else:
                        print(fb_input["tags"], "is not the same as", log_type_def["tags"])

        if self.debug_mode:
            # won't output to es, will output to console
            del template_yaml_as_dict['output.logstash']
            template_yaml_as_dict["output.console.pretty"] = True

        # set appropriate amount of leading paths for tokenizing the log.file.path
        fb_processors = template_yaml_as_dict["processors"]
        for fb_processor in fb_processors:
            if fb_processor.get("dissect", False) and fb_processor["dissect"]["field"] == "log.file.path":
                # replace 
                fb_processor["dissect"]["tokenizer"] = fb_processor["dissect"]["tokenizer"].replace("<path_for_client>", self.path_for_client)



        # remove old filebeat.yml. Can't just overwrite, since we removed write permissions
        print("removing old filebeat yml if exists")
        os.remove(self.filebeat_yml_path)

        with open(self.filebeat_yml_path, 'w', encoding='utf8') as outfile:
            # currently putting all the logs from a single host into a single dir. Helps namespace these filebeat ymls. Might be better somewhere else though

            try:
                # convert back to yml, and save as a file
                print("writing to", self.filebeat_yml_path)
                yaml.dump(template_yaml_as_dict, outfile, default_flow_style=False)

                # change permissions, or else we get error:
                # "Exiting: error loading config file: config file <filebeat.yml path> can only be writable by the owner but the permissions are "-rw-rw-r--" (to fix the permissions use: 'chmod go-w <filebeat.yml path>)"
                # this is equivalent of chmod go-w
                chmod_cmd = f'chmod go-w {self.filebeat_yml_path}'
                print(f"Running chmod command: {chmod_cmd}")
                chmod_cmd_result = subprocess.run(chmod_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if len(chmod_cmd_result.stderr) == 0:
                    print("stdout from chmod_cmd:", chmod_cmd_result.stdout)
                else:
                    print(chmod_cmd_result.stderr)
                    raise Exception(chmod_cmd_result.stderr)

                # make root the owner. https://www.elastic.co/guide/en/beats/libbeat/master/config-file-permissions.html
                chown_cmd = f'sudo chown root {self.filebeat_yml_path}'
                print(f"Running chown command: {chown_cmd}")
                chown_cmd_result = subprocess.run(chown_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if len(chown_cmd_result.stderr) == 0:
                    print("stdout from chown_cmd:", chown_cmd_result.stdout)
                else:
                    print(chown_cmd_result.stderr)
                    raise Exception(chown_cmd_result.stderr)


            except yaml.YAMLError as e:
                print(e)
                raise e

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

            start_filebeat_cmd = f'sudo filebeat -e -d "*" --c {self.filebeat_yml_path}'
            # same thing, but more conservative logging
            # start_filebeat_cmd = f'sudo filebeat -e --c {self.filebeat_yml_path}'

            print(f"Running filebeat command: {start_filebeat_cmd}")

            # TODO error handle this
            os.system(start_filebeat_cmd)


    def archive_tarball(self):
        """
        TODO
        Having extracted and positioned log files to where they need to go, and ran filebeat, we now archive the tarball so we don't run this again on this tarball. 
        Unless we want to of course, so don't delete it. Archive it.
        """
        pass

    def cleanup(self, successful):
        """
        Does whatever needs to be done after the job is successful, or after the job failed for that matter
        for now archiving tarball, but in the future maybe not
        - the individual log files can be left where they were, since unless filebeat is reset, it shouldn't run on those files again 
        - though it might be worth revisiting this; maybe change this and delete these later, especially if client doesn't want us to keep anything. But that would probably be done by another job, after all analysis is completed
        """
        if successful:
            self.archive_tarball()
        else:
            # this is it for now
            print("failed to ingest tarball")

    ###################################################
    # do it all
    ###################################################
    def run(self):
        successful = False
        try:
            print("=== Extracting tarball ===")
            self.extract_tarball()
            print("=== Positioning Log files ===")
            self.position_log_files()
            print("=== Generating filebeat yml ===")
            self.generate_filebeat_yml()
            print("=== Clearing Filebeat data (?) ===")
            self.clear_filebeat_indices_and_registry()
            print("=== Running Filebeat ===")
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
    parser.add_argument('tarball_filename', type=str, help='name of tarball file')
    parser.add_argument('client_name', type=str, help='name of client')
    parser.add_argument('--clean-out-filebeat-first', dest='clean_out_filebeat_first', action='store_true')
    parser.set_defaults(clean_out_filebeat_first=False)
    parser.add_argument('--debug-mode', dest='debug_mode', action='store_true')
    parser.set_defaults(debug_mode=False)

    args = parser.parse_args()

    options = {
        "clean_out_filebeat_first": args.clean_out_filebeat_first,
        "debug_mode": args.debug_mode,
    }

    ingestTarball = IngestTarball(args.tarball_filename, args.client_name, **options)
    ingestTarball.run()
