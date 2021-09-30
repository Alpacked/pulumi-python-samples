from pulumi import ResourceOptions, export, Config
import pulumi_random as random
import pulumi_aws as aws
import vpc
import iam
import security_groups
import ec2
import vpc_endpoints
import rds
import secrets_manager
import lambda_functions
import api_gateway
import s3
import presets

config = Config()
data = config.require_object("data")
current = aws.get_caller_identity()
project_name_underscores = data["project_name"].replace("-", "_")


presets.checks(data["region"], data["project_name"])
private_key = presets.create_repo_and_add_deploy_key(
    data["region"],
    data["project_name"],
    data["path_for_keypair"])

random_suffix = random.RandomString(
    "random",
    length=8,
    upper=False,
    special=False
)


vpc = vpc.Vpc(
    "vpc",
    vpc.VpcArgs(
        region=data["region"],
        flow_log_cloudwatch_log_group_name_prefix=data[
            "flow_log_cloudwatch_log_group_name_prefix"
        ],
        flow_log_destination_type=data["flow_log_destination_type"],
        flow_log_max_aggregation_interval=data[
            "flow_log_max_aggregation_interval"
        ],
        flow_log_traffic_type=data["flow_log_traffic_type"],
        flow_log_log_format=data["flow_log_log_format"],
        flow_log_cloudwatch_log_group_retention_in_days=data[
            "flow_log_cloudwatch_log_group_retention_in_days"
        ],
        flow_log_cloudwatch_log_group_kms_key_id=data[
            "flow_log_cloudwatch_log_group_kms_key_id"
        ],
        create_db_subnets=data["create_db_subnets"],
        enable_dns_support=data["enable_dns_support"],
        enable_dns_hostnames=data["enable_dns_hostnames"],
        vpc_cidr_block=data["vpc_cidr_block"],
        public_subnets_cidr=data["public_subnets_cidr"],
        db_subnets_cidr=data["db_subnets_cidr"],
        name_suffix=random_suffix.result
    ),
)

security_groups = security_groups.SecurityGroups(
    "security_groups",
    security_groups.SecurityGroupsArgs(
        region=data["region"],
        billing_code=data["billing_code"],
        project_name_underscores=project_name_underscores,
        vpc_id=vpc.monitoring_deployment_vpc.id,
        ingress_ec2_rule_ports=data["ingress_ec2_rule_ports"],
        egress_ec2_rule_ports=data["egress_ec2_rule_ports"],
        rule_cidr_blocks=data["rule_cidr_blocks"]
    ),
    opts=ResourceOptions(depends_on=[vpc]),
)

iam = iam.Iam(
    "iam",
    iam.IamArgs(
        region=data["region"],
        aws_account_id=current.account_id,
        project_name_underscores=project_name_underscores,
        name_suffix=random_suffix.result
    ),
    opts=ResourceOptions(depends_on=[security_groups]),
)

rds = rds.Rds(
    "rds",
    rds.RdsArgs(
        region=data["region"],
        billing_code=data["billing_code"],
        project_name=data["project_name"],
        project_name_underscores=project_name_underscores,
        db_instance_type=data["db_instance_type"],
        db_subnet_group_name=vpc.default_subnet_group.name,
        db_security_group_id=security_groups.db_security_group.id,
        db_username=data["db_username"],
        name_suffix=random_suffix.result
    ),
    opts=ResourceOptions(depends_on=[iam]),
)

db_secrets_manager = secrets_manager.DBSecretsManager(
    "db_secrets_manager",
    secrets_manager.DBSecretsManagerArgs(
        billing_code=data["billing_code"],
        project_name=data["project_name"],
        db_username=data["db_username"],
        db_password_result=rds.db_password.result,
        address=rds.default.address,
    ),
    opts=ResourceOptions(depends_on=[rds]),
)

