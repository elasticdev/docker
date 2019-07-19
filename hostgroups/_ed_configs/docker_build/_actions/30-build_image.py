def default():
    
    task = {}
    env_vars = []
    shelloutconfigs = []

    env_vars.append("elasticdev:::docker::build")
    shelloutconfigs.append('elasticdev:::docker::simple_build')

    task['method'] = 'shelloutconfig'
    task['metadata'] = {'env_vars': env_vars, 
                        'shelloutconfigs': shelloutconfigs 
                        }

    return task
