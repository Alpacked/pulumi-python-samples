
## Versions

This block describes versions of packages we use

```none
Python - 3.9.2
Pulumi - 2.23.2
```

For linters:

```none
pylint - 2.7.2
flake8 - 3.9.0
markdownlint - 0.27.1
```

## Contributing

### Code quality

This repository has github actions configured in order to run on-push checks for linters ( markdown, python and spellcheck ) and pulumi `preview` and `up` commands
Dictionary for spellchecks is configured in .github/linters/spellcheck-dict.txt, if you are sure that you didn't make a spellcheck - you can add new words to the dictionary.
When creating PR make sure that you've fixed all failing CI checks, we recommend linting the code before pushing it to your branch

### Pulumi

When testing your feature on separate branch - create a stack starting with `ID-#ISSUE-NUMBER` and test all your updates there.
After your code is ready and you created the PR - you can reference this stack to show off your work and how it was tested.
Make sure to remove the stack after your branch was merged and deleted.
All the modules are configured inside `pulumi/modules/` folders. After code is merged into `master` all the `dev-*` stacks should be updated.
Pulumi github action will try to run `pulumi preview` when you create/update the PR, and `pulumi up` when the PR is merged.

## Connect to S3 backend

To get started transform Terraform to Pulumi you must do:

1) Add aws credentials:

    ```bash
        - export AWS_ACCESS_KEY_ID=""
        - export AWS_SECRET_ACCESS_KEY=""
        - export AWS_DEFAULT_REGION="eu-central-1"
    ```

2) Logging Into s3 Backend
    - pulumi login s3://sandbox-state

3) Add some resource and then run command pulumi up and check the result

4) Self-managed backends requires passphrase, so I typed this passphrase and it requires when you run command pulumi up

If you want to create another stack and save it's state in the same s3 storage, you must do next steps:

1) Add aws credentials:

    ```bash
        - export AWS_ACCESS_KEY_ID=""
        - export AWS_SECRET_ACCESS_KEY=""
        - export AWS_DEFAULT_REGION="eu-central-1"
    ```

2) Logging Into s3 Backend

    ```bash
    - pulumi login s3://sandbox-state
    ```

3) Type the command:

    ```bash
    pulumi stack init <StackName> --secrets-provider="awskms://<stack ID/arn/alias>"
    ```

4) You can see all stacks:

    ```bash
    pulumi stack ls
    ```

5) And if you want, you can change active stack with command

    ```bash
    pulumi stack select <StackName>
    ```

## Structure of project with stack references modules

The project consists of the following modules:

- rds instance
  - Input: vpc id
  - Output: rds instance address, db password, airflow password
- secrets manager
  - Input: rds instance address, db password, airflow password
  - Output: None
- vpc endpoints
  - Input: aws vpc id, aws public route table id, aws security group id, aws instance subnet id
  - Output: None
- vpc
  - Input: None
  - Output: vpc id, subnet id
- lambda
  - Input: db password, rds address, vpc id, ec2 subnet id, ec2 security group id and lambda execution role
  - Output: None
- security groups
  - Input: vpc id
  - Output: db security group id, ec2 security group id
- ec2 instance
  - Input: ec2 security group id, ec2 role name, subnet id
  - Output: ec2 subnet id

If you want to create another stack module you must do next steps:

1) Create a new directory in pulumi/modules/ and go to it:

    ```bash
    mkdir pulumi/modules/<module_name> && cd pulumi/modules/<module_name> 
    ```

2) Create basic structure of project with files __main__.py, Pulumi.yaml and requirements.txt
3) Create new stack

    ```bash
    pulumi stack init <StackName> --secrets-provider="awskms://<stack ID/arn/alias>"
    ```

4) Write you module code in __main__.py
5) If you want connect another stack module in your module, do next:

    ```bash
    from pulumi import StackReference   

    rds_instance = StackReference("rds-instance")   

    address = rds_instance.get_output("address")   
    db_password_result = rds_instance.get_output("db_password")   
    airflow_password_result = rds_instance.get_output("airflow_password")   
    ```

6) But don't forget in module, which you connect, do next:

    ```bash
    pulumi.export("address", default.address)   
    pulumi.export("db_password", db_password.result)   
    pulumi.export("airflow_password", airflow_pass.result)
    ```

7) Attention! Names may differ from yours in last two examples!

## Structure of project with class modules

1) Project consist from next modules (and dependencies between them):
   - vpc.py
   - security_groups.py
         - vpc id from module vpc.py
   - iam.py
   - rds.py
         - db subnet group name from module vpc.py
         - db security group id from module security_groups.py
   - lambda_functions.py
         - ec2 security group id from security_groups.py
         - ec2 subnet id from module vpc.py
         - db password and rds address from module rds.py
         - lambda execution role from module iam.py
   - api_gateway.py
         - lambda get function name and arn, lambda post function name and arn from module lambda_functions.py
   - ec2.py
         - vpc id and ec2 subnet id from module vpc.py
         - ec2 security group from module security groups.py
         - ec2 role name and iam instance profile name from module iam.py
         - default rest api id from module api_gateway.py
   - vpc_endpoints.py
         - vpc id, ec2 instance subnet id and public route table id from module vpc.py
         - ec2 security group from module security_groups.py
   - secrets_manager.py
         - db password, airflow password and rds address from module rds.py
   - s3.py
         - admin_list, vpc_endpoint_id, ec2_role_arn, bucket_name, name_suffix

