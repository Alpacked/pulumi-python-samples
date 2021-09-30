from pulumi import ComponentResource, ResourceOptions, Output
import pulumi_aws as aws
import pulumi_random as random


class RdsArgs:
    """Create class RdsArgs for conveniently passing arguments to the class Rds.
        This arguments make RDS module to be more flexible. You can pass
        different arguments values for 'db_instance_type',
        'db_subnet_group_name', 'db_security_group_id',
        that's make RDS more flexible and configurable:
        - region - specify region in which you want create
        - billing_code - billing code
        - project_name - project name
        - project_name_underscores - modified project name
        - db_instance_type - type of database instance
        - db_username - username for database
        - db_subnet_group_name - database subnet group in which
            you want to allocate RDS
        - db_security_group_id - id of database security group for RDS
        - name_suffix - random string that is added to all resources
        in the stack to avoid name duplication"""

    def __init__(
        self,
        region,
        billing_code,
        project_name,
        project_name_underscores,
        db_instance_type,
        db_subnet_group_name,
        db_security_group_id,
        db_username,
        name_suffix
    ):

        self.region = region
        self.billing_code = billing_code
        self.project_name = project_name
        self.project_name_underscores = project_name_underscores
        self.db_instance_type = db_instance_type
        self.db_subnet_group_name = db_subnet_group_name
        self.db_security_group_id = db_security_group_id
        self.db_username = db_username
        self.name_suffix = name_suffix


class Rds(ComponentResource):
    """Create class Rds which extends class ComponentResource
    """

    def __init__(self, name: str, args: RdsArgs, opts: ResourceOptions = None):
        """Create constructor of class Rds
           This constructor creates RDS instance, and two RandomPassword:
           one for database and second for airflow.."""
        super().__init__("custom:resource:Rds", name, {}, opts)
        """Override ComponentResource class constructor"""

        self.db_password = random.RandomPassword(
            "dbPassword",
            length=12,
            special=False,
            opts=ResourceOptions(parent=self),
        )

        self.default = aws.rds.Instance(
            "default",
            allocated_storage=10,  # must be 100
            storage_type="gp2",
            engine="postgres",
            engine_version="12.5",
            instance_class=args.db_instance_type,
            db_subnet_group_name=args.db_subnet_group_name.apply(
                lambda name: f"{name}"),
            backup_retention_period=7,
            identifier=Output.all(args.project_name, args.name_suffix).apply(
                lambda args: f"{args[0]}-{args[1]}"),
            final_snapshot_identifier=Output.all(
                args.project_name,
                args.name_suffix
                ).apply(
                    lambda args: f"{args[0]}-final-snapshot-{args[1]}"),
            storage_encrypted=True,
            vpc_security_group_ids=[args.db_security_group_id],
            username=args.db_username,
            password=self.db_password.result,
            port=5432,
            tags={
                "BillingCode": args.billing_code,
                "Name": f"{args.project_name_underscores}_db_server",
                "Project": args.project_name_underscores,
            },
            opts=ResourceOptions(parent=self),
        )

        self.register_outputs({})
