from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws
import json


class VpcEndpointsArgs:
    """Create class VpcEndpointsArgs for conveniently
       passing arguments to the class VpcEndpoints.
       These arguments are used for configuration VPC Endpoints:
       - region - specify region in which you want create
       - project_name - project name
       - vpc_id - id of VPC in which you want to allocate EC2
       - ec2_security_group_id - id of EC2 security group for EC2
       - ec2_instance_subnet_id - id of subnet in which you allocated EC2
       - aws_public_route_table_id - id of public route table"""

    def __init__(
        self,
        region,
        project_name,
        vpc_id,
        ec2_security_group_id,
        ec2_instance_subnet_id,
        aws_public_route_table_id,
    ):

        self.region = region
        self.project_name = project_name
        self.vpc_id = vpc_id
        self.ec2_security_group_id = ec2_security_group_id
        self.ec2_instance_subnet_id = ec2_instance_subnet_id
        self.aws_public_route_table_id = aws_public_route_table_id


class VpcEndpoints(ComponentResource):
    """Create class VpcEndpoints which extends class ComponentResource"""

    def __init__(self, name: str, args: VpcEndpointsArgs, opts: ResourceOptions = None):
        """Create constructor of class VpcEndpoints, which creates VPC Endpoints for
           Elastic Container Registry. Amazon ECR needs three VPC endpoints to
           function correctly, as follows:

           - сom.amazonaws.<region>.ecr.api – this VPC endpoint is used
           for calls to the AWS API for Amazon ECR .

           - com.amazonaws.<region>.ecr.dkr – this VPC endpoint is used
           for the Docker Registry API.

           - com.amazonaws.<region>.s3 – because Amazon ECR uses Amazon S3
           to store image layers, an S3 endpoint is required in order to
           download the actual container images.

           You can connect directly to Secrets Manager through a private
           endpoint, for this purpose you mast create secrets manager
           endpoint  com.amazonaws.<region>.secretsmanager"""

        super().__init__("custom:resource:VpcEndpoints", name, {}, opts)
        """Override ComponentResource class constructor"""

        cr_api_endpoint = aws.ec2.VpcEndpoint(
            "ecrApiEndpoint",
            vpc_id=args.vpc_id,
            service_name=f"com.amazonaws.{args.region}.ecr.api",
            vpc_endpoint_type="Interface",
            security_group_ids=[args.ec2_security_group_id],
            subnet_ids=[args.ec2_instance_subnet_id],
            private_dns_enabled=True,
            opts=ResourceOptions(parent=self),
        )

        ecr_dkr_endpoint = aws.ec2.VpcEndpoint(
            "ecrDkrEndpoint",
            vpc_id=args.vpc_id,
            service_name=f"com.amazonaws.{args.region}.ecr.dkr",
            vpc_endpoint_type="Interface",
            security_group_ids=[args.ec2_security_group_id],
            subnet_ids=[args.ec2_instance_subnet_id],
            private_dns_enabled=True,
            opts=ResourceOptions(parent=self),
        )

        secrets_manager_endpoint = aws.ec2.VpcEndpoint(
            "secretsManagerEndpoint",
            vpc_id=args.vpc_id,
            service_name=f"com.amazonaws.{args.region}.secretsmanager",
            vpc_endpoint_type="Interface",
            security_group_ids=[args.ec2_security_group_id],
            subnet_ids=[args.ec2_instance_subnet_id],
            private_dns_enabled=True,
            opts=ResourceOptions(parent=self),
        )

        self.s3_endpoint = aws.ec2.VpcEndpoint(
            "s3Endpoint",
            vpc_id=args.vpc_id,
            service_name=f"com.amazonaws.{args.region}.s3",
            route_table_ids=[args.aws_public_route_table_id],
            policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "logs-bucket-access",
                            "Principal": "*",
                            "Action": "*",
                            "Effect": "Allow",
                            "Resource": [
                                "arn:aws:s3:::" + args.project_name + "-airflow-logs",
                                "arn:aws:s3:::" + args.project_name + "-airflow-logs/*",
                                "arn:aws:s3:::" + args.project_name + "-data",
                                "arn:aws:s3:::" + args.project_name + "-data/*",
                            ],
                        },
                        {
                            "Sid": "ecr-s3-access",
                            "Principal": "*",
                            "Action": ["s3:GetObject", "s3:PutObject"],
                            "Effect": "Allow",
                            "Resource": [
                                "arn:aws:s3:::prod-"
                                + args.project_name
                                + "-starport-layer-bucket/*"
                            ],
                        },
                        {
                            "Sid": "ssm-s3-access",
                            "Principal": "*",
                            "Action": "*",
                            "Effect": "Allow",
                            "Resource": [
                                "arn:aws:s3:::patch-baseline-snapshot-"
                                + args.project_name
                                + "/*",
                                "arn:aws:s3:::aws-ssm-" + args.project_name + "/*",
                            ],
                        },
                        {
                            "Sid": "yum-access",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "*",
                            "Resource": [
                                "arn:aws:s3:::amazonlinux."
                                + args.project_name
                                + ".amazonaws.com",
                                "arn:aws:s3:::amazonlinux."
                                + args.project_name
                                + ".amazonaws.com/*",
                            ],
                        },
                    ],
                }
            ),
            opts=ResourceOptions(parent=self),
        )

        self.register_outputs({})
