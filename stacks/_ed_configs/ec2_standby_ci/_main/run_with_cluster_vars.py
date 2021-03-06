def run(stackargs):

    import json

    # initiate stack 
    stack = newStack(stackargs)

    stack.parse.add_required(key="commit_hash")
    stack.parse.add_required(key="repo_url")
    stack.parse.add_required(key="commit_info")
    stack.parse.add_required(key="repo_key_group")
    stack.parse.add_required(key="docker_image")
    stack.parse.add_required(key="dockerfile",default="Dockerfile")
    stack.parse.add_required(key="tag",default="null")

    # The base environment variables used to build the docker container
    stack.parse.add_required(key="base_env",default="elasticdev:::docker::build")

    # The docker host needs to be provided and ready to be used.
    stack.parse.add_required(key="docker_host")
    stack.parse.add_required(key="sched_name",default="NoNone")
    stack.parse.add_required(key="repo_branch",default="master")

    stack.parse.add_optional(key="config_env",default="private")

    # Add hostgroups
    stack.add_hostgroups("elasticdev:::docker::create_container elasticdev:::docker::push_container","build_groups")

    # Add substacks
    stack.add_substack('elasticdev:::run_commit_info')

    # init the stack namespace
    stack.init_variables()
    stack.init_substacks()
    stack.init_hostgroups()

    # Check and convert objects accordingly
    if not isinstance(stack.commit_info,dict): 
        stack.commit_info = stackargs["commit_info"] = json.loads(stack.commit_info)

    if isinstance(stack.commit_info,unicode) or isinstance(stack.commit_info,str): 
        stack.commit_info = stackargs["commit_info"] = eval(stack.commit_info)

    if not isinstance(stack.commit_info,dict):
        msg = "base_default_values is not a dictionary. It is {}".format(type(stack.commit_info))
        stack.logger.error(msg)
        stack.ehandle.NeedRtInput(message=msg)

    # Set parallel
    stack.set_parallel()

    # We add EnvVars for the Run only
    pipeline_env_var = {"COMMIT_HASH":stack.commit_hash}
    pipeline_env_var["REPO_BRANCH"] = stack.repo_branch
    pipeline_env_var["REPO_URL"] = stack.repo_url
    stack.add_host_env_vars_to_run(pipeline_env_var)

    # Publish commit_info
    default_values = {"commit_info":stack.commit_info}
    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "continuous_delivery"
    inputargs["human_description"] = 'Publish commit_info'
    stack.run_commit_info.insert(display=True,**inputargs)

    pipeline_env_var = {"DOCKER_IMAGE":stack.docker_image}
    pipeline_env_var["DOCKER_IMAGE_TAG"] = stack.tag
    pipeline_env_var["image_tag"] = stack.tag
    stack.publish(pipeline_env_var)
    stack.add_metadata_to_run({"docker":{"name":stack.tag}})

    # Add additional views for pipeline env var
    # that isn't published
    docker_env_file = "/var/tmp/docker/build/.env"
    pipeline_env_var["DOCKER_FILE"] = stack.dockerfile
    pipeline_env_var["DOCKER_ENV_FILE"] = docker_env_file
    stack.add_host_env_vars_to_run(pipeline_env_var)

    # Add cluster vars
    env_ref = "{} hostname:{}".format(stack.base_env,stack.docker_host)
    cvar_name = stack.get_hash_object("{}.build.{}".format(stack.cluster,stack.docker_host))

    input_args = {"type":"env"}
    input_args["env_ref"] = env_ref
    input_args["name"] = cvar_name

    input_args["contents"] = {"DOCKER_BUILD_DIR":"/var/tmp/docker/build",
                              "DESTDIR":"/var/tmp/docker/build",
                              "TARBALL_DIR":"/usr/src/tarballs",
                              "DOCKER_ENV_FILE":docker_env_file}

    input_args["tags"] = [ "docker",
                           "container",
                           "ci",
                           "build",
                           "register",
                           cvar_name,
                           stack.docker_host ]

    stack.add_cluster_envs(**input_args)

    # wait for queue orders below to complete
    stack.wait_all()

    # Disable parallelism
    stack.unset_parallel()

    # Add repo key group to list of groups
    groups = 'local:::private::{} {}'.format(stack.repo_key_group,
                                             stack.build_groups)

    # Associated cluster vars to hostgroups
    cvar_entry_env='name:{}'.format(cvar_name)
    stack.associate_cluster_env(groups=groups,entry=cvar_entry_env)

    # Execute orders on docker_host
    #stack.add_group_orders(groups,hostname=stack.docker_host,unassign=True)
    stack.add_groups_to_host(groups=groups,hostname=stack.docker_host)

    # Wait to complete on host
    stack.wait_hosts_tag(hostname=stack.docker_host)

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
    default_values = {"image_metadata":image_metadata}
    default_values["itype"] = "docker"
    default_values["image"] = stack.docker_image
    default_values["repo_url"] = stack.repo_url
    default_values["config_env"] = stack.config_env
    default_values["commit_hash"] = stack.commit_hash
    default_values["cluster"] = stack.cluster
    if repo_branch: default_values["branch"] = repo_branch

    keys2pass = ["schedule_id", "job_id", "run_id", "job_instance_id"]
    stack.add_dict2dict(keys2pass,default_values,stackargs)

    human_description = "Registers docker image"
    long_description = "Records the docker image with repo_url = {}, branch = {}, commit_hash = {} to Jiffy DB".format(stack.repo_url,
                                                                                                                       repo_branch,
                                                                                                                       stack.commit_hash)

    stack.insert_builtin_cmd(cmd,
                             order_type=order_type,
                             human_description=human_description,
                             long_description=long_description,
                             display=None,
                             role=role,
                             default_values=default_values)

    return stack.get_results(stackargs.get("destroy_instance"))
