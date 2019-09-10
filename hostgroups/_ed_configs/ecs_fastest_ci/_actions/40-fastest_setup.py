def default():
    
    task = {}
    env_vars = []
    shelloutconfigs = []

    shelloutconfigs.append('elasticdev:::cluster_vars::create_envfile_frm_run')
    shelloutconfigs.append('elasticdev:::docker::fastest_ci_setup')
    shelloutconfigs.append('elasticdev:::docker::docker-compose-run')

    task['method'] = 'shelloutconfig'
    task['metadata'] = {'env_vars': env_vars, 
                        'shelloutconfigs': shelloutconfigs 
                        }

    return task
