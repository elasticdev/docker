This stack preforms continuous integration through a dockerhost on AWS - ec2.  It responds to webhooks and builds code accordingly.

Sample entry:

build:
   ci_example:
       dependencies: 
           - infrastructure::dockerhost
           - infrastructure::ecr_repo
       stack_name: elasticdev:::ec2_ci
       arguments:
           docker_host: docker_flask_sample
           repo_url: https://github.com/bill12252016/flask_sample
           repo_branch: master
           triggered_branches:
             - master
