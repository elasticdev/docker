def run(stackargs):

    # instantiate stack
    stack = newStack(stackargs)

    # add variables
    stack.parse.add_required(key="os_version",default="16.04")
    stack.parse.add_required(key="hostname",default="null")
    stack.parse.add_required(key="key",default="first_ssh_key")
    stack.parse.add_required(key="sg_label",default="null")
    stack.parse.add_required(key="sg_web_label",default="null")
    stack.parse.add_required(key="sg",default="null")
    stack.parse.add_required(key="sg_web",default="null")

    # Add substacks
    stack.add_substack('elasticdev:::ed_core::getlock_host')
    stack.add_substack('elasticdev:::ubuntu::ec2_ubuntu')

    # init the stack namespace
    stack.init_variables()
    stack.init_substacks()

    if not stack.sg_label and stack.sg_web_label: 
        stack.set_variable("sg_label",stack.sg_web_label)

    if not stack.sg and stack.sg_web: 
        stack.set_variable("sg",stack.sg_web)

    if not stack.hostname:
        stack.set_variable("hostname","{}-{}".format(stack.cluster,"docker_host"))

    # create ubuntu docker host
    optional_keys = ["queue_name",
                     "vpc",
                     "user",
                     "timeout",
                     "security_group",
                     "region"]

    default_values = {}
    default_values["size"] = "t2.medium"
    default_values["disksize"] = 100
    default_values["hostname"] = stack.hostname
    default_values["key"] = stack.key
    default_values["image_ref"] = "github_13456777:::public::ubuntu.{}-docker".format(stack.os_version)
    default_values["ip_key"] = "private_ip"
    default_values["tags"] = "docker_host docker container single_host {} {} {}".format(stack.hostname,stack.os_version,"dev")
    if stack.sg: default_values["sg"] = stack.sg
    if stack.sg_label: default_values["sg_label"] = stack.sg_label
    
    inputargs = {"default_values":default_values,
                 "optional_keys":optional_keys}
    
    inputargs["automation_phase"] = "initialize_infrastructure"
    inputargs["human_description"] ="Initiates a Docker Server on Ec2"
    inputargs["display"] = True
    inputargs["display_hash"] = stack.get_hash_object(inputargs)

    # add the stack with variables
    stack.ec2_ubuntu.insert(**inputargs)

    #stack.wait_hosts_tag(tags=stack.hostname)
    # publish hostname
    #stack.add_metadata_to_run({"docker_host":stack.hostname},mkey="infrastructure",publish=True)

    return stack.get_results(stackargs.get("destroy_instance"))
