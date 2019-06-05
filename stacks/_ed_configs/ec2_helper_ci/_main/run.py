def run(stackargs):

    import json

    # initiate stack 
    stack = newStack(stackargs)

    stack.parse.add_required(key="commit_hash")
    stack.parse.add_required(key="repo_url")
    stack.parse.add_required(key="commit_info")
    stack.parse.add_required(key="repo_key_group")
    stack.parse.add_required(key="repo_key_loc")

    stack.parse.add_required(key="docker_host")

    stack.parse.add_optional(key="config_env",default="private")
    stack.parse.add_optional(key="sched_name")
    stack.parse.add_optional(key="repo_branch")

    # Add hostgroups
    stack.add_hostgroups("elasticdev:::docker::create_container elasticdev:::docker::push_container","build_groups")
    stack.add_hostgroups("elasticdev:::docker::run_cmd","build_groups_run_only")
    stack.add_hostgroups('elasticdev:::docker::cleanup_build','cleanup_build')

    # Add substacks
    stack.add_substack('elasticdev:::ed_core::getlock_host')
    stack.add_substack('elasticdev:::ed_core::publish_info')
    stack.add_substack('elasticdev:::ed_core::run_commit_info')

    # init the stack namespace
    stack.init_variables()
    stack.init_substacks()
    stack.init_hostgroups()

    # Begin ordering
    if not stack.run_only: 
        build_groups = stack.build_groups
    else:
        build_groups = stack.build_groups_run_only

    if not isinstance(stack.commit_info,dict): 
        stack.commit_info = stackargs["commit_info"] = json.loads(stack.commit_info)

    if isinstance(stack.commit_info,unicode) or isinstance(stack.commit_info,str): 
        stack.commit_info = stackargs["commit_info"] = eval(stack.commit_info)

    if not isinstance(stack.commit_info,dict):
        msg = "base_default_values is not a dictionary. It is {}".format(type(stack.commit_info))
        stack.logger.error(msg)
        stack.ehandle.NeedRtInput(message=msg)

    docker_guest = stackargs.get("docker_guest","{}-{}".format(stack.cluster,stack.sched_name))

    # The base environment variables used to build the docker container
    base_env = stackargs.get("base_env","elasticdev:::docker::build")

    TARBALL_DIR="/usr/src/tarballs"

    # sched_name must be provided
    if not stack.sched_name or stack.sched_name == "None":
        msg = "sched_name cannot be None"
        stack.ehandle.NeedMoreInfo(message=msg)

    # We can't add set_parallel before an order is provided
    cmd = "sleep {0}".format(1)
    stack.add_external_cmd(cmd=cmd,
                           order_type="sleep::shellout",
                           role="external/cli/execute")

    # Set parallel
    stack.set_parallel()

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
    optional_keys.append("repo_key_loc")

    # If not run_only, we are registering the image
    pipeline_env_var = {}

    # Add pipeline metadata
    if not stack.run_only:
        default_values["tag"] = stack.tag
        default_values["DOCKER_IMAGE"] = stack.docker_image
        pipeline_env_var["DOCKER_IMAGE"] = stack.docker_image
        pipeline_env_var["DOCKER_IMAGE_TAG"] = stack.tag
        pipeline_env_var["image_tag"] = stack.tag
        stack.add_metadata_to_run(pipeline_env_var,publish=True)
        stack.add_metadata_to_run({"docker":{"name":stack.tag}})

    # Add additional views for pipeline env var
    # that isn't published
    docker_env_file = "{}/.env".format(stack.dockerfile)
    pipeline_env_var["DOCKER_FILE"] = stack.dockerfile
    pipeline_env_var["DOCKER_ENV_FILE"] = docker_env_file
    stack.add_metadata_to_run(pipeline_env_var,env_var=True)

    # check to see if a docker_guest exists
    docker_guest_info = stack.check_resource(name=docker_guest,
                                             resource_type="server")

    # if docker_guest doesn't exists, create it.
    if not docker_guest_info:

        # Set un-paralled to make sure the guest is created
        # properly
        stack.unset_parallel()

        overide_values = {}
        overide_values["docker_guest"] = docker_guest
  
        default_values = {}
        default_values["docker_host"] = stack.docker_host
        default_values["auto_ssh_port"] = True
        default_values["publish2pipeline"] = True

        CustomConfigGroups = stack.insert_existing_attr("CustomConfigGroups",addNone=True)["CustomConfigGroups"]
        if CustomConfigGroups: default_values["add_groups"] = CustomConfigGroups

        optional_keys = []
        optional_keys.append("ssh_port")
        optional_keys.append("http_port")

        inputargs = {"overide_values":overide_values,
                     "optional_key":optional_keys,
                     "default_values":default_values}

        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Creating Docker Guest on docker_host "{}"'.format(stack.docker_host)
        stack.getlock_host.insert(display=True,**inputargs)

        # Wait to complete on host
        stack.wait_all_instance(**{ "queue_host":"instance","max_wt":"self"})

        # Re-enable parallelism
        stack.set_parallel()

    else:

        overide_values = {}
        overide_values["hostname"] = docker_guest
        overide_values["add_env_var"] = True

        inputargs = {"overide_values":overide_values}
        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Publish info for dock_guest"{}"'.format(docker_guest)
        stack.publish_info.insert(display=True,**inputargs)

    # add env_references
    env_ref = "{} hostname:{}".format(base_env,docker_guest)

    cvar_name = stack.tag

    input_args = {}
    input_args["type"] = "env"
    input_args["env_ref"] = env_ref
    input_args["name"] = cvar_name

    # DESTDIR for untaring files
    input_args["contents"] = {"DOCKER_BUILD_DIR":"/var/tmp/docker/build",
                              "DESTDIR":"/var/tmp/docker/build",
                              "TARBALL_DIR":TARBALL_DIR,
                              "DOCKER_ENV_FILE":docker_env_file}

    docker_host_info = stack.check_resource(name=stack.docker_host,
                                            resource_type="server",
                                            must_exists=True)[0]

    input_args["contents"]["DOCKERHOST_PUBLIC_IP"] = docker_host_info["public_ip"]
    input_args["contents"]["DOCKERHOST_PRIVATE_IP"] = docker_host_info["private_ip"]

    # If not run_only, we are registering the image
    if not stack.run_only: input_args["contents"]["DOCKER_IMAGE"] = DOCKER_IMAGE

    input_args["tags"] = "docker container ci build register {} {}".format(cvar_name,stack.docker_host)
    input_args["track"] = stack.track

    # We add EnvVars for the Run only
    pipeline_env_var = {}
    pipeline_env_var["COMMIT_HASH"] = stack.commit_hash
    existing_keys = [ "rep_key_loc"]
    existing_keys.append("repo_branch")
    existing_keys.append("repo_url")
    existing_keys.append("repo_branch")
    stack.insert_existing_attr(existing_keys,inputargs=pipeline_env_var)
    #if hasattr(stack,"repo_key_loc") and stack.repo_key_loc: pipeline_env_var["REPO_KEY_LOC"] = stack.repo_key_loc
    stack.add_metadata_to_run(pipeline_env_var,env_var_run=True)

    ######################################################
    default_values = {}
    default_values["commit_info"] = stack.commit_info

    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "continuous_delivery"
    inputargs["human_description"] = 'Publish commit_info'
    stack.run_commit_info.insert(display=True,**inputargs)

    # Wait to complete on host
    stack.wait_all_instance(**{ "queue_host":"instance","max_wt":"self"})

    # Disable parallelism
    stack.unset_parallel()

    # Associated cluster vars to hostgroups
    stack.add_cluster_envs(**input_args)

    groups = '{} local:::private::{} {}'.format(stack.cleanup_build,
                                                stack.repo_key_group,
                                                stack.build_groups)

    if stack.append_groups: 
        groups = "{} {}".format(groups,stack.append_groups)

    cvar_entry_env='name:{}'.format(cvar_name)
    stack.associate_cluster_env(groups=groups,entry=cvar_entry_env)
    stack.add_group_orders(groups,hostname=docker_guest,unassign=True)

    # Wait to complete on host
    stack.wait_hosts_tag(hostname=docker_guest)

    # If not run_only, we are registering the image
    if not stack.run_only: 
        cmd = "image register"
        order_type = "register-docker::api"
        role = "image/register"

        keys2pass = [ "author",
                      "message",
                      "commit_hash",
                      "event_type",
                      "authored_date",
                      "repo_url" ]

        image_metadata = stack.add_dict2dict(keys2pass,{},stack.commit_info)

        commit_url = stack.commit_info.get("url")
        if commit_url: image_metadata["commit_url"] = commit_url

        compare_url = stack.commit_info.get("compare")
        if compare_url: image_metadata["compare_url"] = compare_url

        repo_branch = stack.commit_info.get("branch")
        if repo_branch: image_metadata["repo_branch"] = repo_branch

        # Parse commit_info
        default_values = {}
        default_values["itype"] = "docker"
        default_values["image"] = DOCKER_IMAGE
        default_values["repo_url"] = stack.repo_url
        default_values["config_env"] = stack.config_env
        default_values["commit_hash"] = stack.commit_hash
        default_values["image_metadata"] = image_metadata
        default_values["cluster"] = stack.cluster
        if repo_branch: default_values["branch"] = repo_branch

        keys2pass = ["schedule_id", "job_id", "run_id", "job_instance_id"]
        stack.add_dict2dict(keys2pass,default_values,stackargs)

        human_description = "Registers docker image"
        long_description = "Records the docker image with repo_url = {}, branch = {}, commit_hash = {} to Jiffy DB".format(stack.repo_url,repo_branch,stack.commit_hash)

        stack.insert_builtin_cmd(cmd,
                                 order_type=order_type,
                                 human_description=human_description,
                                 long_description=long_description,
                                 display=None,
                                 role=role,
                                 default_values=default_values)

    return stack.get_results(stackargs.get("destroy_instance"))

