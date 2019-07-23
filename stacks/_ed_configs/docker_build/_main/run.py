def run(stackargs):

    import json

    # initiate stack 
    stack = newStack(stackargs)

    stack.parse.add_required(key="commit_hash")
    stack.parse.add_required(key="repo_url")
    stack.parse.add_required(key="repo_key_group")

    stack.parse.add_required(key="build_groups",default="elasticdev:::docker::simple_build")
    stack.parse.add_required(key="repo_branch",default="master")
    stack.parse.add_required(key="dockerfile",default="Dockerfile")
    stack.parse.add_required(key="docker_env_file",default="null")
    stack.parse.add_required(key="docker_build_dir",default="/var/tmp/docker/build")
    stack.parse.add_required(key="destdir",default="/var/tmp/docker/build")
    stack.parse.add_required(key="tarball_dir",default="/usr/src/tarballs")

    # The base environment variables used to build the docker container
    stack.parse.add_required(key="base_env",default="elasticdev:::docker::build")

    # The docker host needs to be provided and ready to be used by this stack
    stack.parse.add_required(key="docker_host",default="null")

    # Add substacks
    stack.add_substack('elasticdev:::wrapper_add_hostgroup')

    # init the variables before hostgroups
    stack.init_variables()
    stack.init_substacks()
    stack.init_hostgroups()

    # Set docker host accordingly
    if not stack.docker_host:
        stack.docker_host = "{}-docker_host".format(stack.cluster)  
        stackargs["docker_host"] = "{}-docker_host".format(stack.cluster)  

    # We add EnvVars for the Run only
    pipeline_env_var = {"COMMIT_HASH":stack.commit_hash}
    pipeline_env_var["REPO_BRANCH"] = stack.repo_branch
    pipeline_env_var["REPO_URL"] = stack.repo_url
    pipeline_env_var["DOCKER_BUILD_DIR"] = stack.docker_build_dir
    pipeline_env_var["DESTDIR"] = stack.destdir
    pipeline_env_var["TARBALL_DIR"] = stack.tarball_dir
    pipeline_env_var["DOCKER_FILE"] = stack.dockerfile
    if stack.docker_env_file: pipeline_env_var["DOCKER_ENV_FILE"] = stack.docker_env_file
    stack.add_host_env_vars_to_run(pipeline_env_var)

    # Check resource
    resource_info = stack.get_resource(name=stack.docker_host,
                                       resource_type="server",
                                       must_exists=True)[0]

    if resource_info.get("status") != "running" or resource_info.get("status") == "stopped":
        # Start the server when doing a build
        stack.modify_resource(resource_type="server",
                              human_description='Starting resource server hostname "{}"'.format(stack.docker_host),
                              provider="ec2",
                              name=stack.docker_host,
                              method="start")

    # Add repo key group to list of groups
    groups = 'local:::private::{} {}'.format(stack.repo_key_group,stack.build_groups)

    # Execute orders on docker_host
    human_description = 'Execute orders/tasks on hostname = "{}"'.format(stack.docker_host)
    default_values = {"groups":groups}
    default_values["hostname"] = stack.docker_host
    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "continuous_delivery"
    inputargs["human_description"] = human_description
    stack.wrapper_add_hostgroup.insert(display=True,**inputargs)

    # Stop the server when done to save money
    stack.modify_resource(resource_type="server",
                          human_description='Stopping resource server hostname "{}"'.format(stack.docker_host),
                          provider="ec2",
                          name=stack.docker_host,
                          method="stop")

    return stack.get_results()
