def default():

    ordered_tasks=[]
    ordered_tasks.append("5-install-base.py,end")
    ordered_tasks.append("10-pull-code.py,end")
    ordered_tasks.append("20-cluster_var_env.py,end")
    ordered_tasks.append("40-env_file.py,end")
    ordered_tasks.append("50-cd_setup.py,end")
    ordered_tasks.append("60-launch_cd_builder.py,end")

    return ordered_tasks
