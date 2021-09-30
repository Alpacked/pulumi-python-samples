from pulumi import ComponentResource, ResourceOptions, Output
import pulumi_aws as aws
import json


class IamArgs:
    """Create class VpcArgs for conveniently passing arguments to the class Vpc
       These arguments are used for configuration IAM
       roles and attachment policies:
       - region - specify region in which you want create
       - aws_account_id - id of current aws account
       - project_name_underscores - modified project name
       - name_suffix - random suffix that is added to all unique resources"""

    def __init__(
        self,
        region,
        aws_account_id,
        project_name_underscores,
        name_suffix,
    ):

        self.region = region
        self.aws_account_id = aws_account_id
        self.project_name_underscores = project_name_underscores
        self.name_suffix = name_suffix


class Iam(ComponentResource):
    """Create class Iam which extends class ComponentResource"""

    def __init__(self, name: str, args: IamArgs, opts: ResourceOptions = None):
        """Create constructor of class Iam
           This constructor creates IAM role for EC2 instance,
           role for lambda functions execution and role for
           lambda functions logging"""

        super().__init__("custom:resource:Iam", name, {}, opts)
        """Override ComponentResource class constructor"""

        self.ec2_role = aws.iam.Role(
            "ec2Role",
            name=Output.all(
                args.project_name_underscores,
                args.name_suffix
                ).apply(
                lambda args: f"{args[0]}-{args[1]}-ec2-role"),
            assume_role_policy="""{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Effect": "Allow",
                    "Sid": ""
                }]
            }
        """,
            opts=ResourceOptions(parent=self),
        )

        self.default = aws.iam.InstanceProfile(
            "default",
            name=Output.all(
                args.project_name_underscores,
                args.name_suffix
                ).apply(
                lambda arg: f"{arg[0]}-{arg[1]}-instance_profile"),
            role=self.ec2_role.name,
            opts=ResourceOptions(parent=self),
        )

        self.lambda_exec = aws.iam.Role(
            "lambdaExec",
            name=Output.all(
                args.project_name_underscores,
                args.name_suffix
                ).apply(
                lambda arg: f"{arg[0]}-{arg[1]}-lambda_iam_role"),
            assume_role_policy="""{
            "Version": "2012-10-17",
            "Statement": [
                {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
        }
        """,
            opts=ResourceOptions(parent=self),
        )

        lambda_logging = aws.iam.Policy(
            "lambdaLogging",
            description="IAM policy for logging from a lambda",
            path="/",
            policy="""{
                "Version": "2012-10-17",
                "Statement": [
                    {
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "arn:aws:logs:*:*:*",
                    "Effect": "Allow"
                    }]
                }
            """,
            opts=ResourceOptions(parent=self),
        )

        lambda_retrieve_secrets = aws.iam.Policy(
            "lambdaRetrieveSecrets",
            description="IAM policy for retrieve secrets from SM",
            path="/",
            policy="""{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "secretsmanager:GetResourcePolicy",
                            "secretsmanager:GetSecretValue",
                            "secretsmanager:DescribeSecret",
                            "secretsmanager:ListSecretVersionIds"
                        ],
                        "Resource": ["*"]
                    }
                ]
            }""",
            opts=ResourceOptions(parent=self),
        )

        self.ec2_role_policy = aws.iam.RolePolicy(
            "ec2RolePolicy",
            name=Output.all(
                args.project_name_underscores,
                args.name_suffix
                ).apply(
                lambda arg: f"{arg[0]}-{arg[1]}-ec2-role-policy"),
            role=self.ec2_role.id,
            policy=Output.all(
                args.project_name_underscores,
                args.name_suffix,
                args.aws_account_id,
                args.region
                ).apply(
                lambda args: json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "ssm:DescribeAssociation",
                                "ssm:GetDeployablePatchSnapshotForInstance",
                                "ssm:GetDocument",
                                "ssm:DescribeDocument",
                                "ssm:GetManifest",
                                "ssm:GetParameter",
                                "ssm:GetParameters",
                                "ssm:ListAssociations",
                                "ssm:ListInstanceAssociations",
                                "ssm:PutInventory",
                                "ssm:PutComplianceItems",
                                "ssm:PutConfigurePackageResult",
                                "ssm:UpdateAssociationStatus",
                                "ssm:UpdateInstanceAssociationStatus",
                                "ssm:UpdateInstanceInformation"
                            ],
                            "Resource": "*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "ssmmessages:CreateControlChannel",
                                "ssmmessages:CreateDataChannel",
                                "ssmmessages:OpenControlChannel",
                                "ssmmessages:OpenDataChannel"
                            ],
                            "Resource": "*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "ec2messages:AcknowledgeMessage",
                                "ec2messages:DeleteMessage",
                                "ec2messages:FailMessage",
                                "ec2messages:GetEndpoint",
                                "ec2messages:GetMessages",
                                "ec2messages:SendReply"
                            ],
                            "Resource": "*"
                        },
                        {
                            "Sid": "secretsPermissions",
                            "Effect": "Allow",
                            "Action": [
                                "secretsmanager:GetResourcePolicy",
                                "secretsmanager:GetSecretValue",
                                "secretsmanager:DescribeSecret",
                                "secretsmanager:ListSecretVersionIds"
                            ],
                            "Resource": [
                                f"arn:aws:secretsmanager:{args[3]}:{args[2]}:secret:{args[1]}_*",  # noqa: E501
                                f"arn:aws:secretsmanager:ap-south-1:{args[2]}:secret:dod-sendgrid-api-key"]  # noqa: E501
                        },
                        {
                            "Sid": "secretsManagerPermissions",
                            "Effect": "Allow",
                            "Action": [
                                "secretsmanager:GetRandomPassword",
                                "secretsmanager:ListSecrets"
                            ],
                            "Resource": "*"
                        },
                        {
                            "Sid": "s3Access",
                            "Action": [
                                "s3:DeleteObject",
                                "s3:GetObject",
                                "s3:ListBucket",
                                "s3:PutObject"
                                ],
                            "Effect": "Allow",
                            "Resource": [
                                    f"arn:aws:s3:::datalake-{args[0]}",
                                    f"arn:aws:s3:::datalake-{args[0]}/*",
                                    f"arn:aws:s3:::airflow-logs-{args[0]}",
                                    f"arn:aws:s3:::airflow-logs-{args[0]}/*",
                                    f"arn:aws:s3:::patch-baseline-snapshot-{args[3]}/*",  # noqa: E501
                                    f"arn:aws:s3:::aws-ssm-{args[3]}/*"
                                ]
                        },
                        {
                            "Sid": "ecrAccess",
                            "Effect": "Allow",
                            "Action": [
                                "ecr:*",
                                "cloudtrail:LookupEvents"
                            ],
                            "Resource": "*"
                        }
                    ]
                }),
            )
            # opts=ResourceOptions(parent=self),
        )

        self.lambda_logs = aws.iam.RolePolicyAttachment(
            "lambdaLogs",
            role=self.lambda_exec.name,
            policy_arn=lambda_logging.arn,
            opts=ResourceOptions(parent=self),
        )

        self.lambda_secrets = aws.iam.RolePolicyAttachment(
            "lambdaSecrets",
            role=self.lambda_exec.name,
            policy_arn=lambda_retrieve_secrets.arn,
            opts=ResourceOptions(parent=self),
        )

        self.lambda_vpc_access = aws.iam.RolePolicyAttachment(
            "lambdaVpcAccess",
            role=self.lambda_exec.name,
            policy_arn="arn:aws:iam::aws:policy/"
            + "service-role/AWSLambdaVPCAccessExecutionRole",
            opts=ResourceOptions(parent=self),
        )

        self.register_outputs({})
