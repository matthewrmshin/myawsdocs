# -----------------------------------------------------------------------------
# Copyright (C) British Crown (Met Office) & Contributors
# -----------------------------------------------------------------------------
"""Utility to create/remove postprocessing applications on AWS."""
import json
import logging
from pathlib import Path
from shutil import make_archive
from subprocess import check_call
import sys
from tempfile import TemporaryDirectory

import boto3
import click


logging.basicConfig(
    datefmt='%Y%m%dT%H%M%S%z',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
    stream=sys.stderr,
)
S3_LAMBDA_STACK = 's3-lambda'
LAMBDA_STACK = 'lambda-sample'
STACKS = (
    S3_LAMBDA_STACK,
    LAMBDA_STACK,
)


@click.group()
@click.option('--profile', default='default')
@click.pass_context
def cli(ctx, profile):
    """Deploy/Remove stacks on AWS."""
    ctx.ensure_object(dict)
    ctx.obj['profile'] = profile


@cli.command('setup')
@click.pass_context
def cli_setup(ctx):
    """CLI: Create and deploy the stacks with cloudformation."""
    setup(ctx.obj.get('profile'))


@cli.command('teardown')
@click.pass_context
def cli_teardown(ctx):
    """CLI: Remove the deployed stacks."""
    teardown(ctx.obj.get('profile'))


@cli.command('validate')
def cli_validate():
    """CLI: Validate the cloudformation templates."""
    validate()


def create_stack(session: boto3.Session, name: str):
    """Create a named cloudformation stack. Wait for creation to complete."""
    cfn_client = session.client('cloudformation')
    cfn_client.create_stack(
        StackName=name,
        TemplateBody=open(get_template_path(name)).read(),
        Parameters=json.load(
            open(Path(__file__).parent.joinpath('service-meta.json'))
        ),
        Capabilities=['CAPABILITY_IAM'],
    )
    cfn_client.get_waiter('stack_create_complete').wait(StackName=name)


def delete_stack(session: boto3.Session, name: str):
    """Delete a named cloudformation stack. Wait for deletion to complete."""
    cfn_client = session.client('cloudformation')
    cfn_client.delete_stack(name)
    cfn_client.get_waiter('stack_delete_complete').wait(StackName=name)


def get_lambda_bucket_name(session) -> str:
    """Return name of S3 bucket hosting lambda code."""
    cfn_client = session.client('cloudformation')
    resources = cfn_client.describe_stack_resources(StackName=S3_LAMBDA_STACK)
    return resources[0]['PhysicalResourceId']


def get_template_path(name: str) -> str:
    """Return the path to a cloudformation template.

    FIXME: We are making an assumption that of the locations of the templates
           are *.yaml files relative to this script. This should be reviewed.
    """
    return str(Path(__file__).parent.joinpath(name).with_suffix('.yaml'))


def remove_lambda_bucket(session: boto3.Session):
    """Remove a bucket and its contents."""
    bucket = session.resource('s3').Bucket(get_lambda_bucket_name(session))
    bucket.objects.delete()
    bucket.delete()
    bucket.wait_until_not_exists()


def setup(profile_name: str):
    """Create the cloudformation stacks.

    Create the stacks. Subscribe to ServiceHub.
    """
    validate()
    session = boto3.Session(profile_name=profile_name)
    # Upload ingestion lambda function code
    create_stack(session, S3_LAMBDA_STACK)
    tempdir = TemporaryDirectory()
    tempname = Path(tempdir.name).joinpath('moppa-services')
    make_archive(
        str(tempname), 'zip', Path(__file__).parent.parent, 'moppa/services')
    # pylint: disable=E1101
    bucket = session.resource('s3').Bucket(get_lambda_bucket_name(session))
    bucket.upload_file(tempname.with_suffix('.zip'), 'moppa-services.zip')
    tempdir.cleanup()
    # Deploy lambda stack
    create_stack(session, LAMBDA_STACK)


def teardown(profile_name: str):
    """Delete the cloudformation stacks."""
    session = boto3.Session(profile_name=profile_name)
    remove_lambda_bucket(session)
    delete_stack(S3_LAMBDA_STACK)
    delete_stack(LAMBDA_STACK)


def validate():
    """Find and lint cloudformation templates.

    Assuming that the linter is doing its job, we should not need to call
    "aws cloudformation validate-template" as well.
    """
    check_call(['cfn-lint'] + [get_template_path(name) for name in STACKS])


if __name__ == '__main__':
    # pylint: disable=E1120
    cli()
