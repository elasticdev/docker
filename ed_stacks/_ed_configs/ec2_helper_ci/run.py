def _get_register_variables(tag,instructargs):

    DOCKER_IMAGE = instructargs.get("DOCKER_IMAGE")
    #####################################
    if not DOCKER_IMAGE:
        DOCKER_IMAGE_NAME = instructargs.get("DOCKER_IMAGE_NAME",tag)
        DOCKER_REPO = instructargs["DOCKER_REPO"].rstrip().lstrip()
        DOCKER_IMAGE = "{}:{}".format(DOCKER_REPO,DOCKER_IMAGE_NAME)
    else:
        docker_elements = DOCKER_IMAGE.split(":")
        DOCKER_REPO = docker_elements[0]
        DOCKER_IMAGE_NAME = docker_elements[1]

    return DOCKER_REPO,DOCKER_IMAGE,DOCKER_IMAGE_NAME

def run(instructargs):

    # ShortStack that collapses these stacks
    # ContinousDelivery/Helpers/Ubuntu/Ec2/Register/DirectPull/docker_guest
    # ContinousDelivery/Helpers/Ubuntu/Ec2/Docker/Params/DockerGuest/DirectPull/build

    import json

    #####################################
    instructions = newStack(instructargs)
    #####################################
    run_only = instructargs.get("run_only")

    if not run_only: 
        build_groups = "elasticdev:::docker::create_docker elasticdev:::docker::push_container"
    else:
        build_groups = "elasticdev:::docker::run_cmd"

    commit_hash = instructargs["commit_hash"]
    repo_url = instructargs["repo_url"]

    commit_info = instructargs["commit_info"]

    if not isinstance(commit_info,dict): 
        commit_info = instructargs["commit_info"] = json.loads(commit_info)

    if isinstance(commit_info,unicode) or isinstance(commit_info,str): 
        commit_info = instructargs["commit_info"] = eval(commit_info)

    if not isinstance(commit_info,dict):
        msg = "base_default_values is not a dictionary. It is {}".format(type(commit_info))
        instructions.logger.error(msg)
        instructions.ehandle.NeedRtInput(message=msg)

    config_env = instructargs.get("config_env","private")
    DOCKER_FILE_DIR = instructargs.get("DOCKER_FILE_DIR","/opt")

    cleanup_groups = 'elasticdev:::docker::cleanup_build'
    repo_key_group = instructargs["repo_key_group"]
    CustomConfigGroups = instructargs["CustomConfigGroups"]
    repo_key_loc = instructargs["repo_key_loc"]
    docker_host = instructargs["docker_host"]
    append_groups = instructargs.get("append_groups")
    sched_name = instructargs["sched_name"]
    docker_guest = instructargs.get("docker_guest","{}-{}".format(instructions.cluster,sched_name))

    DOCKER_ENV_FILE = instructargs.get("DOCKER_ENV_FILE")
    PRE_SCRIPTS = instructargs.get("PRE_SCRIPTS")
    POST_SCRIPTS = instructargs.get("POST_SCRIPTS")
    DOCKER_CMD_SCRIPT = instructargs.get("DOCKER_CMD_SCRIPT")
    INIT = instructargs.get("init")
    repo_branch = instructargs.get("repo_branch")

    DOCKER_ENV_CRED = instructargs.get("DOCKER_ENV_CRED")

    # The base environment variables used to build the docker container
    base_env = instructargs.get("base_env","elasticdev:::docker::build")

    # if you provide the DOCKER_BUILD_NAME, we either set it to None or some other value. 
    # if not provided, then we set it to tag
    DOCKER_BUILD_NAME = instructargs.get("DOCKER_BUILD_NAME")
    DOCKER_BUILD_DIR="/var/tmp/docker/build"
    TARBALL_DIR="/usr/src/tarballs"
    if not DOCKER_ENV_FILE: DOCKER_ENV_FILE="{}/.env".format(DOCKER_BUILD_DIR)
    ######################################################
    if not sched_name or sched_name == "None":
        msg = "sched_name cannot be None"
        instructions.ehandle.NeedMoreInfo(message=msg)
    ######################################################
    #We can't add set_parallel before an order is provided
    cmd = "sleep {0}".format(1)
    instructions.add_external_cmd(cmd=cmd,
                                  order_type="sleep::shellout",
                                  role="external/cli/execute")
    ######################################################
    instructions.set_parallel()
    ######################################################
    required_keys = []
    required_keys.append("DOCKER_ENV_CRED")
    required_keys.append("docker_host")
    required_keys.append("CustomConfigGroups")
    required_keys.append("commit_info")
    required_keys.append("commit_hash")
    required_keys.append("repo_key_group")
    required_keys.append("repo_url")

    default_values = {}
    default_values["build_groups"] = build_groups

    optional_keys = []
    optional_keys.append("DOCKER_BUILD_NAME")
    optional_keys.append("ssh_port")
    optional_keys.append("http_port")
    optional_keys.append("PRE_SCRIPTS")
    optional_keys.append("POST_SCRIPTS")
    optional_keys.append("DOCKER_CMD_SCRIPT")
    optional_keys.append("init")
    optional_keys.append("repo_key_loc")

    tag = instructargs.get("tag",instructions.get_random_string())

    ######################################################
    #If not run_only, we are registering the image
    ######################################################
    pipeline_env_var = {}
    if not run_only:
        DOCKER_REPO,DOCKER_IMAGE,DOCKER_IMAGE_NAME = _get_register_variables(tag,instructargs)
        default_values["tag"] = tag
        default_values["DOCKER_IMAGE"] = DOCKER_IMAGE
        pipeline_env_var["DOCKER_IMAGE"] = DOCKER_IMAGE
        pipeline_env_var["DOCKER_IMAGE_NAME"] = DOCKER_IMAGE_NAME
        pipeline_env_var["DOCKER_IMAGE_TAG"] = tag
        pipeline_env_var["image_tag"] = tag
        instructions.add_pipeline_metadata(pipeline_env_var,publish=True)
        ######################################################
        instructions.add_pipeline_metadata({"docker":{"name":tag}})
        ######################################################
        instructargs["DOCKER_REPO"] = DOCKER_REPO
        instructions.add_pipeline_metadata({"DOCKER_IMAGE":DOCKER_IMAGE},mkey="deploy",env_var=True)
    ######################################################

    keys2pass = []
    keys2pass.append("DOCKER_ENV_FILE")
    keys2pass.append("DOCKER_FILE")
    keys2pass.append("DOCKER_BUILD_NAME")
    instructions.add_dict2dict(keys2pass,pipeline_env_var,instructargs)
    pipeline_env_var["DOCKER_FILE_DIR"] = DOCKER_FILE_DIR
    instructions.add_pipeline_metadata(pipeline_env_var,env_var=True)
    ######################################################
    docker_guest_info = instructions.check_resource(name=docker_guest,
                                                    resource_type="server")
    ######################################################
    if not docker_guest_info:

        ######################################################
        instructions.unset_parallel()
        ######################################################
        overide_values = {}
        overide_values["docker_guest"] = docker_guest
  
        default_values = {}
        default_values["docker_host"] = docker_host
        default_values["auto_ssh_port"] = True
        default_values["publish2pipeline"] = True
        if CustomConfigGroups: default_values["add_groups"] = CustomConfigGroups

        optional_keys = []
        optional_keys.append("ssh_port")
        optional_keys.append("http_port")

        instruction_name = "elasticdev:::ed_core::getlock_host"
        inputargs = {"name":instruction_name,
                     "overide_values":overide_values,
                     "optional_key":optional_keys,
                     "default_values":default_values}
        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Creating Docker Guest on docker_host "{}"'.format(docker_host)
        inputargs["display_hash"] = instructions.get_hash_object(inputargs)
        instructions.add_instruction(**inputargs)
        ######################################################
        instructions.wait_all_instance(**{ "queue_host":"instance","max_wt":"self"})
        ######################################################
        instructions.set_parallel()
        ######################################################
    else:
        overide_values = {}
        overide_values["hostname"] = docker_guest
        overide_values["add_env_var"] = True
        instruction_name = "elasticdev:::ed_core::publish_info"
        inputargs = {"name":instruction_name,
                     "overide_values":overide_values}
        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Publish info for dock_guest"{}"'.format(docker_guest)
        inputargs["display_hash"] = instructions.get_hash_object(inputargs)
        instructions.add_instruction(**inputargs)
        ######################################################
    env_ref = "{} hostname:{}".format(base_env,docker_guest)
    if DOCKER_ENV_CRED: env_ref = env_ref+" "+DOCKER_ENV_CRED

    cvar_name = tag
    if DOCKER_BUILD_NAME: cvar_name = DOCKER_BUILD_NAME

    input_args = {}
    input_args["type"] = "env"
    input_args["env_ref"] = env_ref
    input_args["name"] = cvar_name

    #DESTDIR for untaring files
    input_args["contents"] = {"DOCKER_BUILD_DIR":DOCKER_BUILD_DIR,
                              "DESTDIR":DOCKER_BUILD_DIR,
                              "TARBALL_DIR":TARBALL_DIR,
                              "DOCKER_ENV_FILE":DOCKER_ENV_FILE}

    docker_host_info = instructions.check_resource(name=docker_host,
                                                   resource_type="server",
                                                   must_exists=True)[0]

    input_args["contents"]["DOCKERHOST_PUBLIC_IP"] = docker_host_info["public_ip"]
    input_args["contents"]["DOCKERHOST_PRIVATE_IP"] = docker_host_info["private_ip"]

    ######################################################
    #If not run_only, we are registering the image
    ######################################################
    if not run_only: input_args["contents"]["DOCKER_IMAGE"] = DOCKER_IMAGE

    input_args["tags"] = "docker container ci build register {} {}".format(cvar_name,docker_host)
    input_args["track"] = instructargs.get("track",True)

    # We add EnvVars for the Run only
    pipeline_env_var = {}
    pipeline_env_var["COMMIT_HASH"] = commit_hash
    if repo_key_loc: pipeline_env_var["REPO_KEY_LOC"] = repo_key_loc
    if repo_branch: pipeline_env_var["REPO_BRANCH"] = repo_branch
    if PRE_SCRIPTS: pipeline_env_var["PRE_SCRIPTS"] = PRE_SCRIPTS
    if POST_SCRIPTS: pipeline_env_var["POST_SCRIPTS"] = POST_SCRIPTS
    if DOCKER_CMD_SCRIPT: pipeline_env_var["DOCKER_CMD_SCRIPT"] = DOCKER_CMD_SCRIPT
    if repo_url: pipeline_env_var["REPO_URL"] = repo_url
    if repo_branch: pipeline_env_var["REPO_BRANCH"] = repo_branch
    if INIT: pipeline_env_var["INIT"] = INIT
    if pipeline_env_var: instructions.add_pipeline_metadata(pipeline_env_var,env_var_run=True)
    ######################################################
    if commit_info:
        default_values = {}
        default_values["commit_info"] = commit_info
        instruction_name = "elasticdev:::ed_core::run_commit_info"
        inputargs = {"name":instruction_name,
                     "default_values":default_values}
        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Publish commit_info'
        inputargs["display_hash"] = instructions.get_hash_object(inputargs)
        instructions.add_instruction(**inputargs)
    ######################################################
    instructions.wait_all_instance(**{ "queue_host":"instance","max_wt":"self"})
    ######################################################
    instructions.unset_parallel()
    ######################################################
    instructions.add_cluster_envs(**input_args)
    groups = '{} local:::private::{} {}'.format(cleanup_groups,repo_key_group,build_groups)
    if append_groups: groups = "{} {}".format(groups,append_groups)
    cvar_entry_env='name:{}'.format(cvar_name)
    instructions.associate_cluster_env(groups=groups,entry=cvar_entry_env)
    instructions.add_group_orders(groups,hostname=docker_guest,unassign=True)
    ######################################################
    instructions.wait_hosts_tag(hostname=docker_guest)
    ######################################################
    #If not run_only, we are registering the image
    ######################################################
    if not run_only: 
        pargs = "image register"
        order_type = "register-docker::api"
        role = "image/register"

        keys2pass = [ "author",
                      "message",
                      "commit_hash",
                      "event_type",
                      "authored_date",
                      "repo_url" ]

        image_metadata = instructions.add_dict2dict(keys2pass,{},commit_info)

        commit_url = commit_info.get("url")
        if commit_url: image_metadata["commit_url"] = commit_url

        compare_url = commit_info.get("compare")
        if compare_url: image_metadata["compare_url"] = compare_url

        repo_branch = commit_info.get("branch")
        if repo_branch: image_metadata["repo_branch"] = repo_branch

        # Parse commit_info
        default_values = {}
        default_values["itype"] = "docker"
        default_values["name"] = DOCKER_IMAGE_NAME
        default_values["image"] = DOCKER_IMAGE
        default_values["repo_url"] = repo_url
        default_values["config_env"] = config_env
        default_values["commit_hash"] = commit_hash
        default_values["image_metadata"] = image_metadata
        default_values["cluster"] = instructions.cluster
        if repo_branch: default_values["branch"] = repo_branch

        keys2pass = ["schedule_id", "job_id", "run_id", "job_instance_id"]
        instructions.add_dict2dict(keys2pass,default_values,instructargs)

        human_description = "Registers docker image"
        long_description = "Records the docker image with repo_url = {}, branch = {}, commit_hash = {} to Jiffy DB".format(repo_url,repo_branch,commit_hash)

        instructions.add_jiffy_cli(pargs=pargs,
                                   order_type=order_type,
                                   human_description=human_description,
                                   long_description=long_description,
                                   display=None,
                                   role=role,
                                   default_values=default_values)
        ##############################################
    return instructions.get_results(instructargs.get("destroy_instance"))

def example():

    print '''
    '''
