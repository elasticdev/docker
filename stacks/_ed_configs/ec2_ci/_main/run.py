class Main(newSchedStack):

    def __init__(self,stackargs):

        newSchedStack.__init__(self,stackargs)

        self.parse.add_required(key="repo_branch",default="dev")
        self.parse.add_required(key="repo_key_group")
        self.parse.add_required(key="repo_key_loc")
        self.parse.add_required(key="git_url")

        self.parse.add_required(key="dockerfile",default="Dockefile")
        self.parse.add_required(key="docker_repo")
        self.parse.add_required(key="docker_repo_type",default="private")
        self.parse.add_required(key="docker_tag_method",default="commit_hash")

        self.parse.add_required(key="commit_info")
        self.parse.add_required(key="config_env",default="private")

        self.stack.add_substack("elasticdev:::ed_core::run_commit_info")
        self.stack.add_substack("elasticdev:::docker::ec2_helper_ci")

        self.stack.init_substacks()

    def run_updatecode(self):

        self.init_variables()

        inputargs = {}
        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Publish commit_info'
        inputargs["default_values"] = {"commit_info":self.commit_info}
        return self.stack.run_commit_info.insert(display=True,**inputargs)

    def set_chk_registerdocker_attr(self):

        # Docker Image Name and Repo
        if self.docker_tag_method == "commit_hash":
            self.image_tag = self.commit_info["commit_hash"]
        else:
            self.image_tag = self.stack.get_random_string()

        self.docker_image = "{}:{}".format(self.docker_repo,self.image_tag)

    def run_registerdocker(self):

        self.parse.add_required(key="docker_host")

        self.parse.add_required(key="repo_url")
        self.init_variables()

        # This sets the commit info need to register the image
        # we don't put this in the parsing arguments requested 
        # since it is retrieved from the "run"
        self.set_commit_info()
        self.set_chk_registerdocker_attr()

        default_values = {}
        default_values["docker_repo"] = stack.docker_repo
        default_values["docker_image"] = stack.docker_image
        default_values["repo_key_group"] = stack.repo_key_group
        default_values["tag"] = stack.image_tag
        default_values["config_env"] = stack.config_env
        default_values["branch"] = stack.repo_branch
        default_values["repo_url"] = stack.repo_url
        default_values["repo_key_loc"] = stack.repo_key_loc
        default_values["commit_hash"] = stack.commit_hash
        if hasattr(self,"commit_info"): default_values["commit_info"] = stack.commit_info

        # do we need to overide here?
        overide_values = {}
        overide_values["docker_host"] = stack.docker_host
        overide_values["DOCKER_FILE"] = stack.DOCKER_FILE_BUILD

        inputargs = {"default_values":default_values,
                     "overide_values":overide_values}

        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Building docker container for commit_hash "{}"'.format(stack.commit_hash)

        return self.stack.ec2_helper_ci.insert(display=True,**inputargs)

    def run(self):
    
        self.stack.unset_parallel()
        ##############################################
        self.stack.add_job("registerdocker",instance_name="auto")
        #####################################
        self.stack.add_job("updatecode",instance_name="auto")
        ##############################################
        ###Evaluating Jobs and loads
        ##############################################
        for run_job in self.stack.get_jobs(): eval(run_job)

        return self.stack.get_results(self.stack.stackargs.get("destroy_instance"))

    def schedule(self):

        sched = self.stack.new_schedule()
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
        self.stack.add_sched(sched)

        sched = self.stack.new_schedule()
        sched.job = "registerdocker"
        sched.archive.timeout = 2700
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.conditions.frequency = "wait_last_run 60"
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Building docker container with code"
        self.stack.add_sched(sched)
        
        #The order of delete instances
        delete_instsuffix = [ "updatecode", "registerdocker" ]
        self.stack.schedule_on_delete(parallel=delete_instsuffix)

        return self.stack.schedules

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
