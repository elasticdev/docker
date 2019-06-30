def run(stackargs):

    import json

    # initiate stack 
    stack = newStack(stackargs)

    stack.parse.add_required(key="commit_hash")
    stack.parse.add_required(key="repo_url")
    stack.parse.add_required(key="commit_info")
    stack.parse.add_required(key="repo_key_group")
    stack.parse.add_required(key="docker_repo")
    stack.parse.add_required(key="dockerfile",default="Dockerfile")
    stack.parse.add_required(key="docker_env_file",default="null")
    stack.parse.add_required(key="docker_build_dir",default="/var/tmp/docker/build")
    stack.parse.add_required(key="destdir",default="/var/tmp/docker/build")
    stack.parse.add_required(key="tarball_dir",default="/usr/src/tarballs")
    stack.parse.add_required(key="aws_default_region",default="us-east-1")
    stack.parse.add_required(key="tag",default="null")

    # The base environment variables used to build the docker container
    stack.parse.add_required(key="base_env",default="elasticdev:::docker::build")

    # The docker host needs to be provided and ready to be used by this stack
    stack.parse.add_required(key="docker_host")
    stack.parse.add_required(key="sched_name",default="NoNone")
    stack.parse.add_required(key="repo_branch",default="master")

    stack.parse.add_optional(key="config_env",default="private")

    # Add hostgroups
    stack.add_hostgroups("elasticdev:::docker::ecs_create_push_image","build_groups")

    # Add substacks
    stack.add_substack('elasticdev:::run_commit_info')
    stack.add_substack('elasticdev:::wrapper_add_hostgroup')
    stack.add_substack('elasticdev:::ecr_repo')

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

    # Check if ECR repo exists for docker images
    docker_repo = stack.check_resource(name=stack.docker_repo,
                                       resource_type="ecr_repo",
                                       provider="aws",
                                       must_exists=True)[0]

    ## Sleep to set reference point
    #time_increment = 1
    # Set parallel
    stack.set_parallel()

    # Publish commit_info
    default_values = {"commit_info":stack.commit_info}
    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "continuous_delivery"
    inputargs["human_description"] = 'Publish commit_info'
    stack.run_commit_info.insert(display=True,**inputargs)

    pipeline_env_var = {"DOCKER_REPO":stack.docker_repo}
    pipeline_env_var["DOCKER_IMAGE_TAG"] = stack.tag
    pipeline_env_var["image_tag"] = stack.tag
    stack.publish(pipeline_env_var)

    # Add additional views for pipeline env var
    # that isn't published
    # We add EnvVars for the Run only
    pipeline_env_var["COMMIT_HASH"] = stack.commit_hash
    pipeline_env_var["REPO_BRANCH"] = stack.repo_branch
    pipeline_env_var["REPO_URL"] = stack.repo_url
    pipeline_env_var["DOCKER_BUILD_DIR"] = stack.docker_build_dir
    pipeline_env_var["DESTDIR"] = stack.destdir
    pipeline_env_var["TARBALL_DIR"] = stack.tarball_dir
    pipeline_env_var["DOCKER_FILE"] = stack.dockerfile
    pipeline_env_var["REPOSITORY_URI"] = docker_repo["repository_uri"]
    if stack.docker_env_file: pipeline_env_var["DOCKER_ENV_FILE"] = stack.docker_env_file
    stack.add_host_env_vars_to_run(pipeline_env_var)

    # Getting ecr login
    human_description = "Getting ECR_LOGIN for pushing image"

    stack.execute_shellout(shelloutconfig="elasticdev:::aws::ecr_login",
                           human_description='executing shelloutconfig "{}"'.format("ecr_login"),
                           insert_env_vars=json.dumps(["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]),
                           env_vars=json.dumps({"METHOD":"get","AWS_DEFAULT_REGION":stack.aws_default_region}),
                           output_to_json=None,
                           insert_to_run_var="ECR_LOGIN",
                           run_key="EnvVars",
                           display=True)

    stack.wait_all_instance(**{ "queue_host":"instance","max_wt":"self"})

    # Disable parallelism
    stack.unset_parallel()

    # Add repo key group to list of groups
    groups = 'local:::private::{} {}'.format(stack.repo_key_group,
                                             stack.build_groups)

    # Execute orders on docker_host
    human_description = 'Execute orders/tasks on hostname = "{}"'.format(stack.docker_host)
    default_values = {"groups":groups}
    default_values["hostname"] = stack.docker_host
    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "continuous_delivery"
    inputargs["human_description"] = human_description
    stack.wrapper_add_hostgroup.insert(display=True,**inputargs)

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

    # We need the entire commit info for the SaaS API
    image_metadata = stack.commit_info
    stack.add_dict2dict(keys2pass,image_metadata,stack.commit_info)

    commit_url = stack.commit_info.get("url")
    if commit_url: image_metadata["commit_url"] = commit_url

    compare_url = stack.commit_info.get("compare")
    if compare_url: image_metadata["compare_url"] = compare_url

    repo_branch = stack.commit_info.get("branch")
    if repo_branch: image_metadata["repo_branch"] = repo_branch

    # Parse commit_info
    default_values = {"image_metadata":image_metadata}
    default_values["itype"] = "docker"
    default_values["repo_url"] = stack.repo_url
    default_values["config_env"] = stack.config_env
    default_values["commit_hash"] = stack.commit_hash
    default_values["cluster"] = stack.cluster
    default_values["provider"] = "aws"
    default_values["image"] = "{}:{}".format(docker_repo["repository_uri"],stack.tag)

    # We make the name of the image the same as the commit_hash
    default_values["name"] = stack.commit_hash

    _values = {"repo_name":docker_repo["repository_uri"].split("/")[-1]}
    _values["repo_type"] = "ecr"
    _values["product"] = "ecr"

    default_values["values"] = _values

    default_values["tags"] = [ "ecr",
                               "aws",
                               "docker",
                               docker_repo["repository_uri"],
                               stack.tag,
                               stack.repo_url,
                               stack.commit_hash,
                               stack.aws_default_region ]

    if repo_branch: 
        default_values["branch"] = repo_branch
        default_values["tags"].append(repo_branch)

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

    return stack.get_results()
