import argparse
import os
import shutil
import yaml
from pathlib import Path

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
        """
        # modified time will be something like 1596785608.063104 (unix timestamp)
        # since moving counts as modifying, will be when we put the tarball into the log-tarballs-to-ingest folder
        tarball_modified_time = os.path.getmtime(self.tarball_path)
        self.incident_id = tarball_modified_time

        # where we will put all the logs into
        self.base_filepath_for_logs = f"{dir_path}/logs-for-client/{self.client_name}/incident-{self.incident_id}" # /{self.hostname}/{self.log_type}"

        # where we will extract the tarball to (temporarily)
        self.extract_dest_path = f"{self.base_filepath_for_logs}/tmp"

        # relative path from parent dir (the root of the tarball) to the nodes
        self.path_to_nodes_dir = "nodes"

        # how to get from the nodes dir to our logs. Hopefully there's only one per node...
        self.path_to_logs = {
            "cassandra": "<hostname>/logs/cassandra",
            "system": None
        }

        ##################
        # other options
        ##################
        if kwargs.get("debug_mode", False):
            # does things such as setting filebeat.yml so we don't output to ES, but to console instead
            self.debug_mode = True


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

            # whether these are system logs or Cassandra logs
            for log_type in ["cassandra", "system"]:
                if self.path_to_logs.get(log_type, None) is None:
                    # this tarball doesn't have this type of logs, or we're just not getting them
                    print("no path for log_type", log_type, "...skipping.")
                    continue

                # get node's hostname from the directory name (ie the final part of the path)
                hostname = os.path.basename(os.path.normpath(dir_for_node))

                # add this hostname to list of all hostnames in tarball
                self.hostnames.append(hostname)

                # TODO add logic to detect if these are cassandra logs or system logs, and then run once per hostname/logtype permutation (ie, for each node, run position_log_files_for_node once per log_type, or multiple times for log_type if it's easier. 
                # for now, just assume all are cassandra logs (which is probably wrong)
                cassandra_logs_dir = os.path.join(nodes_dir, self.path_to_logs[log_type].replace("<hostname>", hostname))
                print("these logs are found at", cassandra_logs_dir)

                # move the files for this node and log_type
                self.position_log_files_for_node(cassandra_logs_dir, hostname, log_type)

    # NOTE not using currently. Only if we want all files everywhere. Currently we're just targeting the /logs dir
    def position_log_files_for_node(self, source_dir, hostname, log_type, **kwargs):
        """
        For a directory that contains logs for a single node and a single log_type of that node:
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
        print("getting all from", source_dir)

        # all the files in the tmp directory we just made will be moved, and 
        all_files = os.listdir(source_dir)
        for filename in all_files:
            # filename should be str, e.g., `gc.log.0.current` 
            print("filename", filename)
            source_path = os.path.join(source_dir, filename)
            if kwargs.get("recursive", False) and os.path.isdir(source_path):
                # this is a dir, so recursively loop through
                self.position_log_files(source_path)

            else:
                # moving this file to where it needs to be:
                dest_dir_path = os.path.join(self.base_filepath_for_logs, hostname, log_type)
                # make sure the directory exists
                Path(dest_dir_path).mkdir(parents=True, exist_ok=True)

                print(f"moving {source_path} to", dest_dir_path)

                # move it
                shutil.move(source_path, dest_dir_path)

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
        for fb_input in filebeat_inputs:
            # add one path per hostname
            if fb_input["paths"] is None:
                fb_input["paths"] = []

            for hostname in self.hostnames:
                print("one host", hostname)
                if "system" in fb_input["tags"]:
                    # This is for a finding system logs, not cassandra logs

                    fb_input["paths"].append(
                        f"{self.base_filepath_for_logs}/{hostname}/system/*.test"
                    )

                elif "gc" in fb_input["tags"]:
                    # this should be to find our cassandra garbage collection logs
                    fb_input["paths"].append(
                        f"{self.base_filepath_for_logs}/{hostname}/cassandra/system.log*"
                    )

                elif "main" in fb_input["tags"]:
                    # this should be to find our main cassandra logs
                    fb_input["paths"].append(
                        f"{self.base_filepath_for_logs}/{hostname}/cassandra/gc.log*"
                    )

        if self.debug_mode:
            # won't output to es, will output to console
            del template_yaml_as_dict['output.elasticsearch']
            template_yaml_as_dict["output.console.pretty"] = True

        # currently putting in with all the logs. Helps namespace these filebeat ymls. Might be better somewhere else though
        output_path = os.path.join(self.base_filepath_for_logs, 'tmp', 'filebeat.yaml')

        with open(output_path, 'w', encoding='utf8') as outfile:
            try:
                # convert back to yml, and save as a file
                print("writing to", output_path)
                yaml.dump(template_yaml_as_dict, outfile, default_flow_style=False)

            except yaml.YAMLError as e:
                print(e)
                raise e


    def run_filebeat(self):
        """
        Probably do this assuming that rest of ELK stack is already running
        """
        pass

    def archive_tarball(self):
        """
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
            self.extract_tarball()
            self.position_log_files()
            self.generate_filebeat_yml()
            self.run_filebeat()
            successful = True

        except Exception as e:
            # currently not catching
            successful = False
            raise e

        # no matter what, cleanup
        self.cleanup(successful)

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
        usage='{tarball_filename} {company_name} {system|cassandra}')
    parser.add_argument('tarball_filename', type=str, help='name of tarball file')
    parser.add_argument('client_name', type=str, help='name of client')
    args = parser.parse_args()

    ingestTarball = IngestTarball(args.tarball_filename, args.client_name)
    ingestTarball.run()

    print("Success.")
