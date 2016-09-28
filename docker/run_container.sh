#!/bin/bash
# This script corresponds to the following  version
VERSION="1.1.0-1"

function usage {
    echo "Version: $VERSION"
    echo "USAGE:"
    echo "./run_container.sh [ -p (y)|n ] IMAGE_NAME"
    echo ""
    echo "    -p y: the script will pull the image from a registry."
    echo "       n: the script will omit the docker pull command,"
    echo "          used to run an instance of a local image."
    echo "    -h:   Displays the message."
    exit
}

# Check arguement/option number is 1 or 3
if [ $# -ne 1 ] && [ $# -ne 3 ]
then
    usage
fi

# Process options
while getopts "hp:" OPT; do
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
       ?)
           usage
       ;;
    esac
done

# Set defaults
if [ -z $PULL]
then
    PULL="y"
fi

shift "$((OPTIND-1))" # Shift off the options and optional.

# Set arguements
if [ $# -ne 1 ]
then
    usage
fi

IMAGE_NAME=$1
echo "This script will deploy the containers for INDIGO-DataCloud Accounting, using $IMAGE_NAME."
echo "Deploying $IMAGE_NAME with run_container.sh ($VERSION)."

# If -p y, or if -p was ommited
if [ "$PULL" == "y" ]
then
    echo "Pulling image: $IMAGE_NAME"
    docker pull $IMAGE_NAME
else
    echo "Using local image: $IMAGE_NAME"
fi

echo "Deploying Database"

# The database root password.
# NEEDS POPULATING
MYSQL_ROOT_PASSWORD=

# Create an APEL user
# Do not change
MYSQL_USER="apel"

# The password for the APEL user.
# Can be overidden
MYSQL_PASSWORD="${MYSQL_ROOT_PASSWORD}APEL"

# The name of the database used to store accounting data  
# Can be overidden
MYSQL_DATABASE="apel_rest"

docker run -v /var/lib/mysql --name apel-mysql -p 3306:3306 -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -e "MYSQL_DATABASE=$MYSQL_DATABASE" -e "MYSQL_USER=$MYSQL_USER" -e "MYSQL_PASSWORD=$MYSQL_PASSWORD" -d mysql:5.6

#wait for apel-mysql to configure
sleep 30

# Create schema
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud.sql`"

# Partition tables
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud-extra.sql`"

echo "Done"

echo "Deploying APEL Server"

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

docker run -d --link apel-mysql:mysql -p 80:80 -p 443:443 -e "MYSQL_PASSWORD=$MYSQL_PASSWORD" -e "ALLOWED_FOR_GET=$ALLOWED_FOR_GET" -e "SERVER_IAM_ID=$SERVER_IAM_ID" -e "SERVER_IAM_SECRET=$SERVER_IAM_SECRET" -e "DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY" $IMAGE_NAME

# this allows the APEL REST interface to configure
sleep 60
echo "Done!"
