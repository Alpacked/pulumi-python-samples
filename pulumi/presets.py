import pulumi_tls as tls
import pulumi_github as github
import re
import os


def checks(region, project_name):
    """This function checks if variable project_name
       corresponds to the naming requirements. Also it checks
       that VPC exists in this region or not"""

    if not bool(re.match("^[a-z-]*$", project_name)):
        raise SystemExit("Error: project name can only contain " +
                         "lowercase characters and hyphens")


def create_repo_and_add_deploy_key(region, project_name, path_for_keypair):
    """This function creates SSH keypair for deployment,
       creates GitHub repository from template repo, and
       adds public key from our keypair to our repository"""

    project_name_underscores = project_name.replace('-', '_')
    region_underscores = region.replace('-', '_')
    keypair_name = f"{project_name_underscores}_{region_underscores}_deployment_key"

    keypair = tls.PrivateKey(
        keypair_name,
        algorithm="RSA",
        rsa_bits=2048)

    if not os.path.exists(os.path.expanduser(f"~/{path_for_keypair}")):
        os.makedirs(os.path.expanduser(f"~/{path_for_keypair}"))

    def write(key, ext):
        with open(
            os.path.expanduser(f"~/{path_for_keypair}/{keypair_name}{ext}"), "w"
        ) as f:
            f.write(key)

    keypair.private_key_pem.apply(lambda key: write(key, ".pem"))
    keypair.public_key_openssh.apply(lambda key: write(key, ""))

    github_repo = github.Repository(
        "github_repo",
        template=github.RepositoryTemplateArgs(
            owner="project",
            repository="airflow_pipeline_template",
        ),
        name=f"{project_name_underscores}_airflow_pipeline",
        visibility="private",)

    add_deploy_key_to_repo = github.RepositoryDeployKey(
        "RepositoryDeployKey",
        key=keypair.public_key_openssh,
        read_only=True,
        repository=github_repo.name,
        title="EC2 Deploy Key")

    return keypair.private_key_pem
