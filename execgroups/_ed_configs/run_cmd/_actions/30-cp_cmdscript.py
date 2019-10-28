def default():
    
    task = {}
    env_vars = []
    shelloutconfigs = []

    env_vars.append("elasticdev:::docker::build")
    shelloutconfigs.append('elasticdev:::docker::copy_cmd_script')

    task['method'] = 'shelloutconfig'
    task['metadata'] = {'env_vars': env_vars, 
                        'shelloutconfigs': shelloutconfigs 
                        }

    return task
