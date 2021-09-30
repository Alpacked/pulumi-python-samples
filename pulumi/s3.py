import pulumi_aws as aws
from pulumi import ComponentResource, ResourceOptions, Output

current_id = aws.get_caller_identity().account_id


class S3Args:
    """Create class S3Args for conveniently passing
        arguments to the class S3. The following arguments
        are required:
        - project_name - name of the project
        - billing_code - billing code
        - admin_list - list of IAM users for admin access
        - vpc_endpoint_id - ID of S3 vpc endpoint
        - ec2_role_arn - arn of EC2 instance role
        - bucket_name - name that bucket will have
        - name_suffix - random suffix that will be used for s3
        bucket naming"""

    def __init__(
        self,
        project_name,
        billing_code,
        admin_list,
        vpc_endpoint_id,
        ec2_role_arn,
        bucket_name,
        name_suffix,
    ):

        self.project_name = project_name
        self.billing_code = billing_code
        self.admin_list = admin_list
        self.vpc_endpoint_id = vpc_endpoint_id
        self.ec2_role_arn = ec2_role_arn
        self.bucket_name = bucket_name
        self.name_suffix = name_suffix


class S3(ComponentResource):
    """Create class S3 which extends class ComponentResource"""

    def __init__(self, name: str, args: S3Args, opts: ResourceOptions = None):
        """Create constructor of class S3"""
        super().__init__("custom:resource:S3", name, {}, opts)
        """Override ComponentResource class constructor"""

        self.bucket_final = Output.all(
            args.project_name,
            args.bucket_name
            ).apply(
            lambda arg: f"{arg[0]}-{arg[1]}"
        )

        self.bucket = aws.s3.Bucket(
            args.bucket_name,
            bucket=self.bucket_final,
            acl="private",
            tags={
                "BillingCode": args.billing_code,
                "Name": self.bucket_final,
                "Project": args.project_name,
            },
            server_side_encryption_configuration={
                "rule": {
                    "applyServerSideEncryptionByDefault": {
                        "sseAlgorithm": "AES256",
                    },
                },
            },
            opts=ResourceOptions(parent=self)
        )

        self.deny_vpce_policy = Output.all(
            args.ec2_role_arn,
            self.bucket.arn,
            args.vpc_endpoint_id
            ).apply(
            lambda args:
            aws.iam.get_policy_document(
                version="2012-10-17",
                statements=[
                    aws.iam.GetPolicyDocumentStatementArgs(
                        sid="Access-to-specific-VPCE-only",
                        principals=[
                            aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                                identifiers=[args[0]],
                                type="AWS",
                            )
                        ],
                        actions=[
                            "s3:DeleteObject",
                            "s3:GetObject",
                            "s3:ListBucket",
                            "s3:PutObject",
                            "s3:RestoreObject",
                        ],
                        effect="Deny",
                        resources=[
                            args[1],
                            args[1]+"/*"
                        ],
                        conditions=[
                            aws.iam.GetPolicyDocumentStatementConditionArgs(
                                test="StringNotEquals",
                                values=[args[2]],
                                variable="aws:sourceVpce",
                            )
                        ],
                    )
                ],
                opts=ResourceOptions(parent=self.bucket)
            )
        )

        admin_principals = []
        for admin in args.admin_list:
            admin_principals.append(f"arn:aws:iam::{current_id}:user/{admin}")

        self.admin_access_policy = Output.all(self.bucket.arn).apply(
            lambda args:
            aws.iam.get_policy_document(
                version="2012-10-17",
                statements=[
                    aws.iam.GetPolicyDocumentStatementArgs(
                        sid="admin-access",
                        principals=[
                            aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                                identifiers=admin_principals,
                                type="AWS",
                            )
                        ],
                        actions=["s3:*"],
                        effect="Allow",
                        resources=[
                            args[0],
                            args[0]+"/*"
                        ],
                    )
                ],
                opts=ResourceOptions(parent=self.bucket)
            )
        )

        self.policy = aws.s3.BucketPolicy(
            f'{args.bucket_name}-policy',
            bucket=self.bucket.id,
            policy=aws.iam.get_policy_document(
                source_json=self.deny_vpce_policy.json,
                override_json=self.admin_access_policy.json,
                ).json,
            opts=ResourceOptions(parent=self.bucket)
        )

        self.register_outputs({})
