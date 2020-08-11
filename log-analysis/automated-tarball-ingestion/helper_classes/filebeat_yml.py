import os
from copy import deepcopy
import yaml
import subprocess

class FilebeatYML:
    template_yaml_as_dict = None
    hostnames = []

    """
    base dict for filebeat.inputs in our yml
    for now all have the same for all these. If they don't we'll have to add more to our log_type_definitions dict above and then set using those
    """
    filebeat_input_template = {
        "enabled": "true",
        "exclude_files": ["\.zip$"],
        "multiline.match": "after",
        "multiline.negate": "true",
        "multiline.pattern": "^TRACE|DEBUG|WARN|INFO|ERROR",
        "type": "log",
        "paths": [],
    }

    """
    all metadata related to a given log
    - main key:      (e.g., cassandra.main) is arbitrarily chosen for use in this script. Will be referred to generally using var `log_type` in this script.
    - tags:          what we want tagged in filebeat.template.yml filebeat.inputs field to identify these logs
    - path_to_logs_source:  path from base path for this tarball to the direct parent directory that holds these logs (if there are logs nested within subdirectories, make a new log_type_definitions key for those). Will replace all names within <> dynamically.
    - path_to_logs_dest:  path to where we want these so filebeat can find them
    - log_regex:     regex to use to find all these logs that we want from that parent directory

    To not do a certain kind of log, just put None in the path_to_logs_source and we'll skip it. Or comment the whole thing out of course.

    ADDING A NEW LOG TYPE
    - add a definition here with all the keys
    - add the fields in filebeat.template.yml as well
    """

    # TODO maybe this best lives in separate file as a constant, unless we manipulate it 
    log_type_definitions = {
        "cassandra.main": {
            "path_to_logs_source": "<hostname>/logs/cassandra",
            "path_to_logs_dest": "<hostname>/cassandra",
            "tags": ["cassandra","main"],
            "log_regex": "<self.base_filepath_for_logs>/<hostname>/cassandra/system.log*",
        },
        "system": {
            # NOTE: This is for a finding system logs, not cassandra logs
            "path_to_logs_source": None, # TODO set this when we have a path
            "tags": ["system","messages"],
            "log_regex": "<self.base_filepath_for_logs>/<hostname>/system/*.test",
        },
        "spark.master": {
            "path_to_logs_source": "<hostname>/logs/spark/master",
            "path_to_logs_dest": "<hostname>/spark/master",
            "tags": ["spark","master"],
            "log_regex": "<self.base_filepath_for_logs>/<hostname>/spark/master/master.*",
            # at the path_to_logs_source at least some are zipped
            "zipped": True,
            "zip_format": "zip", # ie not tar.gz
        },
        "spark.worker": {
            "path_to_logs_source": "<hostname>/logs/spark/worker",
            "path_to_logs_dest": "<hostname>/spark/worker",
            "tags": ["spark","worker"],
            # so far only seeing "worker.log" and only one file
            "log_regex": "<self.base_filepath_for_logs>/<hostname>/spark/worker/worker.log*",
        },
    }


    def __init__(self, project_root_path, base_filepath_for_logs, path_for_client, **kwargs):
        self.template_path = os.path.join(project_root_path, "config-templates/filebeat.template.yml")

        # does things such as setting filebeat.yml so we don't output to ES, but to console instead
        self.debug_mode = kwargs.get("debug_mode", False)

        """
        a list of configs to set on the filebeat.yml, key being key of config (potentially multiple layers deep) and value is what to set it to
        - called last, so overrides any other setting
        - use integer to set a list value
        - E.g., `[["output.elasticsearch.hostname", "127.0.0.1"], ["kibana.hostname", "123.456.789.101"], ["output.kibana.enabled", "false", ["processors.2.timestamp.ignore_failure", "false"]]`.
        """
        self.custom_config = kwargs.get("custom_config", [])

        self.base_filepath_for_logs = base_filepath_for_logs
        self.path_for_client = path_for_client

        # where the filebeat.yml will go
        self.file_path = os.path.join(self.base_filepath_for_logs, 'tmp', 'filebeat.yaml')


    ##############################
    # helpers
    ##############################
    def breakout_keys_from_yml_dict(self, base_dict):
        """
        some keys are getting returned as "part1.part2" e.g., "filebeat.inputs". 
        This is fine for yml, but hard to manipulate if we want to set something else on filebeat.
        Make it simple by parsing this out, so it's more like:
        ```
            filebeat:
              inputs: 
        ```

        easier way would be to just make sure filebeat.template.yml doesn't set keys like this. But we want the template to handle any valid yml template, so let's just handle here
        - Works recursively
        - modifies dict in place

        IF this doesn't work for whatever reason, consider this: https://stackoverflow.com/a/39464072/6952495
        """
        new_dict = {}
        #print("starts with:\n", base_dict)


        # for each item on this dict:
        for template_key, value in list(base_dict.items()):
            # target_dict is what gets set on
            # target_dict will change throughout this recursive iteration, as we dig deeper into the nested dicts. 
            target_dict = new_dict

            key_list = template_key.split(".")

            # iterate through each layer and set. Hopefully only one layer (?)
            for index, key in enumerate(key_list):

                # if there is another key after this, 
                if len(key_list) > index + 1:
                    # in yml these will only be nested with "." like this if they are dicts
                    if target_dict.get(key, None) is None:
                         target_dict[key] = {}
    
                    # print("\nnow we have:\n", new_dict)

                    target_dict = target_dict[key]

                else:
                    # we're at the end, can set the value
                    # but first, make sure value is also unnested
                    if type(value) == dict:
                        # print("+++++++++++digging into:", key, "which has value", value)
                        new_value_dict = self.breakout_keys_from_yml_dict(value)
                        target_dict[key] = new_value_dict

                    else:
                        # print("--------------", value, "is not a dict, so setting on key:", key, "on dict:", target_dict, "--------------")

                        target_dict[key] = value

        return new_dict

    ##############################
    # steps in generating template
    ##############################

    def load_template(self):
        with open(self.template_path, 'r') as stream:
            try:
                # convert to dict
                # no need to load, so just safe_load
                self.template_yaml_as_dict = yaml.safe_load(stream)

            except yaml.YAMLError as e:
                print(e)
                # for now just throwing anyways. If it doesn't generate, we don't want it to run
                raise e

        # format the dict so it's easier to use
        self.template_yaml_as_dict = self.breakout_keys_from_yml_dict(self.template_yaml_as_dict)

        #print("\nFINAL")
        #print(self.template_yaml_as_dict)

    def add_filebeat_inputs(self):
        """
        add the paths to the dict
        mutates self.template_yaml_as_dict in place
        """

        self.template_yaml_as_dict["filebeat"] = {}
        self.template_yaml_as_dict["filebeat"]["inputs"] = []
        filebeat_inputs = self.template_yaml_as_dict["filebeat"]["inputs"]

        # iterate over our log_type_definitions, and set all the paths we need into our yml
        for key, log_type_def in self.log_type_definitions.items():
            if log_type_def.get("path_to_logs_source", None) is None:
                # we're not supporting yet
                continue

            filebeat_inputs.append(deepcopy(self.filebeat_input_template))

            fb_input = filebeat_inputs[-1]
            # add tags for this log type
            fb_input["tags"] = log_type_def["tags"]

            # add one path per host
            for hostname in self.hostnames:
                print("hn", hostname)
                fb_input["paths"].append(
                    log_type_def["log_regex"].replace("<self.base_filepath_for_logs>", self.base_filepath_for_logs).replace("<hostname>", hostname)
                )

    def set_processors(self):
        """
        set appropriate amount of leading paths for tokenizing the log.file.path
        - mutates self.template_yaml_as_dict in place
        """
        fb_processors = self.template_yaml_as_dict["processors"]
        for fb_processor in fb_processors:
            if fb_processor.get("dissect", False) and fb_processor["dissect"]["field"] == "log.file.path":
                # replace 
                fb_processor["dissect"]["tokenizer"] = fb_processor["dissect"]["tokenizer"].replace("<path_for_client>", self.path_for_client)


    def handle_optional_settings(self):
        """
        handles different options that can get past and
        - note that anything else that is set will still be overridden by custom_config
        - mutates self.template_yaml_as_dict in place
        """
        if self.debug_mode:
            # won't output to es, will output to console
            del self.template_yaml_as_dict["output"]["logstash"]
            self.template_yaml_as_dict["output"]["console"]["pretty"] = True

    def apply_custom_config(self):
        """
        apply any custom_configs passed in through args
        """

        for config in self.custom_config:
            key_trail_str = config[0]
            key_list = key_trail_str.split(".")
            value = config[1]

            base = self.template_yaml_as_dict
            for index, key in enumerate(key_list):
                key_value = dict
                if len(key_list) > index + 1:
                    try:
                        int(key_list[index + 1])
                        # if no exception, it's a list index
                        key_value = list
                    except:
                        print(key, "is a key, not a list index")

                    # if key not set yet, initialize it based on what is next
                    if base.get(key, None) == None:
                        print("setting key", key, "on base", base)
                        base[key] = key_value() # e.g., will be dict() or list()
                    else:
                        print("key found", key, "on base", base)

                    # set new base and iterate over again
                    base = base[key]

                else:
                    # this is the final leaf of the chain, so set as value and we're done
                    base[key] = value
                    base = base[key]


    def remove_old_filebeat_yml(self):
        """
        remove old filebeat.yml. 
        Can't just overwrite, since we removed write permissions
        """
        print("removing old filebeat yml if exists")
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)

    def write_the_file(self):
        # make the filebeat.yml, and set necessary permissions
        with open(self.file_path, 'w', encoding='utf8') as outfile:
            # currently putting all the logs from a single host into a single dir. Helps namespace these filebeat ymls. Might be better somewhere else though

            try:
                # convert back to yml, and save as a file
                print("writing to", self.file_path)
                yaml.dump(self.template_yaml_as_dict, outfile, default_flow_style=False)

                # change permissions, or else we get error:
                # "Exiting: error loading config file: config file <filebeat.yml path> can only be writable by the owner but the permissions are "-rw-rw-r--" (to fix the permissions use: 'chmod go-w <filebeat.yml path>)"
                # this is equivalent of chmod go-w
                chmod_cmd = f'chmod go-w {self.file_path}'
                print(f"Running chmod command: {chmod_cmd}")
                chmod_cmd_result = subprocess.run(chmod_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if len(chmod_cmd_result.stderr) == 0:
                    print("stdout from chmod_cmd:", chmod_cmd_result.stdout)
                else:
                    print(chmod_cmd_result.stderr)
                    raise Exception(chmod_cmd_result.stderr)

                # make root the owner. https://www.elastic.co/guide/en/beats/libbeat/master/config-file-permissions.html
                chown_cmd = f'sudo chown root {self.file_path}'
                print(f"Running chown command: {chown_cmd}")
                chown_cmd_result = subprocess.run(chown_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if len(chown_cmd_result.stderr) == 0:
                    print("stdout from chown_cmd:", chown_cmd_result.stdout)
                else:
                    print(chown_cmd_result.stderr)
                    raise Exception(chown_cmd_result.stderr)


            except yaml.YAMLError as e:
                print(e)
                # just raising anyways for now
                raise e

    def generate(self, **kwargs):
        """
        generate a yml file for this instance of FilebeatYML
        - sets the filename on this IngestTarball instance
        - converts our base yml file to dict, then adds fields, then converts back.
        - That way, we have something that's easy to test and query against (a dict) in the middle
        - Also allows us to maintain a single yml template that matches what filebeat.ymls normally look like (filebeat.template.yml) as our starting point

        Options:
        - debug_mode : Boolean. If True, won't output to es, will output to console

        """
        self.load_template()
        self.add_filebeat_inputs()
        self.set_processors()
        self.handle_optional_settings()
        self.apply_custom_config()
        self.remove_old_filebeat_yml()
        self.write_the_file()
