from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
)
import policies.api_gateway_security as agw
import policies.s3_security as s3
import policies.iam as iam
import policies.rds as rds
import policies.ec2 as ec2
import policies.vpc as vpc
import policies.vpc_endpoints as vpce
import policies.secrets_manager as sm
import policies.security_groups as sg
PolicyPack(
    name="PolicyPack",
    enforcement_level=EnforcementLevel.MANDATORY,
    policies=[
        agw.apigw_cache_cluster_enabled,
        agw.apigw_endpoint_configuration,
        agw.apigw_cloudwatch_alarms,
        agw.apigw_access_log_settings,
        s3.s3_no_public_read,
        s3.s3_logging_enabled,
        s3.s3_bucket_versioning_enabled,
        s3.s3_bucket_encryption_enabled,
        sg.rules_no_unexpected_ports,
        sg.rules_no_all_allow_cidr,
        sg.db_no_public_sg,
        iam.role_assume_policy,
        iam.vpc_flow_log_policy,
        iam.ec2_policy,
        iam.lambda_policy_attach,
        rds.rds_subnet,
        rds.rds_instance_class,
        rds.rds_publicity,
        rds.rds_encrypt,
        rds.rds_username,
        rds.rds_monitoring_enabled,
        rds.rds_backup_retention_enabled,
        rds.rds_multiAZ_enabled,
        rds.rds_logging_enabled,
        ec2.ec2_iam_profile,
        ec2.ec2_instance_type,
        ec2.ec2_public_ip,
        ec2.ec2_ebs_encrypted,
        vpc.subnets_belong_to_vpc,
        vpc.vpc_has_private_cidr,
        vpc.subnets_has_private_cidr,
        vpc.public_ip_on_lunch,
        vpc.dns_support_and_hostnames_enabled,
        vpc.route_gateway,
        vpce.vpce_private_dns_enabled,
        vpce.vpce_service_name,
        vpce.vpce_type,
        vpce.vpce_belong_to_vpc,
        sm.sm_rotation_enabled,
        sm.custom_kms_key_uses
    ],
)