2) List of variables, that can be added into config file:
   - billing_code: str
   - create_db_subnets: bool
   - create_lambda_and_apigateway: bool
   - db_instance_type: str
   - db_subnets_cidr: list
   - db_username: str
   - ec2_instance_type: str
   - egress_ec2_rule_ports: list
   - enable_dns_hostnames: bool
   - enable_dns_support: bool
   - flow_log_cloudwatch_log_group_kms_key_id: str
   - flow_log_cloudwatch_log_group_name_prefix: str
   - flow_log_cloudwatch_log_group_retention_in_days: str
   - flow_log_destination_type: str
   - flow_log_log_format: str
   - flow_log_max_aggregation_interval: int
   - flow_log_traffic_type: str
   - ingress_ec2_rule_ports: list
   - project_name: str
   - public_subnets_cidr: list
   - rule_cidr_blocks: list
   - region: str
   - repo_deploy_key: str
   - vpc_cidr_block: str

3) List of outputs, that we will get:
   - ApiGateway URL
   - EC2 public ip
   - db username

4) If you want create another module, do next steps:
   - create file module_name.py in folder /pulumi/
   - create classes with a constructor, which creates resources, which you need
   - import this module in __main__.py with command import module_name
   - create an instance of the class, which you created

5) You can create all infrastructure with only one command pulumi up in __main__.py  

## Presets

Presets module do next:

- checks configuration (VPC existing and validity of project name)
- creates SSH keypair
- create GitHub repository
- adds public key to repo

For creating GitHub repository and adding deploy key you must add GitHub Access Token:

   ```bash
   export GITHUB_TOKEN=""
   ```

## Pulumi CrossGuard

We decided to implement Policy as Code to enforce compliance for resources.
Our Policy Pack stores in pulumi/policypack folder.
All policies store in pulumi/policypack/policies/ folder as python files.
Configuration of Policy Pack store in pulumi/policypack/__main__.py file

To run the Policy Pack locally against a Pulumi program, execute next command:

   ```bash
   pulumi preview --policy-pack <path-to-policy-pack-directory>
   ```

The following functions are contained in the Policy Pack

- Security groups:
  - rules_no_unexpected_ports_validator, which checks ports for security groups
  - rules_no_all_allow_cidr_validator, which checks that rules don't have 0.0.0.0/0 in security groups
  - db_no_public_sg_validator, which checks source for db security groups
- IAM:
  - role_assume_policy_validator, which checks, that assume role policies have expected services
  - vpc_flow_log_policy_validator, which checks, that the policy don't have unexpected actions
  - ec2_policy_validator, which checks, that the policy don't have unexpected actions
  - lambda_policy_attach_validator, which checks, that the policy ARN have expected value.
- RDS:
  - rds_subnet_validator, which checks, that DB subnet group name have expected value.
  - rds_instance_class_validator, which checks, that instance class have expected value.
  - rds_publicity_validator, which checks, that instance don't have public access.
  - rds_encrypt_validator, which checks, that instance storage encrypted.
  - rds_username_validator, which checks, that username for RDS have expected value.
  - rds_monitoring_enabled, which checks that monitoring enabled for RDS instance.
  - rds_backup_retention_enabled, which checks, that backup retention enabled for RDS instance.
  - rds_multiAZ_enabled, which checks, that multiAZ enabled enabled for RDS instance.
  - rds_logging_enabled, which checks, that logging enabled for RDS instance.
- EC2:
  - ec2_iam_profile_validator, which checks, that IAM instance profile have expected value.
  - ec2_instance_type_validator, which checks, that instance type have expected value.
  - ec2_public_ip_validator, which checks, that instance have associated public IP address.
  - ec2_ebs_encrypted_validator, which checks, that all EBS (root and other) encrypted.
- VPC:
  - subnets_belong_to_vpc_validator, which checks, that they belong to one VPC.
  - subnets_has_private_cidr_validator, which checks, that they have private CIDR block.
  - vpc_has_private_cidr_validator, which checks, that they have private CIDR block.
  - public_ip_on_lunch_validator, which checks, that they assign public IP for instances on launch.
  - dns_support_and_hostnames_enabled_validator, which checks, that DNS hostnames and supports is enabled for VPCs.
  - route_gateway_validator, which checks, that they have attached internet gateway.
- VPC Endpoints:
  - vpce_private_dns_enabled_validator, which checks, that private DNS is enabled for VPC endpoints.
  - vpce_service_name_validator, which checks, that they have expected service name.
  - vpce_type_validator, which checks, that they have expected VPC endpoint type.
  - vpce_belong_to_vpc_validator, which checks, that they belong to one VPC.
- Secrets manager:
  - sm_rotation_enabled_validator, which checks, that rotation is enabled for secrets.
  - custom_kms_key_uses_validator, which checks, that they use custom KMS key for encryption.
