from pulumi_policy import (
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)


def s3_no_public_read_validator(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    if args.resource_type == "aws:s3/bucket:Bucket" and \
                             "acl" in args.props:
        acl = args.props["acl"]
        if acl == "public-read" or acl == "public-read-write":
            report_violation(
                "You cannot set public-read or public-read-write on an bucket")


s3_no_public_read = ResourceValidationPolicy(
    name="s3-no-public-read",
    description="Prohibits setting the publicRead or publicReadWrite",
    validate=s3_no_public_read_validator,
)


def s3_logging_enabled(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    if args.resource_type == "aws:s3/bucket:Bucket":
        if "loggings" not in args.props:
            report_violation("You need to set logging on S3")


s3_logging_enabled = ResourceValidationPolicy(
    name="s3-no-logging-enabled",
    description="Set logging on S3.",
    validate=s3_logging_enabled,
)


def s3_bucket_versioning_enabled(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    if args.resource_type == "aws:s3/bucket:Bucket":
        if args.props["versioning"] is None or \
           args.props['versioning']['enabled'] is False:
            report_violation("You need to enable versioning.")


s3_bucket_versioning_enabled = ResourceValidationPolicy(
    name="bucket-versioning",
    description="Object versioning must be enabled",
    validate=s3_bucket_versioning_enabled,
)


def s3_bucket_encryption_enabled(
    args: ResourceValidationArgs, report_violation: ReportViolation
):
    if args.resource_type == "aws:s3/bucket:Bucket" and \
                              "serverSideEncryptionConfiguration" \
                              not in args.props:
        report_violation("Server-side encryption must be enabled.")


s3_bucket_encryption_enabled = ResourceValidationPolicy(
    name="bucket-encryption",
    description="Server-side encryption with KMS must be enabled.",
    validate=s3_bucket_encryption_enabled,
)
