# API GATEWAY

The policy was writing according Security best practices in Amazon API Gateway
Added following checks

* Implement logging
* Implement Amazon CloudWatch alarms
* Enable AWS Config

## S3 Cross-Guard Security

Configuration for S3 Cross-Guard Security verifies that the S3 bucket has the following settings

* Versioning
* No "public-read" or "public-read-write" access
* S3 loggings
* Server-side encryption with KMS

## IAM

This configuration creates IAM roles and IAM policies  

* EC2 - Role
* Lambda Exec - Role
* lambda Logging - Policy
* EC2 Role - Policy
* Lambda Logs - Policy Attachment
* Lambda Vpc Access - Policy Attachment
* Instance Profile

To create this resources export your AWS credentials to terminal
run command

```bash
 export AWS_ACCESS_KEY_ID=""
 export AWS_SECRET_ACCESS_KEY=""
 export AWS_DEFAULT_REGION=""

 $ pulumi up
```

The IAM stack uses next input variables

* aws:region - the location where resources will be deployed
* region - to define a current region in the policies
* aws_account_id - to define a current account id in the policies

Output variables is:

* EC2 role name
* Lambda exec role arn
