# What is this?

I am trying to document some of my set up while experimenting with AWS.

# Locations

## conda-aws-access

In this folder is a `requirements.yml` file for creating a Conda
environment that allows me to access AWS functionalities on my Linux
environment at work.

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
   if required.
2. Download the `conda-aws-access/requirements.yml` file.
3. Change directory to where the `requirements.yml` file is saved.
4. Run `conda env create`.
5. Run `conda activate aws-access`.
6. Type `aws` to test that you have access to the `aws` command.
7. Type `python3 -c 'import boto3"` to test that you can import `boto3`.

## docker-gfortran-fcm-make-netcdf

In this folder is a `Dockerfile` that documents how to create an environment on
Amazon Linux 2 to compile [JULES](https://jules.jchmr.org/)
with [netCDF](https://www.unidata.ucar.edu/software/netcdf/).
You can use the `Dockerfile` to build an image that installs:
* `gfortran`
* `fcm make`
* Compatible versions of `netcdf-c` and `netcdf-fortran`.

> Alternatively, you can set up an AWS EC2 instance running Amazon Linux 2,
> and roughly follow the instruction of the `Dockerfile` to create a suitable
> environment. (I'll see if this can be done via AWS Cloudformation in the future.)

To use the docker image. You will need to be in an environment that can run
[Docker](https://www.docker.com/). The easiest way is to use an Amazon EC2
instance by following the instructions:
* [Setting Up with Amazon EC2](https://docs.aws.amazon.com/en_pv/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html)
* [Getting Started with Amazon EC2 Linux Instances](https://docs.aws.amazon.com/en_pv/AWSEC2/latest/UserGuide/EC2_GetStarted.html)
* [Docker Basics for Amazon ECS](https://docs.aws.amazon.com/en_pv/AmazonECS/latest/developerguide/docker-basics.html)

Once you are set up, build the docker image:
1. Copy/Download the `Dockerfile` to a suitable folder. Change directory to it.
2. Run `docker build -t myfortran .`, (note the `.` at the end of the command.)

Get JULES, export a suitable source tree from
[MOSRS](https://code.metoffice.gov.uk/). (Account required.)
1. Run `svn pget fcm:revision https://code.metoffice.gov.uk/svn/jules/main`
   to find out the revision numbers of release versions or just go for trunk@HEAD.
2. Run, for example, `svn export fcm:revision https://code.metoffice.gov.uk/svn/jules/main/trunk@15927 jules-5.6` to get a source tree for vn5.6.

Build JULES:
1. Change directory to the source tree. E.g. run `cd jules-5.6`.
2. Run the docker image, binding `$PWD` into a volume in the container. E.g.:

```sh
docker run --rm -t -i -v $PWD:/opt/jules-5.5 myfortran env \
    JULES_PLATFORM=vm \
    JULES_NETCDF=netcdf \
    JULES_NETCDF_INC_PATH=/usr/local/include \
    JULES_NETCDF_LIB_PATH=/usr/local/lib \
    fcm make -C /opt/jules-5.5 -f etc/fcm-make/make.cfg
```

The executables should be located under `./build/bin/`.

## lambda-sample

(NOT FULLY TESTED.)

This folder contains logic and templates to use Cloudformation to set up (and
tear down) a sample lambda function from my Linux environment at work.

The sample lambda is a Python function that prints the ingested event to the log.
It is set up to run every 5 minutes with a cron event.

To use:
1. Set up your environment using the `conda-aws-access` instruction above.
3. Run `python3 -m moppa.cloudformation.main validate` to validate the templates.
3. Run `python3 -m moppa.cloudformation.main setup` to setup.
4. Run `python3 -m moppa.cloudformation.main setup` to teardown.

## What's Next?

I'll experiment with packaging up an AWS Lambda function to run a Fortran
executable with a Python wrapper.
