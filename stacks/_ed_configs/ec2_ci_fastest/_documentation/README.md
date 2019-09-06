**Description**

  - This stack performs the fastest continuous integration through a dockerhost on AWS - ec2.  It sets up a webhook to connect directly to the allocated build dockerhost.  Unlike "ec2_ci" stack, this will not "stop" the machine after builds to save costs.  It takes about a minute or two for AWS to bring a machine up for a stopped state.  
  
  - How it works: code change is made, a webhook is sent directly to the dockerhost, which then tests and builds immediately.  It's liken to building locally. 

  - A good application is a feature branched, where you want to build and test remotely. However you want it to build immediately and take advantage of the docker cache and private network on AWS.  You may also want a "temporary" registroy on ecr to for this featured branched.  This stack inconjuction with the "ecr_repo" stack can create a completely separate featured development environmnent.   Once you're done, you can delete the project and the ecr_repo and build dockerhost will be deleted.

**Infrastructure**

  - expects a dockerhost be available to be used for builds
  - expects ec2 ecr to be created

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

        self.parse.add_required(key="dockerfile",default="null")

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
