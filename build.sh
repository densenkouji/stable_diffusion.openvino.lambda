#!/bin/sh
RESULT=$(aws lambda list-functions --query 'Functions[].[ FunctionName ]' --output table)
if [ $# = 0 ]; then
    echo "Argument is required. Input Lambda Function Name."
    echo "$RESULT"
    exit
elif [ ! "`echo $RESULT | grep $1`" ]; then
    echo "Input Lambda Function Name."
    echo "$RESULT"
    exit
fi

LAMBDANAME=$1
REPOSITORYNAME=$(echo "$LAMBDANAME-repo" | tr 'A-Z' 'a-z')
REGION=$(aws configure get region)
ACCOUNTID=$(aws sts get-caller-identity --output text --query Account)

aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com
docker build --target production -t ${REPOSITORYNAME} .
# docker build -f ./Dockerfile.waifu --target production -t ${REPOSITORYNAME} .
docker tag ${REPOSITORYNAME}:latest ${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORYNAME}:latest
docker push ${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORYNAME}:latest
DIGEST=$(aws ecr list-images --repository-name ${REPOSITORYNAME} --out text --query 'imageIds[?imageTag==`latest`].imageDigest')
aws lambda update-function-code --function-name ${LAMBDANAME} --output text --image-uri ${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORYNAME}@${DIGEST}
