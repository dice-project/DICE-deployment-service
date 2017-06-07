# Setting up Cloudify manager

In this document we will describe specifics of bootstrap procedure for Cloudify
3.4.2 on FCO, EC2 and OpenStack. The document is based on the
[official instructions](#official-documentation).

1. [Creating bootstrap environment](#creating-bootstrap-environment)
1. [Preparing platform infrastructure](#preparing-platform-infrastructure)
    1. [FCO](#fco)
    1. [EC2](#ec2)
    1. [OpenStack](#openstack)
1. [Installing Cloudify resources](#installing-cloudify-resources)
1. [Creating server certificate](#creating-server-certificate)
1. [Executing bootstrap](#executing-bootstrap)
1. [Testing installation](#testing-installation)
1. [Granting access to the Cloudify Manager](#granting-access-to-the-cloudify-manager)
1. [Removing installation](#removing-installation)
1. [Official documentation](#official-documentation)


## Creating bootstrap environment

When we perform Cloudify Manager bootstrap, we will need some scratch space to
install required clients and configuration files. We can create new folder and
create python's virtual environment using next couple of commands:

    $ mkdir ~/cfy-manager && cd ~/cfy-manager
    $ virtualenv -p python2 venv
    $ . venv/bin/activate

In this documentation, we will also assume that DICE Deployment Service
sources are available at `~/dds`. Adjust commands accordingly or create a
symbolic link to make your life a bit easier:

    $ ln -s /path/to/dice/deployment/service/sources ~/dds

This being out of the way, we can start preparing our platform.


## Preparing platform infrastructure

What we need to prepare before we can bootstrap the Cloudify manager depends
on the platform being used. Next couple of sections provide detailed
instructions for all supported platforms.


### FCO

**TODO:** Prepare script for FCO.


### EC2

Preparing infrastructure on Amazon EC2 is automated using
`~/dds/install/aws-prepare.sh` script. Before we can use this script, we must
install AWS command line client by running:

    $ pip install awscli

Now that we have client installed, we must create API user that Cloudify and
tool will use to create required resources. Navigate to your
[AWS IAM console](https://console.aws.amazon.com/iam/) and create new user
with programmatic access. Make sure this user can use EC2 services. You can
use policy similar to the one shown below:

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "Stmt1488457587000",
          "Effect": "Allow",
          "Action": [ "ec2:*" ],
          "Resource": [ "*" ]
        }
      ]
    }

After new user is created, write down both access keys that are shown.

Next, we must prepare configuration for the preparation script. The simplest
thing to do is to copy `~/dds/install/aws-config.inc.sh` file from deployment
service sources to working directory and edit it:

    $ cp ~/dds/install/aws-config.inc.sh .
    $ $EDITOR aws-config.inc.sh

Note that there are default values listed for most of the configuration, so to
get things up and running, we only need to supply EC2 credentials. After the
edits are done, configuration file should look something like this:

    export AWS_SUBNET_CIDR=10.50.51.0/24
    export AWS_KEY_NAME=cloudify-manager-key
    export AWS_MANAGER_GROUP_NAME=cloudify-manager-grp
    export AWS_DEFAULT_GROUP_NAME=cloudify-default-grp
    export AWS_AMI_ID=ami-061b1560
    export AWS_INSTANCE_TYPE=m3.medium
    export AWS_DEFAULT_REGION=eu-west-1
    export AWS_ACCESS_KEY_ID=my.access.key.id
    export AWS_SECRET_ACCESS_KEY=secret.access.key
    export AWS_ACTIVATE_SWAP=false

Now we can test the configuration by running:

    $ . aws-config.inc.sh
    $ aws ec2 describe-vpcs
    {
      "Vpcs": [
        {
          "VpcId": "vpc-f2952897",
          "InstanceTenancy": "default",
          "State": "available",
          "DhcpOptionsId": "dopt-480dec2d",
          "CidrBlock": "172.30.0.0/16",
          "IsDefault": true
        }
      ]
    }

Note that in your output, the list of Vpcs might be empty, i.e., `"Vpcs" = []`,
but that is also a valid result.

If the configuration has been done properly, we should see something similar
to the output above. Now we can run the preparation script:

    $ ~/dds/install/aws-prepare.sh
    Creating VPC ...
    Creating subnet ...
    Creating gateway ...
    Attaching gateway ...
    Setting up route table ...
    Creating SSH key ...
    Creating default security group ...
    Creating manager security group ...
    Creating manager instance ...
    Adding elastic IP to manager ...
    Waiting for instance to start accepting ssh connections ...
      Attempt 0 ... failed. Retrying in 10 seconds.
      Attempt 1 ... failed. Retrying in 10 seconds.
      Attempt 2 ... failed. Retrying in 10 seconds.
      Attempt 3 ...
    Creating DICE plugin configuration ...
    Uploading DICE configuration to manager VM ...
    dice-aws.yaml                              100%  293     0.7KB/s   00:00
    cloudify-manager-key.pem                   100% 1671    39.0KB/s   00:00
    Creating bootstrap inputs template ...
    Creating cfy environment file ...
    ------------------------------------------------------------------------
    SUMMARY:
      Manager VM public address: 52.50.134.253
      Manager VM private address: 10.50.51.83
      SSH access to VM: ssh -i cloudify-manager-key.pem centos@52.50.134.253
    ------------------------------------------------------------------------

When the script terminates, summary section will contain some information,
relevant to the bootstrap procedure. Additionally, preparation script also
created an environment templates for Cloudify's command line client configuration
`cloudify.inc.sh` and bootstrap inputs that we will both use later on. And
lastly, configuration, needed by the DICE TOSCA Library has also been copied to
the manager instance for us.


### OpenStack

**TODO:** Prepare similar script as for EC2.


## Installing Cloudify resources

First we need to install prerequisites for Cloudify's CLI client. For Red Hat
related GNU/Linux distributions, following packages need to be installed:
`python-virtualenv`, `python-devel` and `openssl-devel`. Adjust properly for
Ubuntu and the gang.

After this is done, we can install client using pip:

    $ pip install cloudify==3.4.2

Next, we need to obtain official blueprints for manager and checkout the
**3.4.2** tag:

    $ git clone https://github.com/cloudify-cosmo/cloudify-manager-blueprints
    $ cd cloudify-manager-blueprints
    $ git checkout -b v3.4.2 tags/3.4.2

With blueprints present locally, we can install dependencies that are required
by manager blueprint. We do this by executing

    $ cfy init
    $ cfy local install-plugins -p simple-manager-blueprint.yaml

In order to prevent `requests` experiencing a fit when confronted with some
certificates, we reinstall them using `security` flag:

    $ pip install -U requests[security]

We can move to the server certificate creation now.


## Creating server certificate

Instructions on how to create server certificate are out of scope for this
document. If you need help with this, consult
[certificate instructions](certificates.md#creating-self-signed-certificates).

After certificate is ready, place it (along with generated key) into
`resources/ssl` folder and change their names to `server.crt` and `server.key`
respectively. Now we can proceed to actually executing bootstrap procedure.


## Executing bootstrap

Since we enabled security options in blueprint, we need to export some
environment variables that will inform cfy command about various settings that
we used. After this is done, we can bootstrap the manager. Commands that
perform all described actions are:

    $ . ../cloudify.inc.sh
    $ cfy bootstrap -p simple-manager-blueprint.yaml -i ../inputs.yaml

Note that installation step may take up to 30 minutes on a slow platform,
but in most cases, it should finish in no more than 15 minutes.


## Testing installation

First thing we can do is execute `cfy status`. Output of that command should
be similar to this:

    Getting management services status... [ip=109.231.122.46]
    Services:
    +--------------------------------+---------+
    |            service             |  status |
    +--------------------------------+---------+
    | InfluxDB                       | running |
    | Celery Management              | running |
    | Logstash                       | running |
    | RabbitMQ                       | running |
    | AMQP InfluxDB                  | running |
    | Manager Rest-Service           | running |
    | Cloudify UI                    | running |
    | Webserver                      | running |
    | Riemann                        | running |
    | Elasticsearch                  | running |
    +--------------------------------+---------+

Another way to test if manager is working is to point our web browser to
server's IP address, where we should be greeted by Cloudify's UI.


## Granting access to the Cloudify Manager

In order for our users to be able to use installed manager, we need to give
them next pieces of information:

1.  manager's IP address (address of the server we created),
2.  content of the `cloudify.inc.sh` file and
3.  SSL certificate that was uploaded to the server.

Users can now access manager by installing Cloudify command-line tool (`cfy`),
modifying certificate path in `cloudify.inc.sh` and executing:

    $ cfy init
    $ . cloudify.inc.sh
    $ cfy use -t manager_ip_address --port 443


## Removing installation

To remove all resources created during bootstrap, execute:

    $ . aws-config.inc.sh
    $ ~/dds/install/aws-teardown.sh # for AWS
    $ ~/dds/install/fco-teardown.sh # for FCO
    $ ~/dds/install/openstack-teardown.sh # for OpenStack

This will remove all traces of Cloudify manager from selected platform. Note
that you should execute uninstall workflow on all blueprints before removing
the manager, since tear-down procedure will not clean up resources created
during blueprint deployments.


## Official documentation

For further reference, the following links point to the official documentation:

* [How to bootstrap Cloudify Manager v.3.4.2](http://docs.getcloudify.org/3.4.2/manager/bootstrapping/)