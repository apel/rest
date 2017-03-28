#!/bin/bash
set -eu

############ MODIFY THESE VARIABLES ############# 

# The password for the APEL user.
# NEEDS POPULATING
# EVEN IF NOT RE-DEPLOYING A DATABASE
# As it is needed to access the deployed database
MYSQL_PASSWORD=

# A (python) list of IAM service IDs allowed to submit GET requests.
# This bash variable needs to be interpreted by python as a list of strings
# i.e. [\'ac2f23e0-8103-4581-8014-e0e82c486e36\']
# NEEDS POPULATING
ALLOWED_FOR_GET=

# An IAM ID corresponding to this instance, used to validate tokens.
# NEEDS POPULATING
SERVER_IAM_ID=

# An IAM secret corresponding to this instance, used to validate tokens.
# NEEDS POPULATING
SERVER_IAM_SECRET=

# The Django server requires its own "secret".
# NEDDS POPULATING
DJANGO_SECRET_KEY=

# The database root password.
# NEEDS POPULATING if and only if deploying database containers
MYSQL_ROOT_PASSWORD=

#################################################


# This script corresponds to the following  version
VERSION="1.2.1-1"

function usage {
    echo "Version: $VERSION"
    echo "USAGE:"
    echo "./run_container.sh [ -p (y)|n ] [ -d (y)|n ] IMAGE_NAME"
    echo ""
    echo "    -p y: Pull the image from a registry."
    echo "       n: Omit the docker pull command,"
    echo "          used to run an instance of a local image."
    echo "    -d y: Deploy the database container"
    echo "       n: Do not deploy the database container,"
    echo "          used when deploying an upgrade to the APEL Server container."
    echo "    -h:   Displays the message."
    exit
}

# Set defaults for options
PULL="y"
DATABASE="y"

# Process options
while getopts "d:hp:" OPT; do
    case $OPT in
       h) # Display the usage message
           usage
       ;;
       p) # Pull the docker image or use locally
           if [ "$OPTARG" == "y" ] || [ "$OPTARG" == "n" ]
           then
               PULL=$OPTARG
           else
               echo "Invalid -p arguement: $OPTARG"
               usage
           fi
       ;;
       d) # Deploy the database
           if [ "$OPTARG" == "y" ] || [ "$OPTARG" == "n" ]
           then
               DATABASE=$OPTARG
           else
               echo "Invalid -d arguement: $OPTARG"
               usage
           fi
       ;;
       ?)
           usage
       ;;
    esac
done

shift "$((OPTIND-1))" # Shift off the options and optional.

# Set arguements
if [ $# -ne 1 ]
then
    usage
fi

IMAGE_NAME=$1
echo "This script will deploy the containers for INDIGO-DataCloud Accounting"
echo "Deploying $IMAGE_NAME with run_container.sh ($VERSION)"

# If -p y, or if -p was ommited
if [ "$PULL" == "y" ]
then
    echo "Pulling image"
    docker pull $IMAGE_NAME
else
    echo "Using local image"
fi

if [ "$DATABASE" == "y" ]
then
    # Deploy the databbase
    echo "Deploying MySQL Container"

    docker run -v /var/lib/mysql:/var/lib/mysql --name apel-mysql -p 3306:3306 -v `pwd`/docker/etc/mysql/conf.d:/etc/mysql/conf.d -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -e "MYSQL_DATABASE=apel_rest" -e "MYSQL_USER=apel" -e "MYSQL_PASSWORD=$MYSQL_PASSWORD" -d mysql:5.6

    #wait for apel-mysql to configure
    sleep 60

    # Create schema
    docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud.sql`"

    # Partition tables
    docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud-extra.sql`"
    echo "MySQL Container deployed"
fi

echo "Deploying APEL Server Container"

docker run -d --link apel-mysql:mysql -p 80:80 -p 443:443 -v /var/spool/apel/cloud:/var/spool/apel/cloud -e "MYSQL_PASSWORD=$MYSQL_PASSWORD" -e "ALLOWED_FOR_GET=$ALLOWED_FOR_GET" -e "SERVER_IAM_ID=$SERVER_IAM_ID" -e "SERVER_IAM_SECRET=$SERVER_IAM_SECRET" -e "DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY" $IMAGE_NAME


# this allows the APEL REST interface to configure
sleep 60
echo "APEL Server Container deployed"
echo "Deployment complete!"
