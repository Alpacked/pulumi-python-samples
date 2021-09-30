from pulumi import ComponentResource, ResourceOptions, FileArchive
import pulumi_aws as aws


class LambdaArgs:
    """Create class LambdaArgs for conveniently passing arguments to the class Lambda
       These arguments are used for configuration Lambdas functions:
       - billing_code - billing code
       - ec2_security_group_id - security group in which we create
       - project_name_underscores - modified project name
       - db_username_secret_arn - ARN of secret with db username
       - db_password_secret_arn - ARN of secret with db password
       - db_address_secret_arn - ARN of secret with db address
       - lambda_exec_arn - ARN of IAM role for lambda execution
       - ec2_subnet_id - subnet id in which EC2 is created"""

    def __init__(
        self,
        billing_code,
        ec2_security_group_id,
        project_name_underscores,
        db_username_secret_arn,
        db_password_secret_arn,
        db_address_secret_arn,
        lambda_exec_arn,
        ec2_subnet_id,
    ):

        self.billing_code = billing_code
        self.ec2_security_group_id = ec2_security_group_id
        self.project_name_underscores = project_name_underscores
        self.db_username_secret_arn = db_username_secret_arn
        self.db_password_secret_arn = db_password_secret_arn
        self.db_address_secret_arn = db_address_secret_arn
        self.lambda_exec_arn = lambda_exec_arn
        self.ec2_subnet_id = ec2_subnet_id


class Lambda(ComponentResource):
    """Create class Lambda which extends class ComponentResource"""

    def __init__(self, name: str, args: LambdaArgs, opts: ResourceOptions = None):
        """Create constructor of class Lambda
           This constructor creates two lambda functions:
           one for GET method and another for POST method"""
        super().__init__("custom:resource:Lambda", name, {}, opts)
        """Override ComponentResource class constructor"""

        file_archive = FileArchive("./lambda_dummy.zip")

        self.get_function = aws.lambda_.Function(
            "getMethodFunction",
            # name=f"{args.project_name_underscores}_get_method",
            code=file_archive,
            handler="get_method.main_handler",
            runtime="python3.7",
            timeout=20,
            role=args.lambda_exec_arn,
            tags={
                "BillingCode": args.billing_code,
            },
            vpc_config={
                "subnet_ids": [args.ec2_subnet_id],
                "security_group_ids": [args.ec2_security_group_id],
            },
            environment={
                "variables": {
                    "db_host": args.db_address_secret_arn,
                    "db_username": args.db_username_secret_arn,
                    "db_password": args.db_password_secret_arn,
                    "db_name": "production",
                    "db_port": "5432",
                },
            },
            opts=ResourceOptions(parent=self),
        )

        self.post_function = aws.lambda_.Function(
            "postMethodFunction",
            # name=f"{args.project_name_underscores}_post_method",
            code=file_archive,
            handler="post_method.main_handler",
            runtime="python3.7",
            timeout=20,
            role=args.lambda_exec_arn,
            tags={
                "BillingCode": args.billing_code,
            },
            vpc_config={
                "subnet_ids": [args.ec2_subnet_id],
                "security_group_ids": [args.ec2_security_group_id],
            },
            environment={
                "variables": {
                    "db_host": args.db_address_secret_arn,
                    "db_username": args.db_username_secret_arn,
                    "db_password": args.db_password_secret_arn,
                    "db_name": "production",
                    "db_port": "5432",
                },
            },
            opts=ResourceOptions(parent=self),
        )

        self.register_outputs({})
