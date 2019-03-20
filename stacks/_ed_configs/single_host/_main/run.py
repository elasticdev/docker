def run(instructargs):

    stack = newStack(instructargs)

    # Add required variables
    stack.parse.add_required(key="hostname",default="NoNone")
    stack.parse.add_required(key="random_id",default="_random")
    stack.parse.add_required(key="proj_var_name",default="jiffy_host_base_build")
    stack.parse.add_required(key="access_group",default=None)

    # init the stack namespace
    stack.init_variables()

    #_groups = 'elasticdev:::docker::Docker/JiffyHost/BaseImage elasticdev:::docker::Docker/JiffyHost/Template'
    #groups = "{} {}".format(stack.access_group,_groups)

    # add hostgroups
    #stack.add_hostgroups(stack.access_group,"groups")

    # init hostgroups
    #stack.init_hostgroups()

    # add project_vars
    DOCKER_BUILD_DIR="/var/tmp/docker/build/{}".format(stack.random_id)
    contents = { "DOCKER_BUILD_DIR":DOCKER_BUILD_DIR }

    input_args = {}
    input_args["name"] = stack.proj_var_name
    input_args["type"] = "env"
    input_args["contents"] = contents
    input_args["tags"] = "{} single_host docker_host jiffy_host".format(stack.proj_var_name)
    stack.add_proj_env_vars(**input_args)

    # Need to unassign before remapping directories
    stack.unassign_hostgroups(hostname=stack.hostname)

    # Map build directory
    stack.host_map_dir(hostname=stack.hostname,
                       groups="ALL_map_dir_{}_1".format(stack.random_id),
                       dir_map="/var/tmp/docker/build:{}".format(DOCKER_BUILD_DIR))

    # Associate project vars to a set of hostgroups
    entry='name:{}'.format(stack.proj_var_name)
    stack.assoc_proj_vars_to_hostgroups(groups=stack.access_group,entry=entry)

    #####################################
    stack.set_parallel()
    #####################################

    stack.assoc_groups_to_host(stack.access_group,hostname=stack.hostname,assoc_proj_keys=False)

    resource_info = stack.get_resource(name=stack.hostname,
                                       resource_type="server",
                                       must_exists=True)[0]

    values = {"docker_host":stack.hostname}
    stack.add_stack_args_to_run(values)

    # Publish dockerhost 
    values["public_ip"] = resource_info["public_ip"]
    values["private_ip"] = resource_info["private_ip"]
    if resource_info.get("public_dns_name"): values["public_dns_name"] = resource_info["public_dns_name"]
    stack.publish(values)

    return stack.get_results(instructargs.get("destroy_instance"))
