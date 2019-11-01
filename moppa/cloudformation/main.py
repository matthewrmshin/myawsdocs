# -----------------------------------------------------------------------------
# Copyright (C) British Crown (Met Office) & Contributors
# -----------------------------------------------------------------------------
"""Utility to create/remove postprocessing applications on AWS."""
import json
import logging
from pathlib import Path
from shutil import make_archive
from subprocess import run
import sys
from tempfile import TemporaryDirectory

import boto3
import botocore
import click


logging.basicConfig(
    datefmt='%Y%m%dT%H%M%S%z',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
    stream=sys.stderr,
)
LOG = logging.getLogger()


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
    StackMgr(ctx.obj.get('profile')).setup()


@cli.command('teardown')
@click.pass_context
def cli_teardown(ctx):
    """CLI: Remove the deployed stacks."""
    StackMgr(ctx.obj.get('profile')).teardown()


@cli.command('validate')
@click.pass_context
def cli_validate(ctx):
    """CLI: Validate the cloudformation templates."""
    StackMgr(ctx.obj.get('profile')).validate()


class StackMgr():
    """Manage cloudformation stacks."""

    SOURCE_PACKAGES_STACK = 'source-packages'
    LAMBDA_STACK = 'lambda-sample'
    STACKS = (
        SOURCE_PACKAGES_STACK,
        LAMBDA_STACK,
    )

    def __init__(self, profile_name: str):
        self.session = boto3.Session(profile_name=profile_name)

    def create_stack(self, name: str):
        """Create a named cloudformation stack.

        Wait for creation to complete.
        """
        cfn_client = self.session.client('cloudformation')
        LOG.info('create stack: %s', name)
        cfn_client.create_stack(
            StackName=name,
            TemplateBody=open(self.get_template_path(name)).read(),
            Parameters=json.load(
                open(Path(__file__).parent.joinpath('service-meta.json'))
            ),
            Capabilities=['CAPABILITY_IAM'],
        )
        cfn_client.get_waiter('stack_create_complete').wait(StackName=name)
        LOG.info('create stack done: %s', name)

    def delete_stack(self, name: str):
        """Delete a named cloudformation stack.

        Wait for deletion to complete.
        """
        cfn_client = self.session.client('cloudformation')
        LOG.info('delete stack: %s', name)
        cfn_client.delete_stack(StackName=name)
        cfn_client.get_waiter('stack_delete_complete').wait(StackName=name)
        LOG.info('delete stack done: %s', name)

    def get_lambda_bucket_name(self) -> str:
        """Return name of S3 bucket hosting lambda code."""
        cfn_client = self.session.client('cloudformation')
        resources = cfn_client.describe_stack_resources(
            StackName=self.SOURCE_PACKAGES_STACK)
        return resources['StackResources'][0]['PhysicalResourceId']

    @staticmethod
    def get_template_path(name: str) -> str:
        """Return the path to a cloudformation template.

        FIXME: We are making an assumption that of the locations of the
               templates are *.yaml files relative to this script.
               This should be reviewed.
        """
        return str(Path(__file__).parent.joinpath(name).with_suffix('.yaml'))

    def remove_lambda_bucket(self):
        """Remove a bucket and its contents."""
        bucket = self.session.resource('s3').Bucket(
            self.get_lambda_bucket_name())
        bucket.objects.delete()
        bucket.delete()
        bucket.wait_until_not_exists()

    def setup(self):
        """Create the cloudformation stacks.

        Create the stacks. Subscribe to ServiceHub.
        """
        self.validate()
        self.upload()
        # Deploy lambda stack
        self.create_stack(self.LAMBDA_STACK)

    def teardown(self):
        """Delete the cloudformation stacks."""
        self.delete_stack(self.LAMBDA_STACK)
        self.remove_lambda_bucket()
        self.delete_stack(self.SOURCE_PACKAGES_STACK)

    def upload(self):
        """Create lambda package and upload."""
        tempdir = TemporaryDirectory()
        tempname = Path(tempdir.name).joinpath('moppa-services')
        make_archive(
            str(tempname),
            'zip',
            Path(__file__).parent.parent.parent,
            'moppa/services')
        try:
            bucket_name = self.get_lambda_bucket_name()
        except botocore.exceptions.ClientError as exc:
            if LOG.isEnabledFor(logging.DEBUG):
                LOG.exception(exc)
            self.create_stack(self.SOURCE_PACKAGES_STACK)
            bucket_name = self.get_lambda_bucket_name()
        # pylint: disable=E1101
        bucket = self.session.resource('s3').Bucket(bucket_name)
        bucket.upload_file(
            str(tempname.with_suffix('.zip')), 'moppa-services.zip')
        tempdir.cleanup()

    def validate(self):
        """Find and lint cloudformation templates.

        Assuming that the linter is doing its job, we should not need to call
        "aws cloudformation validate-template" as well.
        """
        cfn_client = self.session.client('cloudformation')
        for name in self.STACKS:
            templ = self.get_template_path(name)
            LOG.info('validate %s', templ)
            run(['cfn-lint', templ], check=True)
            cfn_client.validate_template(TemplateBody=open(templ).read())


if __name__ == '__main__':
    # pylint: disable=E1120
    cli()
