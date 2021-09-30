from pulumi_policy import (
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)
import re


def rules_no_unexpected_ports_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches Security group rules with values of parameters
    'toPort' and 'fromPort' and checks, that rules have expected values.
    """
    if args.resource_type == "aws:ec2/securityGroupRule:SecurityGroupRule":
        ports = [80, 443, 22, 5432, 587, 5555]
        if args.props["fromPort"] not in ports and args.props["toPort"] not in ports:
            report_violation(
                "You tried to set unexpected port for security group rule. " +
                "Expected values: 80, 443 (HTTP/HTTPS), 22 (SSH), " +
                "5432 (PostgreSQL), 587 (SMTP), 5555.")


rules_no_unexpected_ports = ResourceValidationPolicy(
    name="rules-no-unexpected-ports",
    description="Unexpected ports",
    validate=rules_no_unexpected_ports_validator,
)


def rules_no_all_allow_cidr_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches Security group rules with values of parameters
    'toPort' and 'cidrBlocks' and checks, that rules with value '22'
    for parameter 'toPort' don't have value in parameter 'cidrBlock'
    '0.0.0.0/0', which means allow traffic from all the Internet
    """
    if args.resource_type == "aws:ec2/securityGroupRule:SecurityGroupRule":
        if args.props["toPort"] == 22 and "0.0.0.0/0" in args.props["cidrBlocks"]:
            report_violation(
                "You tried to set access from all the Internet for SSH security " +
                "group rule. Set CIDR of you office or set your IP address."
            )


rules_no_all_allow_cidr = ResourceValidationPolicy(
    name="rules-no-all-allow-cidr",
    description="Unexpected CIDR block",
    validate=rules_no_all_allow_cidr_validator,
)


def db_no_public_sg_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches Security group rules with values of parameters
    'fromPort' and 'toPort'. Possible value is '5432' (default port for PostgreSQL);
    And then it checks parameter 'sourceSecurityId' that its value starts
    with 'sg-', which means allow traffic only from concrete security group
    """
    if args.resource_type == "aws:ec2/securityGroupRule:SecurityGroupRule":
        if args.props["toPort"] == 5432 and args.props["fromPort"] == 5432:
            if not re.match("sg-", args.props["sourceSecurityGroupId"]):
                report_violation(
                    "You tried to set access for DB " +
                    "security group not from security group"
                )


db_no_public_sg = ResourceValidationPolicy(
    name="db-no-public-sg",
    description="Unexpected source security group id for the rule",
    validate=db_no_public_sg_validator,
)
