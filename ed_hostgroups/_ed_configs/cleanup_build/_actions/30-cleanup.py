def default():
    
    task = {}
    env_vars = []
    shelloutconfigs = []
    shelloutconfigs.append('elasticdev:::docker::cleanup_build')

    task['method'] = 'shelloutconfig'
    task['metadata'] = {'env_vars': env_vars, 
                        'shelloutconfigs': shelloutconfigs 
                        }

    return task