if data["create_lambda_and_apigateway"] is True:
    lambdas = lambda_functions.Lambda(
        "lambda",
        lambda_functions.LambdaArgs(
            billing_code=data["billing_code"],
            ec2_security_group_id=security_groups.ec2_security_group.id,
            project_name_underscores=project_name_underscores,
            db_username_secret_arn=db_secrets_manager.db_username_secret.arn,
            db_password_secret_arn=db_secrets_manager.db_password_secret.arn,
            db_address_secret_arn=db_secrets_manager.db_address_secret.arn,
            lambda_exec_arn=iam.lambda_exec.arn,
            ec2_subnet_id=vpc.ec2_subnet_id.results[0],
        ),
        opts=ResourceOptions(depends_on=[rds]),
    )

    api_gateway = api_gateway.ApiGateway(
        "api_gateway",
        api_gateway.ApiGatewayArgs(
            project_name_underscores=project_name_underscores,
            lambda_get_function_name=lambdas.get_function.name,
            lambda_post_function_name=lambdas.post_function.name,
            lambda_get_function_invoke_arn=lambdas.get_function.invoke_arn,
            lambda_post_function_invoke_arn=lambdas.post_function.invoke_arn
        ),
        opts=ResourceOptions(depends_on=[lambdas]),
    )

ec2 = ec2.Ec2(
    "ec2",
    ec2.Ec2Args(
        region=data["region"],
        billing_code=data["billing_code"],
        project_name_underscores=project_name_underscores,
        vpc_id=vpc.monitoring_deployment_vpc.id,
        aws_account_id=current.account_id,
        repo_deploy_key=data["repo_deploy_key"],
        ec2_instance_type=data["ec2_instance_type"],
        ec2_security_group_id=security_groups.ec2_security_group.id,
        ec2_role_name=iam.ec2_role.name,
        ec2_subnet_id=vpc.ec2_subnet_id.results[0],
        iam_instance_profile_name=iam.default.name,
        default_rest_api_id=api_gateway.default_rest_api.id
    ),
    opts=ResourceOptions(),
)

vpc_endpoints = vpc_endpoints.VpcEndpoints(
    "vpc_endpoints",
    vpc_endpoints.VpcEndpointsArgs(
        region=data["region"],
        project_name=data["project_name"],
        vpc_id=vpc.monitoring_deployment_vpc.id,
        ec2_security_group_id=security_groups.ec2_security_group.id,
        ec2_instance_subnet_id=ec2.default.subnet_id,
        aws_public_route_table_id=vpc.public_route_table.id,
    ),
    opts=ResourceOptions(depends_on=[ec2]),
)

s3_airflow_logs_bucket = s3.S3(
    "airflow_logs_bucket",
    s3.S3Args(
        billing_code=data["billing_code"],
        project_name=project_name_underscores,
        admin_list=["pulumi-github"],
        vpc_endpoint_id=vpc_endpoints.s3_endpoint.id,
        ec2_role_arn=iam.ec2_role.arn,
        bucket_name="airflow-logs",
        name_suffix=random_suffix.result,
    ),
    opts=ResourceOptions(depends_on=[vpc_endpoints, iam]),
)

s3_datalake_bucket = s3.S3(
    "datalake_bucket",
    s3.S3Args(
        billing_code=data["billing_code"],
        project_name=project_name_underscores,
        admin_list=["pulumi-github"],
        vpc_endpoint_id=vpc_endpoints.s3_endpoint.id,
        ec2_role_arn=iam.ec2_role.arn,
        bucket_name="datalake",
        name_suffix=random_suffix.result,
    ),
    opts=ResourceOptions(depends_on=[vpc_endpoints, iam]),
)

secrets_manager = secrets_manager.SecretsManager(
    "secrets_manager",
    secrets_manager.SecretsManagerArgs(
        billing_code=data["billing_code"],
        project_name=data["project_name"],
        project_name_underscores=project_name_underscores,
        airflow_pass_result=ec2.airflow_pass.result,
        airflow_bucket_name=s3_airflow_logs_bucket.bucket.id,
        datalake_bucket_name=s3_datalake_bucket.bucket.id,
    ),
    opts=ResourceOptions(depends_on=[vpc_endpoints, ec2, rds]),
)
if data["create_lambda_and_apigateway"] is True:
    export("ApiGateway", api_gateway.default_deployment.invoke_url)
export("ec2_public_ip", ec2.default.public_ip)
export("db_endpoint", rds.default.address)
export("db_username", rds.default.username)
export("db_password", rds.db_password.result)
