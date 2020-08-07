import argparse
import os
import shutil
import yaml

dir_path = os.path.dirname(os.path.realpath(__file__))
tarballs_to_ingest_dir_path = f"{dir_path}/log-tarballs-to-ingest"

class IngestTarball:
    """
    Class to model a single tarball's ingestion process

    Currently only support running for a single tarball at a time
    """
    client_name = ""
    hostname = ""
    tarball_filename = ""
    logfiles = []
    debug_mode = False

    def __init__(self, tarball_filename, client_name, hostname, log_type, **kwargs):
        self.tarball_filename = tarball_filename

        # absolute path to the tar ball
        self.tarball_path = f"{tarballs_to_ingest_dir_path}/{self.tarball_filename}"

        # the name of the client (or some sort of human readable identifier for them), e.g., example-company
        self.client_name = client_name

        # original hostname where the logs were genereated. Can be domain name or ip addr. Used to identify that C* node and distinguish it from other nodes in the client's cluster
        self.hostname = hostname

        # whether these are system logs or cassandra logs
        self.log_type = log_type

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
        self.base_filepath_for_logs = f"{dir_path}/logs-for-client/{self.client_name}/incident-{self.incident_id}/{self.hostname}/{self.log_type}"

        # where we will extract the tarball to (temporarily)
        self.extract_dest_path = f"{self.base_filepath_for_logs}/tmp"

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

    def position_log_files(self, original_dir="extract_dest_path"):

        """
        put to each individual log files that were extracted from the tarball into the place they should go
        - recursively loops through directories, starting with where files were extracted into. 
        - if they are in a subdirectory, the subdirectories will be flattened out so all files will be in same directory: self.base_filepath_for_logs
        - At the end, since we're not moving the whole directory over but each file, there will be one dir only, tmp/, and all the *.log or gc.log.* files in there.
        - better than doing shutil.copytree, since this is idempotent (we could probably implement shutil.copytree to be as well, but that one requires that the dest dir didn't exist before running)
        """
        # now we want to move them from original_dir to where filebeat will find them
        if (original_dir == "extract_dest_path"):
            # starting from the top
            original_dir = self.extract_dest_path
        print("getting all from", original_dir)

        # all the files in the tmp directory we just made will be moved, and 
        all_files = os.listdir(original_dir)
        for filename in all_files:
            # filename should be str, e.g., `gc.log.0.current` 
            print("filename", filename)
            source_path = os.path.join(original_dir, filename)
            if os.path.isdir(source_path):
                # this is a dir, so recursively loop through
                self.position_log_files(source_path)

            else:
                # move this file to where it needs to be
                shutil.move(source_path, self.base_filepath_for_logs)

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

        for fb_input in filebeat_inputs:
            if "system" in fb_input["tags"]:
                # This is for a system log, not a cassandra log
                if self.log_type == "cassandra":
                    # don't set this, we are only looking at cassandra logs for this run
                    # it doesn't hurt though...but for now, let's make things explicit and raise errors when it's not right
                    continue

                fb_input["paths"] = [
                    f"{self.base_filepath_for_logs}/*.test"
                ]

            elif "gc" in fb_input["tags"]:
                # this should be our cassandra garbace collection logs
                if self.log_type == "system":
                    # don't set this, we are only looking at system logs for this run
                    continue

                fb_input["paths"] = [
                    f"{self.base_filepath_for_logs}/system.log*"
                ]

            elif "main" in fb_input["tags"]:
                # this should be our main cassandra logs
                if self.log_type == "system":
                    # don't set this, we are only looking at system logs for this run
                    continue

                fb_input["paths"] = [
                    f"{self.base_filepath_for_logs}/gc.log*"
                ]

        if self.debug_mode:
            # won't output to es, will output to console
            del template_yaml_as_dict['output.elasticsearch']
            template_yaml_as_dict["output.console.pretty"] = True

        print(template_yaml_as_dict)
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
        - the individual log files can be left where they were, since unless filebeat is reset, it shouldn't run on those files again (though it might be worth revisiting this; maybe change this and delete these later, especially if client doesn't want us to keep anything. But that would probably be done by another job, after all analysis is completed)
        """
        pass


    ###################################################
    # do it all
    ###################################################
    def run(self):
        self.extract_tarball()
        self.position_log_files()
        self.generate_filebeat_yml()
        self.run_filebeat()
        self.archive_tarball()

if __name__ == '__main__':
    """
    Instructions:
    1) Place a log tarball in `./log-tarballs-to-ingest/` (currently not automating, you have to do this manually)

    2)- Run script passing in args to provide metadata about the tarball
        Args:
            - tarball_filename: filename of our tarball
            - client_name: (make this consistent for the company, for every company there should only be one)
            - hostname - what host these logs came from. Can be a domain name or IP address, but it is best to stay consistent for that node (don't change back and forth between ip and domain name)

    Call like:
        python3 ingest_tarball.py example-logs.tar.gz my-company 123.456.789.101
    """
    parser = argparse.ArgumentParser(
        description='Converting Stats Form TXT TO CSV Format',
        usage='{tarball_filename} {company_name} {hostname} {system|cassandra}')
    parser.add_argument('tarball_filename', type=str, help='name of tarball file')
    parser.add_argument('client_name', type=str, help='name of client')
    parser.add_argument('hostname', type=str, help='ip address or domain name of host')
    parser.add_argument('log_type', type=str, help='whether these are system logs or Cassandra logs')
    args = parser.parse_args()

    ingestTarball = IngestTarball(tarball_filename, client_name, hostname, log_type)
    ingestTarball.run()

    print("Success.")
