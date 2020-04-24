**Description**

  - creates a docker registry with s3 as a backstore

**Infrastructure**

  - expects a dockerhost be available to be used to create the endpoint

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| docker_host   | name of the dockerhost                 | string   | None         |
| repo_url      | the repository to build code from      | string   | None         |
| dockerfile      | the dockerfile to build image      | string   | Dockerfile         |

**Optional**

| *argument*           | *description*                            | *var type* |  *default*      |
| ------------- | -------------------------------------- | -------- | ------------ |
| repo_branch        | branch to build from          | array    | master       |
| dockerfile_test      | the dockerfile to run unit tests    | string   | None         |

**Sample entry:**

```
build:
  ci_example:
    dependencies: 
      - infrastructure::dockerhost
      - infrastructure::ecr_repo
    stack_name: elasticdev:::ec2_ci_fastest
    arguments:
      docker_host: docker_flask_sample
      repo_url: https://github.com/bill12252016/flask_sample
      repo_branch: dev

```
