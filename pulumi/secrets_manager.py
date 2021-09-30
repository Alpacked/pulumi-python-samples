from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws
import json

# TODO rewrite into dynamic creation of secret + secretVersion
# so we don't specify all secrets in the object


class SecretsManagerArgs:
    """Create class SecretsManagerArgs for conveniently
       passing arguments to the class SecretsManager:
       - billing_code - billing code
       - project_name - project name
       - project_name_underscores - modified project name
       - airflow_pass_result - password for airflow
       - airflow_bucket_name - name of airflow bucket
       - datalake_bucket_name - name of datalake bucket"""

    def __init__(
        self,
        billing_code,
        project_name,
        project_name_underscores,
        airflow_pass_result,
        airflow_bucket_name,
        datalake_bucket_name
    ):

        self.billing_code = billing_code
        self.project_name = project_name
        self.project_name_underscores = project_name_underscores
        self.airflow_pass_result = airflow_pass_result
        self.airflow_bucket_name = airflow_bucket_name
        self.datalake_bucket_name = datalake_bucket_name


class SecretsManager(ComponentResource):
    """Create class SecretsManager which extends class ComponentResource"""

    def __init__(
        self, name: str, args: SecretsManagerArgs, opts: ResourceOptions = None
    ):
        """Create constructor of class SecretsManager"""
        super().__init__("custom:resource:SecretsManager", name, {}, opts)
        """Override ComponentResource class constructor"""

        # TO DO: class must be a constructor for secret and secret version,
        # and their values must be passed as arguments

        airflow_logs_bucket_secret = aws.secretsmanager.Secret(
            f"{args.project_name}_airflowLogsBucketSecret",
            # name=f"{args.project_name_underscores}_airflow_logs_bucket",
            tags={
                "BillingCode": args.billing_code,
                "Name": f"{args.project_name}_airflowLogsBucketSecret",
                "Project": args.project_name,
            },
            opts=ResourceOptions(parent=self),
        )

        data_lake_bucket_secret = aws.secretsmanager.Secret(
            f"{args.project_name}_dataLakeBucketSecret",
            # name=f"{args.project_name_underscores}_data_lake_bucket",
            tags={
                "BillingCode": args.billing_code,
                "Name": f"{args.project_name}_dataLakeBucketSecret",
                "Project": args.project_name,
            },
            opts=ResourceOptions(parent=self),
        )

        airflow_user_secret = aws.secretsmanager.Secret(
            f"{args.project_name}_airflowUserSecret",
            # name=f"{args.project_name_underscores}_airflow_user",
            tags={
                "BillingCode": args.billing_code,
                "Name": f"{args.project_name}_airflowUserSecret",
                "Project": args.project_name,
            },
            opts=ResourceOptions(parent=self),
        )

        airflow_logs_bucket_secret = aws.secretsmanager.SecretVersion(
            f"{args.project_name}_airflowLogsBucketSecret",
            secret_id=airflow_logs_bucket_secret.id,
            secret_string=args.airflow_bucket_name.apply(
                lambda arg: arg
            ),
            opts=ResourceOptions(parent=airflow_logs_bucket_secret),
        )

        data_lake_bucket_secret = aws.secretsmanager.SecretVersion(
            f"{args.project_name}_dataLakeBucketSecret",
            secret_id=data_lake_bucket_secret.id,
            secret_string=args.datalake_bucket_name.apply(
                lambda arg: arg
            ),
            opts=ResourceOptions(parent=data_lake_bucket_secret),
        )

        airflow_user_secret = aws.secretsmanager.SecretVersion(
            f"{args.project_name}_airflowUserSecret",
            secret_id=airflow_user_secret.id,
            secret_string=args.airflow_pass_result.apply(
                lambda result: json.dumps(
                    {
                        "airflow_username": "admin",
                        "airflow_password": result
                    }
                )
            ),
            opts=ResourceOptions(parent=airflow_user_secret),
        )

        self.register_outputs({})


class DBSecretsManagerArgs:
    """Create class SecretsManagerArgs for conveniently
       passing arguments to the class DBSecretsManager:
       - billing_code - billing code
       - project_name - project name
       - project_name_underscores - modified project name
       - db_username - username for database
       - db_password_result - password for database
       - address - database endpoint URL address"""

    def __init__(
        self,
        billing_code,
        project_name,
        db_username,
        db_password_result,
        address
    ):

        self.billing_code = billing_code
        self.project_name = project_name
        self.db_username = db_username
        self.db_password_result = db_password_result
        self.address = address


class DBSecretsManager(ComponentResource):
    """Create class SecretsManager which extends class ComponentResource"""

    def __init__(
        self, name: str, args: DBSecretsManagerArgs, opts: ResourceOptions = None
    ):
        """Create constructor of class DBSecretsManager"""
        super().__init__("custom:resource:DBSecretsManager", name, {}, opts)
        """Override ComponentResource class constructor"""

        self.db_username_secret = aws.secretsmanager.Secret(
            f"{args.project_name}_dbSecret_username",
            tags={
                "BillingCode": args.billing_code,
                "Name": f"{args.project_name}_dbSecret_username",
                "Project": args.project_name,
            },
            opts=ResourceOptions(parent=self),
        )

        db_username_secret = aws.secretsmanager.SecretVersion(
            f"{args.project_name}_dbSecret_username",
            secret_id=self.db_username_secret.id,
            secret_string=args.db_username,
            opts=ResourceOptions(parent=self.db_username_secret),
        )

        self.db_password_secret = aws.secretsmanager.Secret(
            f"{args.project_name}_dbSecret_password",
            tags={
                "BillingCode": args.billing_code,
                "Name": f"{args.project_name}_dbSecret_password",
                "Project": args.project_name,
            },
            opts=ResourceOptions(parent=self),
        )

        db_password_secret = aws.secretsmanager.SecretVersion(
            f"{args.project_name}_dbSecret_password",
            secret_id=self.db_password_secret.id,
            secret_string=args.db_password_result,
            opts=ResourceOptions(parent=self.db_password_secret),
        )

        self.db_address_secret = aws.secretsmanager.Secret(
            f"{args.project_name}_dbSecret_address",
            tags={
                "BillingCode": args.billing_code,
                "Name": f"{args.project_name}_dbSecret_address",
                "Project": args.project_name,
            },
            opts=ResourceOptions(parent=self),
        )

        db_address_secret = aws.secretsmanager.SecretVersion(
            f"{args.project_name}_dbSecret",
            secret_id=self.db_address_secret.id,
            secret_string=args.address,
            opts=ResourceOptions(parent=self.db_address_secret),
        )

        self.register_outputs({})
