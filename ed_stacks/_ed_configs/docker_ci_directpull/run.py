class Main(InstructionWrapper):

    def __init__(self,instructargs):

        InstructionWrapper.__init__(self,instructargs)

        #Required
        required_keys = [ "DOCKER_USERNAME",
                          "DOCKER_REPO_TYPE",
                          "DOCKER_REPO_NAME",
                          "DOCKER_ENV_CRED",
                          "git_url",
                          "repo_key_group",
                          "repo_key_loc"
                          ]

        for required_key in required_keys: self.parse.add_required(key=required_key)

        self.parse.add_required(key="DOCKER_REGISTRY",default="docker.io")
        self.parse.add_required(key="DOCKER_REPO_TYPE",default="public")
        self.parse.add_required(key="repo_branch",default="dev")
        self.parse.add_required(key="config_env",default="private")
        self.parse.add_required(key="ELASTICDEV_CONFIG_GROUP_BUILD")

        self.parse.add_optional(key="ELASTICDEV_CONFIG_GROUP_SCRIPTS")
        self.parse.add_optional(key="ELASTICDEV_ACCESS_GROUP")
        self.parse.add_optional(key="INIT")
        self.parse.add_optional(key="PRE_SCRIPTS")
        self.parse.add_optional(key="POST_SCRIPTS")
        self.parse.add_optional(key="commit_hash")
        self.parse.add_optional(key="commit_info")

    def run_updatecode(self):

        self.set_class_vars()

        default_values = {}
        default_values["commit_info"] = self.commit_info
        instruction_name = "elasticdev:::ed_core::run_commit_info"
        inputargs = {"name":instruction_name,
                     "default_values":default_values}
        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Publish commit_info'
        inputargs["display_hash"] = self.instructions.get_hash_object(inputargs)

        return self.instructions.add_instruction(**inputargs)

    def set_chk_registerdocker_attr(self):

        #Docker Image Name and Repo
        self.DOCKER_REPO = "{}/{}/{}".format(self.DOCKER_REGISTRY,self.DOCKER_USERNAME,self.DOCKER_REPO_NAME)
        self.image_tag = self.instructions.get_random_string()
        self.DOCKER_IMAGE = "{}:{}".format(self.DOCKER_REPO,self.image_tag)

    def run_registerdocker(self):

        self.parse.add_required(key="DOCKER_FILE_BUILD",default="Dockefile")
        self.parse.add_required(key="docker_host")
        self.parse.add_required(key="repo_url")

        self.parse.add_optional(key="DOCKER_BUILD_NAME")
        self.parse.add_optional(key="DOCKER_ENV_FILE")
        self.parse.add_optional(key="ssh_port")
        self.parse.add_optional(key="http_port")

        ###############################################
        # Set Class Variables
        ###############################################
        self.set_class_vars()

        # This sets the commit info need to register the image
        # we don't put this in the parsing arguments requested 
        # since it is retrieved from the "run"
        self.set_commit_info()
        self.set_chk_registerdocker_attr()

        default_values = {}
        default_values["DOCKER_ENV_CRED"] = self.DOCKER_ENV_CRED
        default_values["DOCKER_REPO"] = self.DOCKER_REPO
        default_values["DOCKER_IMAGE"] = self.DOCKER_IMAGE
        default_values["DOCKER_IMAGE_NAME"] = self.image_tag
        default_values["repo_key_group"] = self.repo_key_group
        default_values["tag"] = self.image_tag
        default_values["config_env"] = self.config_env
        default_values["branch"] = self.repo_branch
        default_values["repo_url"] = self.repo_url
        default_values["repo_key_loc"] = self.repo_key_loc
        default_values["commit_hash"] = self.commit_hash
        if hasattr(self,"commit_info"): default_values["commit_info"] = self.commit_info
        if hasattr(self,"INIT"): default_values["INIT"] = self.INIT
        if hasattr(self,"PRE_SCRIPTS"): default_values["PRE_SCRIPTS"] = self.PRE_SCRIPTS
        if hasattr(self,"POST_SCRIPTS"): default_values["POST_SCRIPTS"] = self.POST_SCRIPTS

        #############################
        # do we need to overide here?
        #############################
        overide_values = {}
        overide_values["docker_host"] = self.docker_host
        overide_values["DOCKER_FILE"] = self.DOCKER_FILE_BUILD
        overide_values["CustomConfigGroups"] = "local:::private::{}".format(self.ELASTICDEV_CONFIG_GROUP_BUILD)
        if hasattr(self,'ELASTICDEV_ACCESS_GROUP'): overide_values["CustomConfigGroups"] = "{} local:::private::{}".format(overide_values["CustomConfigGroups"],
                                                                                                                           self.ELASTICDEV_ACCESS_GROUP)

        if hasattr(self,'ELASTICDEV_CONFIG_GROUP_SCRIPTS'): overide_values["CustomConfigGroups"] = "{} local:::private::{}".format(overide_values["CustomConfigGroups"],
                                                                                                                                   self.ELASTICDEV_CONFIG_GROUP_SCRIPTS)

        instruction_name = "elasticdev:::docker::docker_helper_ci_ec2_directpull"

        inputargs = {"name":instruction_name,
                     "default_values":default_values,
                     "overide_values":overide_values}

        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Building docker container for commit_hash "{}"'.format(self.commit_hash)
        inputargs["display_hash"] = self.instructions.get_hash_object(inputargs)

        self.instructions.add_instruction(**inputargs)
        ##############################################

    def run(self):
    
        self.instructions.unset_parallel()
        ##############################################
        self.instructions.add_job("registerdocker",instance_name="auto")
        #####################################
        self.instructions.add_job("updatecode",instance_name="auto")
        ##############################################
        ###Evaluating Jobs and loads
        ##############################################
        for run_job in self.instructions.get_jobs(): eval(run_job)

        return self.instructions.get_results(self.instructions.instructargs.get("destroy_instance"))

    def schedule(self):

        sched = self.instructions.new_schedule()
        sched.job = "updatecode"
        sched.archive.timeout = 300
        sched.archive.timewait = 60
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.conditions.retries = 1
        sched.conditions.frequency = "wait_last_run 20"
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Insert commit info into run"
        sched.trigger = [ "registerdocker 2" ]
        self.instructions.add_sched(sched)

        sched = self.instructions.new_schedule()
        sched.job = "registerdocker"
        sched.archive.timeout = 2700
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.conditions.frequency = "wait_last_run 60"
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Building docker container with code"
        self.instructions.add_sched(sched)
        
        #The order of delete instances
        delete_instsuffix = [ "updatecode", "registerdocker" ]
        self.instructions.schedule_on_delete(parallel=delete_instsuffix)

        return self.instructions.schedules

        #self.parse.add_optional(key="repo_url")
        #self.parse.add_optional(key="docker_host")
        #self.parse.add_optional(key="DOCKER_FILE_DIR")
        #self.parse.add_optional(key="DOCKER_FILD_FOLDER")

        #self.parse.add_optional(key="DOCKER_TEMPLATE_FILE")
        #self.parse.add_optional(key="DOCKER_TEMPLATE_FOLDER")
        #self.parse.add_optional(key="DOCKER_TEMPLATE_REPLACEMENTS")
        #self.parse.add_optional(key="DOCKER_BASE_IMAGE")
        #self.parse.add_optional(key="DOCKER_RUN_COMMANDS")
        #self.parse.add_optional(key="DOCKER_ENTRYPOINT")
        #self.parse.add_optional(key="DOCKER_CMD")
