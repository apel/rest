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
IMAGE_NAME=$1
if [ -z $IMAGE_NAME ]
then
    echo "No image provided."
    usage
fi

echo "This script will deploy the containers for INDIGO-DataCloud Accounting, using $IMAGE_NAME."
echo "Deploying $IMAGE_NAME with run_container.sh ($VERSION)."

# If -p y, or if -p was ommited
if [ "$PULL" == "y" ]
then
    docker pull $apel_rest_image
fi

echo "Configuring Database"

MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE="apel_rest"
MYSQL_USER="apel"
MYSQL_PASSWORD="${MYSQL_ROOT_PASSWORD}APEL"

docker run -v /var/lib/mysql --name apel-mysql -p 3306:3306 -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -e "MYSQL_DATABASE=$MYSQL_DATABASE" -e "MYSQL_USER=$MYSQL_USER" -e "MYSQL_PASSWORD=$MYSQL_PASSWORD" -d mysql:5.6

#wait for apel-mysql to configure
sleep 30

# Create schema
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud.sql`"

# Partition tables
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud-extra.sql`"

echo "Done"

echo "Configuring APEL Server"

ALLOWED_FOR_GET=
SERVER_IAM_ID=
SERVER_IAM_SECRET=
DJANGO_SECRET_KEY=

docker run -d --link apel-mysql:mysql -p 80:80 -p 443:443 -e "MYSQL_PASSWORD=$MYSQL_PASSWORD" -e "ALLOWED_FOR_GET=$ALLOWED_FOR_GET" -e "SERVER_IAM_ID=$SERVER_IAM_ID" -e "SERVER_IAM_SECRET=$SERVER_IAM_SECRET" -e "DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY" $apel_rest_image

# this allows the APEL REST interface to configure
sleep 60
echo "Done!"
