class Main(newSchedStack):

    def __init__(self,stackargs):

        newSchedStack.__init__(self,stackargs)

        self.parse.add_required(key="repo_branch",default="dev")
        self.parse.add_required(key="repo_key_group")
        self.parse.add_required(key="repo_key_loc")
        self.parse.add_required(key="repo_url")

        self.parse.add_required(key="aws_default_region",default="us-east-1")
        self.parse.add_required(key="dockerfile",default="Dockerfile")
        self.parse.add_required(key="docker_repo")
        self.parse.add_required(key="docker_tag_method",default="commit_hash")
        self.parse.add_required(key="config_env",default="private")

        self.stack.add_substack("elasticdev:::ed_core::run_commit_info")
        self.stack.add_substack("elasticdev:::docker::ec2_standby_ci")

        self.stack.init_substacks()

    def run_record_commit_info(self):

        self.parse.add_optional(key="commit_info",default="null")
        self.parse.add_optional(key="commit_hash",default="null")
        self.parse.add_optional(key="init",default="null")
        self.init_variables()

        if not self.commit_info and not self.init:
            msg = "you need commit_info unless this is the first code retrieval"
            self.stack.ehandle.NeedRtInput(message=msg)

        inputargs = {"automation_phase":"continuous_delivery"}
        inputargs["human_description"] = 'Publish commit_info'
        inputargs["default_values"] = {"commit_info":self.commit_info}
        return self.stack.run_commit_info.insert(display=True,**inputargs)

    def run_registerdocker(self):

        self.parse.add_required(key="docker_host",default="null")
        self.parse.add_required(key="repo_url")
        self.init_variables()

        # Set docker host accordingly
        if not self.docker_host:
            self.docker_host = self.stackargs["docker_host"] = "{}-docker_host".format(self.stack.cluster)  

        # This sets the commit info need to register the image
        # we don't put this in the parsing arguments requested 
        # since it is retrieved from the "run"
        self.set_commit_info()

        default_values = {"docker_repo":self.docker_repo}
        default_values["repo_key_group"] = self.repo_key_group
        default_values["tag"] = self.commit_hash
        default_values["config_env"] = self.config_env
        default_values["branch"] = self.repo_branch
        default_values["repo_url"] = self.repo_url
        default_values["repo_key_loc"] = self.repo_key_loc
        default_values["commit_hash"] = self.commit_hash
        default_values["docker_repo"] = self.docker_repo
        default_values["aws_default_region"] = self.aws_default_region
        if hasattr(self,"commit_info"): default_values["commit_info"] = self.commit_info

        # do we need to overide here?
        overide_values = {"docker_host":self.docker_host}
        overide_values["dockerfile"] = self.dockerfile

        inputargs = {"default_values":default_values,
                     "overide_values":overide_values}

        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Building docker container for commit_hash "{}"'.format(self.commit_hash)

        return self.stack.ec2_standby_ci.insert(display=True,**inputargs)

    def run(self):
    
        self.stack.unset_parallel()
        self.stack.add_job("registerdocker",instance_name="auto")
        self.stack.add_job("record_commit_info",instance_name="auto")

        # Evaluating Jobs and loads
        for run_job in self.stack.get_jobs(): eval(run_job)

        return self.stack.get_results()

    def schedule(self):

        sched = self.stack.new_sched()
        sched.job = "record_commit_info"
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

        sched = self.stack.new_sched()
        sched.job = "registerdocker"
        sched.archive.timeout = 2700
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.conditions.frequency = "wait_last_run 60"
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Building docker container with code"
        self.stack.add_sched(sched)
        
        # ref 3638623542sdafhlhs
        ## delete_sched is no longer used, but will be deleted by the saas
        ## The order of delete instances
        #delete_instsuffix = [ "record_commit_info", "registerdocker" ]

        ## We don't destroy the registry when we delete the schedule
        #keep_resources = [ {"provider":"aws","resource_type":"ecr"} ]
        #destroy_resources = [ {"provider":"ec2","resource_type":"server"} ]

        #self.stack.delete_sched(parallel=delete_instsuffix,
        #                        destroy_resources=destroy_resources,
        #                        keep_resources=keep_resources)

        #                        # ref 466328850045jjfhgndygsdxw
        #                        # Add custom delete stack here for resources
        #                        # stack=stack

        return self.stack.schedules
