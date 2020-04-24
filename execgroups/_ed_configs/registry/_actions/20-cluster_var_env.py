def default():

    task = {}
    env_vars = []
    shelloutconfigs = []
    shelloutconfigs.append('elasticdev:::cluster_vars::create_single_envfile')

    task['method'] = 'shelloutconfig'
    task['metadata'] = {'env_vars': env_vars,
                        'shelloutconfigs': shelloutconfigs
                        }

    return task
