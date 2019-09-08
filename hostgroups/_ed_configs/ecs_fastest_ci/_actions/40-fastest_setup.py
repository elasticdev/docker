def default():
    
    task = {}
    env_vars = []
    shelloutconfigs = []

    shelloutconfigs.append('elasticdev:::docker::fastest_ci_setup')

    task['method'] = 'shelloutconfig'
    task['metadata'] = {'env_vars': env_vars, 
                        'shelloutconfigs': shelloutconfigs 
                        }

    return task
