**Description**

  - This stack performs continuous delivery through a webhook.

**Infrastructure**

  - expects a dockerhost be available to be used for deploys
  - expects ec2 ecr to be created

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| docker_host   | name of the dockerhost                 | string   | None         |
| repo_url      | the repository to build code from      | string   | None         |

**Optional**

| *argument*           | *description*                            | *var type* |  *default*      |
| ------------- | -------------------------------------- | -------- | ------------ |
| triggered_branches | branches to trigger builds from        | string   | master       |
| repo_branch        | branch to build from (array)           | array    | master       |

**Sample entry:**

```
build:
  cd_example:
    dependencies: 
      - infrastructure::dockerhost
      - infrastructure::ecr_repo
    stack_name: elasticdev:::direct_cd
    arguments:
      docker_host: docker_deploy_host
      repo_url: https://github.com/bill12252016/flask_sample
      repo_branch: master
      triggered_branches:
        - master

```
