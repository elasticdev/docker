**Description**

  - This stack creates a single docker host on ec2

**Required**

| *argument*            | *description*                            | *var type* |  *default*      |
|----------------|----------------------|---------------|---------------|
| os_version            | ubuntu os version                 | string   |  None         |
| hostname              | hostname for the docker host      | string   |  None         |
| aws_default_region    | aws default region for the docker host      | string   |  None         |
| region                | this will overide the aws region for the docker host      | string   |  None         |
| key                   | the ssh key to create the hostname with      | string   |  None         |

**Optional**

| *argument*           | *description*                            | *var type* |  *default*      |
|----------------|----------------------|---------------|---------------|
| sg_label             | label for security group        | string   | None       |
| sg_web_label         | label for security group "web"      | string   | None       |
| sg                   | the security group name      | string   | None       |
| sg_web               | the security group name for "web" layer in vpc      | string   | None       |
| size                 | the size of the ec2 docker host to create     | string   | None       |




