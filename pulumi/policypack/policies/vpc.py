from pulumi_policy import (
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
    StackValidationArgs,
    StackValidationPolicy
)
import re


def subnets_belong_to_vpc_validator(
    args: StackValidationArgs, report_violation: ReportViolation
):
    """
    This function matches subnets and checks, that
    they belong to one VPC.
    """
    vpcs = filter(lambda r: r.resource_type == "aws:ec2/vpc:Vpc", args.resources)
    vpcs_ids = [vpc.props['id'] for vpc in vpcs]
    subnets = filter(
        lambda r: r.resource_type == "aws:ec2/subnet:Subnet", args.resources)
    for subnet in subnets:
        if subnet.props["vpcId"] not in vpcs_ids:
            report_violation("You tried to set unexpected VPC id for subnet: " +
                             f"'{subnet.props['tags']['Name']}'")


subnets_belong_to_vpc = StackValidationPolicy(
    name="subnets-belong-to-vpc",
    description="Unexpected VPC id for subnet",
    validate=subnets_belong_to_vpc_validator,
)


def subnets_has_private_cidr_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches subnets and checks, that
    they have private CIDR block.
    """
    private_set = re.compile(r'^(10\.)|^(172\.)|(^192\.168\.)')
    if args.resource_type == "aws:ec2/subnet:Subnet":
        if not re.search(private_set, args.props["cidrBlock"]):
            report_violation("You tried to set public CIDR for subnet: " +
                             f"'{args.props['tags']['Name']}'" +
                             "\nPlease, set private CIDR.")


subnets_has_private_cidr = ResourceValidationPolicy(
    name="subnets-has-private-cidr",
    description="Unexpected CIDR block for subnet",
    validate=subnets_has_private_cidr_validator,
)


def vpc_has_private_cidr_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches VPCs and checks, that
    they have private CIDR block.
    """
    private_set = re.compile(
        r'^(10\.)|^(172\.1[6-9]\.)|^(172\.2[0-9]\.)|^(172\.3[0-1]\.)|^(192\.168\.)')
    if args.resource_type == "aws:ec2/vpc:Vpc":
        if not re.search(private_set, args.props["cidrBlock"]):
            report_violation("You tried to set public CIDR for VPC: " +
                             f"'{args.props['tags']['Name']}'" +
                             "\nPlease, set private CIDR.")


vpc_has_private_cidr = ResourceValidationPolicy(
    name="vpc-has-private-cidr",
    description="Unexpected CIDR block for VPC",
    validate=vpc_has_private_cidr_validator,
)


def public_ip_on_lunch_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches subnets and checks, that
    they assign public IP for instances on launch.
    """
    if args.resource_type == "aws:ec2/subnet:Subnet":
        if args.props["mapPublicIpOnLaunch"] is not True:
            report_violation("You didn't set assignment public IP for instances on" +
                             f"launch in the subnet: '{args.props['tags']['Name']}'" +
                             "\nChange value to True.")


public_ip_on_lunch = ResourceValidationPolicy(
    name="public-ip-on-lunch",
    description="Unexpected value for 'mapPublicIpOnLaunch'",
    validate=public_ip_on_lunch_validator,
)


def dns_support_and_hostnames_enabled_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    """
    This function matches VPCs and checks, that
    DNS hostnames and supports is enabled for VPCs.
    """
    if args.resource_type == "aws:ec2/vpc:Vpc":
        if args.props["enableDnsHostnames"] is not True:
            report_violation("You didn't enable DNS hostnames for VPC: " +
                             f"'{args.props['tags']['Name']}'" +
                             "\nChange value to True.")
        if args.props["enableDnsSupport"] is not True:
            report_violation("You didn't enable DNS support for VPC: " +
                             f"'{args.props['tags']['Name']}'" +
                             "\nChange value to True.")


dns_support_and_hostnames_enabled = ResourceValidationPolicy(
    name="dns-support-and-hostnames-enabled",
    description="Unexpected value for DNS hostnames and support",
    validate=dns_support_and_hostnames_enabled_validator,
)


def route_gateway_validator(
    args: StackValidationArgs, report_violation: ReportViolation
):
    """
    This function matches Routes and checks, that
    they have attached internet gateway.
    """
    routes = filter(lambda r: r.resource_type == "aws:ec2/route:Route", args.resources)
    gateways = filter(
        lambda r: r.resource_type == "aws:ec2/internetGateway:InternetGateway",
        args.resources)
    gateways_ids = [gateway.props['id'] for gateway in gateways]
    for route in routes:
        if route.props["gatewayId"] not in gateways_ids:
            report_violation(
                "You tried to set unexpected Internet Gateway id for Route")


route_gateway = StackValidationPolicy(
    name="route-gateway",
    description="Unexpected Internet Gateway id for Route",
    validate=route_gateway_validator,
)
