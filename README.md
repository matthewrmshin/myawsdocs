<p>
  <a href="https://github.com/matthewrmshin/myawsdocs/actions"><img alt="GitHub Actions status" src="https://github.com/matthewrmshin/myawsdocs/workflows/Python%20application/badge.svg"></a>
</p>

# What is this?

I am trying to document some of my set up while experimenting with AWS.

# Getting Started

The `requirements.yml` file is for creating a Conda environment that allows me
to access AWS functionalities on my Linux environment at work.

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
   if you have not already done so.
2. Clone this repository or download a tree.
3. Change directory to the source tree you have just cloned or downloaded.
4. Run `conda env create`.
5. Run `conda activate aws-access`.
6. Type `aws` to test that you have access to the `aws` command.
7. Type `python3 -c 'import boto3"` to test that you can import `boto3`.
8. Follow the instructions at
   [Configure the AWS CLI](https://docs.aws.amazon.com/en_pv/cli/latest/userguide/cli-chap-configure.html)
   to set up a profile. When prompted for a region, use `eu-west-2`
   which is *EU (London)* if you live in the UK.

## Running JULES as an AWS Lambda

See https://github.com/matthewrmshin/lambda-jules for detail.
