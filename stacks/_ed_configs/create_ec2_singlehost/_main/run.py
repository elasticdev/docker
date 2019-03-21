def run(instructargs):

    #####################################
    stack = newStack(stackargs)
    #####################################

    stack.parse.add_required(key="os_version",default="16.04")
    stack.parse.add_required(key="hostname")
    stack.parse.add_required(key="key",default="first_ssh_key")
    stack.parse.add_required(key="sg_label",default=None)
    stack.parse.add_required(key="sg_web_label",default=None)
    stack.parse.add_required(key="sg",default=None)
    stack.parse.add_required(key="sg_web",default=None)

    # init the stack namespace
    stack.init_variables()

    if not stack.sg_label and stack.sg_web_label: 
        stack.sg_label = stack.sg_web_label

    if not stack.sg and stack.sg_web: 
        stack.sg = stack.sg_web

    # Create Docker Host
    instruction_name = "Cloud/Ec2/OS/ubuntu"
    optional_keys = ["queue_name",
                     "vpc",
                     "user",
                     "timeout",
                     "security_group",
                     "region"]

    default_values = {}
    default_values["size"] = "t2.medium"
    default_values["disksize"] = 100
    default_values["hostname"] = hostname
    default_values["key"] = key
    default_values["image_ref"] = "github_13456777:::public::ubuntu.{}-docker".format(os_version)
    default_values["ip_key"] = "private_ip"
    default_values["tags"] = "docker_host docker container single_host {} {} {}".format(hostname,os_version,"dev")
    if sg: default_values["sg"] = sg
    if sg_label: default_values["sg_label"] = sg_label

    human_description = "Initiates a Docker Server on Ec2"
    
    inputargs = {"name":instruction_name,
                 "default_values":default_values,
                 "optional_keys":optional_keys}
    
    inputargs["automation_phase"] = "initialize_infrastructure"
    inputargs["human_description"] = human_description
    inputargs["display"] = True
    inputargs["display_hash"] = instructions.get_hash_object(inputargs)

    instructions.add_instruction(**inputargs)
    ##############################################
    # Create the a single host without a deploy
    ##############################################
    required_keys = [ "soa" ]
    instruction_name = "Deploy/Docker/Setup/DNS/General/initialize"
    inputargs = {"name":instruction_name,
                 "default_values":default_values,
                 "required_keys":required_keys,
                 "optional_keys":optional_keys}

    inputargs["automation_phase"] = "initialize_infrastructure"
    inputargs["human_description"] = "Singlehost finalization of DockerHost: {}".format(hostname)
    inputargs["display"] = True
    inputargs["display_hash"] = instructions.get_hash_object(inputargs)
    instructions.add_instruction(**inputargs)
    #############################################
    instructions.wait_hosts_tag(tags=hostname)
    ##############################################
    instructions.add_pipeline_metadata({"docker_host":hostname},mkey="infrastructure",publish=True)
    ##############################################
    # Finalize configuration of Docker host
    ##############################################
    instruction_name = "Core/Docker/JiffyHost/initialize"

    default_values = {}
    default_values["hostname"] = hostname

    inputargs = {"name":instruction_name,
                 "default_values":default_values}

    inputargs["automation_phase"] = "initialize_infrastructure"
    inputargs["human_description"] = 'Add base docker_guest on "{}"'.format(hostname)
    inputargs["display"] = True
    inputargs["display_hash"] = instructions.get_hash_object(inputargs)
    instructions.add_instruction(**inputargs)
    ##############################################
    return instructions.get_results(instructargs.get("destroy_instance"))

def example():

    print '''
    '''
