def run(stackargs):

    import json

    stack = newStack(stackargs)

    stack.parse.add_required(key="repo_url")
    stack.parse.add_required(key="repo_branch",default="dev")

    # The repo_key_group is automatically added with ED creates the webhook and deployment key
    stack.parse.add_required(key="repo_key_group")
    stack.parse.add_required(key="project_id")
    stack.parse.add_required(key="dest_env_file",default="/var/tmp/docker/run/.env")
    stack.parse.add_required(key="docker_host",default="null")
    stack.parse.add_required(key="config_env",default="private")
    stack.parse.add_required(key="docker_repo")
    stack.parse.add_required(key="dockerfile",default="Dockerfile")
    stack.parse.add_required(key="docker_env_file",default="null")
    stack.parse.add_required(key="docker_build_dir",default="/var/tmp/docker/build")
    stack.parse.add_required(key="docker_run_dir",default="/var/tmp/docker/run")
    stack.parse.add_required(key="destdir",default="/var/tmp/docker/build")
    stack.parse.add_required(key="tarball_dir",default="/usr/src/tarballs")
    stack.parse.add_required(key="aws_default_region",default="us-east-1")
    stack.parse.add_required(key="tag",default="null")
    stack.parse.add_required(key="aws_default_region",default="us-east-1")
    stack.parse.add_required(key="jiffy_saas_env",default="app")
    stack.parse.add_required(key="webhook_api_endpoint",default="null")

    # Call endpoint
    #stack.parse.add_required(key="callback_api_endpoint")
    stack.parse.add_required(key="callback_token")
    stack.parse.add_required(key="sched_token")

    stack.parse.add_optional(key="run_title",default="fastest_docker_ci")
    stack.parse.add_optional(key="job_name",default="fastest_docker_ci")

    # location of the Dockerfile for unit tests
    stack.parse.add_optional(key="dockerfile_test",default="null")
    stack.parse.add_optional(key="commit_info",default="null")
    stack.parse.add_optional(key="commit_hash",default="null")
    stack.parse.add_optional(key="init",default="null")

    #stack.add_substack("elasticdev:::docker::ec2_fast_direct_ci")
    #stack.init_substacks()
    stack.add_substack("elasticdev:::ed_core::run_commit_info")
    stack.add_substack('elasticdev:::add_groups2host')
    stack.add_substack('elasticdev:::ecr_repo')

    # Add hostgroups
    stack.add_hostgroups("elasticdev:::docker::ecs_fastest_ci","build_groups")

    stack.init_variables()
    stack.init_substacks()
    stack.init_hostgroups()

    # Set docker host accordingly
    if not stack.docker_host:
        stack.set_variable("docker_host","{}-docker_host".format(stack.cluster))

    if not stack.webhook_api_endpoint:
        stack.set_variable("webhook_api_endpoint","https://api-{}.elasticdev.io/web_api/v1.0/github/webhook".format(stack.jiffy_saas_env))

    docker_host_info = stack.check_resource(name=stack.docker_host,
                                            resource_type="server",
                                            must_exists=True)[0]

    host_info = stack.get_host_info(hostname=stack.docker_host)

    stack.set_variable("public_ip",docker_host_info["public_ip"])

    stack.set_variable("trigger_id",stack.get_random_string(size=12))
    stack.set_variable("trigger_secret",stack.get_random_string(size=30))

    # Check if ECR repo exists for docker images
    docker_repo = stack.check_resource(name=stack.docker_repo,
                                       resource_type="ecr_repo",
                                       provider="aws",
                                       must_exists=True)[0]

    # Make callback to setup webhook
    stack.set_variable("post_url","https://{}/{}".format(stack.public_ip,stack.trigger_id))

    pipeline_env_var = {"REPO_URL":stack.repo_url}
    pipeline_env_var["REPO_BRANCH"] = stack.repo_branch
    pipeline_env_var["DOCKER_BUILD_DIR"] = stack.docker_build_dir
    pipeline_env_var["DESTDIR"] = stack.destdir
    pipeline_env_var["TARBALL_DIR"] = stack.tarball_dir
    pipeline_env_var["DOCKER_FILE"] = stack.dockerfile
    pipeline_env_var["REPOSITORY_URI"] = docker_repo["repository_uri"]
    pipeline_env_var["TRIGGER_BRANCH"] = stack.repo_branch
    pipeline_env_var["POST_URL"] = stack.post_url
    pipeline_env_var["TRIGGER_ID"] = stack.trigger_id
    pipeline_env_var["TRIGGER_SECRET"] = stack.trigger_secret
    pipeline_env_var["DOCKER_RUN_DIR"] = stack.docker_run_dir
    pipeline_env_var["DOCKER_IMAGE_TAG"] = "latest"
    pipeline_env_var["DOCKER_RUN_IGNORE_COPY"] = "True"
    pipeline_env_var["DOCKER_COMPOSE_BUILD"] = "True"

    pipeline_env_var["PROJECT_ID"] = stack.project_id

    if hasattr(stack,"sched_name") and stack.sched_name:
        pipeline_env_var["SCHED_NAME"] = stack.sched_name

    if hasattr(stack,"sched_type") and stack.sched_type:
        pipeline_env_var["SCHED_TYPE"] = stack.sched_type

    if hasattr(stack,"run_title") and stack.run_title:
        pipeline_env_var["RUN_TITLE"] = stack.run_title

    if hasattr(stack,"job_name") and stack.job_name:
        pipeline_env_var["JOB_NAME"] = stack.job_name

    if hasattr(stack,"schedule_id") and stack.schedule_id:
        pipeline_env_var["SCHEDULE_ID"] = stack.schedule_id

    # Enter host info
    pipeline_env_var["HOST_QUEUE"] = host_info["host_queue"]
    pipeline_env_var["HOST_TOKEN"] = host_info["token"]

    if hasattr(stack,"qhost_callback_token") and stack.qhost_callback_token:
        pipeline_env_var["QHOST_CALLBACK_TOKEN"] = stack.qhost_callback_token

    pipeline_env_var["DEST_ENV_FILE"] = stack.dest_env_file

    pipeline_env_var["ENV_FIELDS"] = json.dumps(["REPO_KEY_LOC",
                                                 "SCHEDULE_ID",
                                                 "SCHEDULE_TOKEN",
                                                 "DOCKER_FILE",
                                                 "DOCKER_FILE_TEST",
                                                 "REPOSITORY_URI",
                                                 "QHOST_CALLBACK_TOKEN",
                                                 "TRIGGER_ID",
                                                 "TRIGGER_BRANCH",
                                                 "TRIGGER_SECRET",
                                                 "ECR_LOGIN"]) 
    #"DOCKER_USERNAME",
    #"DOCKER_PASSWORD",

    if stack.tag: pipeline_env_var["DOCKER_IMAGE_TAG"] = stack.tag

    if stack.dockerfile_test: pipeline_env_var["DOCKER_FILE_TEST"] = stack.dockerfile_test
    if stack.docker_env_file: pipeline_env_var["DOCKER_ENV_FILE"] = stack.docker_env_file
    stack.add_host_env_vars_to_run(pipeline_env_var)

    # Publish pipeline
    stack.publish(pipeline_env_var)

    # Add commit info for the first run
    if stack.commit_info and stack.init:
        inputargs = {"automation_phase":"continuous_delivery"}
        inputargs["human_description"] = 'Publish commit_info'
        inputargs["default_values"] = {"commit_info":stack.commit_info}
        stack.run_commit_info.insert(display=True,**inputargs)

    # Getting ecr login
    # It runs the shellout and places
    # the output in the environment variable "ECR_LOGIN"
    # that will be stored in EnvVars in the pipeline run
    stack.execute_shellout(shelloutconfig="elasticdev:::aws::ecr_login",
                           human_description="Getting ECR_LOGIN for pushing image",
                           insert_env_vars=json.dumps(["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]),
                           env_vars=json.dumps({"METHOD":"get","AWS_DEFAULT_REGION":stack.aws_default_region}),
                           output_to_json=None,
                           insert_to_run_var="ECR_LOGIN",
                           run_key="EnvVars",
                           display=True)

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
    stack.add_groups2host.insert(display=True,**inputargs)

    values = {"schedule_id":stack.schedule_id}
    values["post_url"] = stack.post_url
    values["name"] = stack.cluster
    values["cluster"] = stack.cluster
    values["instance"] = stack.instance
    values["repo_url"] = stack.repo_url
    values["repo_branch"] = stack.repo_branch
    values["secret"] = stack.trigger_secret
    values["trigger_id"] = stack.trigger_id
    values["project_id"] = stack.project_id
    values["clobber"] = True
    values["control_repo"] = None
    # We all insecure ssl since it's just an ip address
    # This can be changed later if using DNS
    values["insecure_ssl"] = True

    default_values = {}
    default_values["http_method"] = "post"
    default_values["api_endpoint"] = stack.webhook_api_endpoint
    default_values["callback"] = stack.callback_token
    default_values["values"] = "{}".format(str(stack.dict2str(values)))

    human_description = 'Creating webhook at "{}"'.format(stack.post_url)

    stack.insert_builtin_cmd("execute restapi",
                             order_type="saas-report_sched::api",
                             default_values=default_values,
                             human_description=human_description,
                             display=True,
                             role="ed/api/execute")

    return stack.get_results()
