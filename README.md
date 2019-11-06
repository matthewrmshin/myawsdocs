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

## Building Fortran executable for AWS Lambda

Current efforts documented in these projects:
* [lambda-gfortran-fcm-make-netcdf](https://github.com/matthewrmshin/lambda-gfortran-fcm-make-netcdf)
  Dockerfile based on AWS Lambda Python 3.7 runtime environment,
  with GFortran, FCM Make and netCDF libraries.

Note: To use the docker image. You will need to be in an environment that can run
[Docker](https://www.docker.com/). The easiest way is to use an Amazon EC2
instance by following the instructions:
* [Setting Up with Amazon EC2](https://docs.aws.amazon.com/en_pv/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html)
* [Getting Started with Amazon EC2 Linux Instances](https://docs.aws.amazon.com/en_pv/AWSEC2/latest/UserGuide/EC2_GetStarted.html)
* [Docker Basics for Amazon ECS](https://docs.aws.amazon.com/en_pv/AmazonECS/latest/developerguide/docker-basics.html)

## Building JULES executable for AWS Lambda

Get JULES, export a suitable source tree from
[MOSRS](https://code.metoffice.gov.uk/). (Account required.)
1. Run `svn pget fcm:revision https://code.metoffice.gov.uk/svn/jules/main`
   to find out the revision numbers of release versions or just go for trunk@HEAD.
2. Run, for example, `svn export fcm:revision https://code.metoffice.gov.uk/svn/jules/main/trunk@15927 jules-5.6` to get a source tree for vn5.6.

Build JULES:
1. Change directory to the source tree. E.g. run `cd jules-5.6`.
2. Run the docker image, binding `$PWD` into a volume in the container. E.g.:

```sh
docker run --rm -t -i -v "$PWD:/opt/jules-5.6" 'lambda-gfortran-fcm-make-netcdf' \
    env \
    JULES_PLATFORM=custom \
    JULES_NETCDF=netcdf \
    JULES_NETCDF_PATH=/var/task \
    fcm make -C /opt/jules-5.6 -f etc/fcm-make/make.cfg
```

The JULES executable should be located under `./build/bin/jules.exe`.

To package things up...
* (Hopefully, a more automated way will follow.)
* Create a new directory. Change directory to it.
  E.g. `mkdir 'package'; pushd 'package'`.
* Copy the shared libraries out of the docker image into `./lib/`.
  E.g. `mkdir 'lib'; docker run --rm -t -i -v "$PWD:/tmp/package" 'lambda-gfortran-fcm-make-netcdf' cp -r '/var/task/lib' '/tmp/package/'`.
* Copy `jules.exe` file to `./bin/`.
* Add some runtime configuration, e.g. namelists to the package if appropriate.
* Add a Python module with a lambda handler function. It should do:
  * Invoke `/var/task/bin/jules.exe` with `subprocess.run` or otherwise.
  * Turn event + input into input to the JULES executable.
  * Send output from the JULES executable to a suitable location.
  * (Example to follow.)
* Review the content. Remove anything unnecessary.
* Create a zip file with content of the current directory.
* Deploy the package.

## Lambda Deployment with Cloudformation

(Should use SAM when it becomes feasible.)

(NOT FULLY TESTED.)

This repository contains logic and templates to use Cloudformation to set up (and
tear down) sample lambda functions from my Linux environment at work.

The `moppa/cloudformation/lambda-sample.yaml` stack deploys a Python function
that prints the ingested event to the log.  It is set up to run every 5 minutes
with a cron event.

The `moppa/cloudformation/lambda-fortwrap.yaml` stack deploys a Python function
to wrap a Fortran binary. The Fortran binary needs to be statically built for
Amazon Linux. This still require work to automate.

To use (in theory):
1. Set up your environment using the `conda-aws-access` instruction above.
3. Run `python3 -m moppa.cloudformation.main validate` to validate the templates.
3. Run `python3 -m moppa.cloudformation.main setup` to setup.
4. Run `python3 -m moppa.cloudformation.main setup` to teardown.

## What's Next?

Automate creating key-pair for accessing EC2 instance,
putting the private key in a common location in my Linux environment at work.

Fully automate JULES build on EC2 instance and deployment to lambda afterwards.

Experiment with running Fortran executables with inputs using a Python wrapper in a lambda.
The python wrapper should be able to generate some of the inputs going into the Fortran
executable. E.g.: It should inspect the event payload, and creating the correct input namelist
based on the values in the event payload.

Add automated tests for logic.
