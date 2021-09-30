from pulumi_policy import (
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
    StackValidationArgs,
    StackValidationPolicy,
)
import re


def ec2_iam_profile_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches EC2 instances and checks, that
    IAM instance profile have expected value.
    """
    if args.resource_type == "aws:ec2/instance:Instance":
        if not re.search(
            r"projectname-[a-z0-9]{8}-instance_profile", args.props["iamInstanceProfile"]
        ):
            report_violation(
                "You tried to set unexpected instance profile: " +
                f"{args.props['iamInstanceProfile']}")


ec2_iam_profile = ResourceValidationPolicy(
    name="ec2-iam-profile",
    description="Unexpected IAM instance profile for EC2",
    validate=ec2_iam_profile_validator,
)


def ec2_instance_type_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches EC2 instance and checks, that
    instance type have expected value.
    """
    if args.resource_type == "aws:ec2/instance:Instance":
        allowed_types = ["t2.small", "t2.medium", "t2.large"]
        if args.props["instanceType"] not in allowed_types:
            report_violation(
                "You tried to set unexpected instance type: " +
                f"'{args.props['instanceType']}'" +
                "\nExpected value is one from next types:\n\t" +
                "\n\t-".join(map(str, allowed_types)))


ec2_instance_type = ResourceValidationPolicy(
    name="ec2-instance-type",
    description="Unexpected value for EC2 instance type",
    validate=ec2_instance_type_validator,
)


def ec2_public_ip_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches EC2 instances and checks, that
    instance have associated public IP address.
    """
    if args.resource_type == "aws:ec2/instance:Instance":
        if args.props["associatePublicIpAddress"] is not True:
            report_violation(
                "You didn't set associated public IP address for EC2" +
                "\nChange value to 'True'")


ec2_public_ip = ResourceValidationPolicy(
    name="ec2-public-ip",
    description="Unexpected value for associated public IP address for EC2",
    validate=ec2_public_ip_validator,
)


def ec2_ebs_encrypted_validator(
    args: StackValidationArgs, report_violation: ReportViolation
):
    """
    This function matches EC2 instances and checks, that
    all EBS (root and other) encrypted.
    """
    ec2_instances = filter(
        lambda r: r.resource_type == "aws:ec2/instance:Instance", args.resources)
    for instance in ec2_instances:
        if instance.props['rootBlockDevice']['encrypted'] is not True:
            report_violation(
                "You didn't set encryption for root EBS" +
                "\nChange value to 'True'")
        for ebs in instance.props['ebsBlockDevices']:
            if ebs['encrypted'] is not True:
                report_violation(
                    "You didn't set encryption for EBS" +
                    "\nChange value to 'True'")


ec2_ebs_encrypted = StackValidationPolicy(
    name="ec2-ebs-encrypted",
    description="Unexpected value for encrypted parameter for EBS in EC2",
    validate=ec2_ebs_encrypted_validator,
)
