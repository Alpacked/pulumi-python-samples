from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws
from jinja2 import Template
import pulumi_random as random


class Ec2Args:
    """Create class Ec2Args for conveniently passing arguments to the class Ec2
       These arguments are used to render the template and create EC2 instance
       - region - specify region in which you want create
       - aws_account_id - id of current aws account
       - project_name_underscores - modified project name
       - repo_deploy_key - private SSH key for EC2
       - billing_code - billing code
       - vpc_id - id of VPC in which you want to allocate EC2
       - ec2_instance_type - type of EC2 instance
       - ec2_security_group_id - id of EC2 security group for EC2
       - ec2_role_name - name of EC2 IAM role for EC2 instance
       - ec2_subnet_id - id of subnet in which you want to allocate EC2
       - iam_instance_profile_name - IAM instance profile for EC2
       - default_rest_api_id - id of REST API to fill template"""

    def __init__(
        self,
        region,
        aws_account_id,
        project_name_underscores,
        repo_deploy_key,
        billing_code,
        vpc_id,
        ec2_instance_type,
        ec2_security_group_id,
        ec2_role_name,
        ec2_subnet_id,
        iam_instance_profile_name,
        default_rest_api_id,
    ):

        self.region = region
        self.aws_account_id = aws_account_id
        self.project_name_underscores = project_name_underscores
        self.repo_deploy_key = repo_deploy_key
        self.billing_code = billing_code
        self.vpc_id = vpc_id
        self.ec2_instance_type = ec2_instance_type
        self.ec2_security_group_id = ec2_security_group_id
        self.ec2_role_name = ec2_role_name
        self.ec2_subnet_id = ec2_subnet_id
        self.iam_instance_profile_name = iam_instance_profile_name
        self.default_rest_api_id = default_rest_api_id


class Ec2(ComponentResource):
    """Create class Ec2 which extends class ComponentResource"""

    def __init__(self, name: str, args: Ec2Args, opts: ResourceOptions = None):
        """Create constructor of class Ec2
           This constructor render the template with variables, than chooses
           latest AMI for EC2 instance and then creates EC2 instance"""
        super().__init__("custom:resource:Ec2", name, {}, opts)
        """Override ComponentResource class constructor"""

        user_data_rendered = Template(open("bootstrap.tpl").read()).render(
            region=args.region,
            repo_name=f"{args.project_name_underscores}_airflow_pipeline",
            deploy_key=args.repo_deploy_key,
            project_name_underscores=args.project_name_underscores,
            aws_account_id=args.aws_account_id,
            api_endpoint=f"https://{args.default_rest_api_id}.execute-api.{args.region}. \
            amazonaws.com/prod/{args.project_name_underscores}"
        )

        amazon_linux2 = aws.ec2.get_ami(
            owners=["amazon"],
            filters=[
                {
                    "name": "owner-alias",
                    "values": ["amazon"],
                },
                {
                    "name": "name",
                    "values": ["amzn2-ami-hvm*"],
                },
            ],
            most_recent=True,
        )

        self.airflow_pass = random.RandomPassword(
            "airflowPass",
            length=12,
            special=False,
            opts=ResourceOptions(parent=self),
        )

        self.default = aws.ec2.Instance(
            "default",
            ami=amazon_linux2.id,
            associate_public_ip_address=True,
            instance_type=args.ec2_instance_type,
            # key_name=f"monitoring_deployments_{data['region']}"
            # .replace("-", "_"),
            # The line above will uncomment, when we create key pair
            vpc_security_group_ids=[args.ec2_security_group_id],
            subnet_id=args.ec2_subnet_id,
            iam_instance_profile=args.iam_instance_profile_name,
            user_data=user_data_rendered,
            tags={
                "BillingCode": args.billing_code,
                "Name": f"{args.project_name_underscores}_airflow_server",
                "Project": args.project_name_underscores,
            },
        )

        self.register_outputs({})
