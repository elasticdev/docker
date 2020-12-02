def run(stackargs):

    import json

    stack = newStack(stackargs)
    stack.parse.add_required(key="registry_host")
    stack.parse.add_required(key="docker_registry_endpoint")
    stack.parse.add_required(key="ssl_private_key")
    stack.parse.add_required(key="ssl_private_cert")
    stack.parse.add_required(key="s3_bucket")
    stack.parse.add_required(key="aws_default_region",default="us-east-1")
    stack.parse.add_required(key="aws_credentials",default="aws")

    # Add hostgroups
    stack.add_hostgroups("elasticdev:::docker::registry","registry_groups")

    # Initialize
    stack.init_variables()
    stack.init_hostgroups()

    stack.set_variable("docker_registry_username",stack.get_random_string(size=12))
    stack.set_variable("docker_registry_password",stack.get_random_string(size=30))

    stack.check_resource(name=stack.registry_host,
                         resource_type="server",
                         must_exists=True)[0]

    #host_info = stack.get_host_info(hostname=stack.registry_host)

    publish_vars = {"DOCKER_REGISTRY_USERNAME":stack.docker_registry_username}
    publish_vars["DOCKER_REGISTRY_PASSWORD"] = stack.docker_registry_password

    # publish values to be seen and used
    stack.publish(publish_vars)

    pipeline_env_var = stack.get_resource(decrypt=True,
                                          name=stack.aws_credentials,
                                          resource_type="credentials",
                                          ref_schedule_id=stack.schedule_id,
                                          must_exists=True)[0]

    pipeline_env_var["DOCKER_REGISTRY_USERNAME"] = stack.docker_registry_username
    pipeline_env_var["DOCKER_REGISTRY_PASSWORD"] = stack.docker_registry_password
    pipeline_env_var["DOCKER_REGISTRY_ENDPOINT"] = stack.docker_registry_endpoint
    pipeline_env_var["SSL_PRIVATE_KEY"] = stack.ssl_private_key
    pipeline_env_var["SSL_PRIVATE_CERT"] = stack.ssl_private_cert
    pipeline_env_var["DOCKER_ENV_FILE"] = "/var/tmp/docker/build/.env"
    pipeline_env_var["AWS_DEFAULT_REGION"] = stack.aws_default_region
    pipeline_env_var["AWS_DEFAULT_REGION"] = stack.s3_bucket

    stack.add_host_env_vars_to_run(pipeline_env_var)

    # Execute orders on registry_host
    stack.add_groups_to_host(groups=stack.registry_groups,hostname=stack.registry_host)

    return stack.get_results()

#    # Add cluster vars
#    env_ref = "{} hostname:{}".format(stack.base_env,stack.docker_host)
#    cvar_name = stack.get_hash_object("{}.build.{}".format(stack.cluster,stack.docker_host))
#
#    input_args = {"type":"env"}
#    input_args["env_ref"] = env_ref
#    input_args["name"] = cvar_name
#
#    input_args["contents"] = pipeline_env_var
#
#    input_args["tags"] = [ "docker",
#                           "register",
#                           cvar_name ]
#
#    stack.add_cluster_envs(**input_args)
#
#    # Associated cluster vars to hostgroups
#    cvar_entry_env='name:{}'.format(cvar_name)
#    stack.associate_cluster_env(groups=registry_groups,entry=cvar_entry_env)
#
#    # Execute orders on docker_host
#    #stack.add_group_orders(groups,hostname=stack.docker_host,unassign=True)
#    stack.add_groups_to_host(groups=groups,hostname=stack.docker_host)


#REGISTRY_STORAGE_S3_ACCESSKEY=<api access key>
#REGISTRY_STORAGE_S3_SECRETKEY=<api secret>
#REGISTRY_STORAGE_S3_BUCKET=<bucket name>
#REGISTRY_STORAGE_S3_REGION=<region>
