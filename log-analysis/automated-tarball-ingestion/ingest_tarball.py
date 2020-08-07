import argparse

class IngestTarball:
    """
    Class to model a single tarball's ingestion process

    Currently only support running for a single tarball at a time
    """
    client_name = ""
    hostname = ""
    tarball_filename = ""
    logfiles = []

    def __init__(self, tarball_filename, client_name, hostname):
        self.tarball_filename = tarball_filename
        self.client_name = client_name
        self.hostname = hostname

    ###################################################
    # some getters
    ###################################################
    def get_incident_id(self):
        """
        We generate the incident time and use it as an incident_id
        - We want it to be unique for this file but ideally the same for everytime the file runs (ie idempotent)
        - Consequently we will grab metadata from the tarball itself and use as the incident_id
        """
        pass

    def get_base_filepath(self):
        pass

    ###################################################
    # the operations we run when ingesting the tarball
    ###################################################

    def load_file(self):
        pass

    def extract_tarball(self):
        """
        unzip the tar ball
        """
        pass

    def position_log_files(self):
        """
        put to each individual log files that were extracted from the tarball into the place they should go
        """
        pass

    def generate_filebeat_yml(self):
        """
        - generates a filebeat.yml file
        - sets the filename on this IngestTarball instance
        """
        pass

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
        self.load_file()
        self.extract_tarball()
        self.generate_filebeat_yml()
        self.run_filebeat()
        self.archive_tarball()

if __name__ == '__main__':
    """
    Instructions:
    1) Place a log tarball in `./log-tarballs-to-ingest/` (currently not automating, you have to do this)

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
        usage='{tarball_filename} {company_name} {hostname}')
    parser.add_argument('tarball_filename', type=str, help='name of tarball file')
    parser.add_argument('client_name', type=str, help='name of client')
    parser.add_argument('hostname', type=str, help='ip address or domain name of host')
    args = parser.parse_args()

    ingestTarball = IngestTarball(tarball_filename, client_name, hostname)
    ingestTarball.run()

    print("Success.")
