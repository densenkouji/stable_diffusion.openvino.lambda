#!/bin/sh
LAMBDANAME=
REPOSITORYNAME=
REGION=$(aws configure get region)
ACCOUNTID=$(aws sts get-caller-identity --output text --query Account)

aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com
docker build --target production -t ${REPOSITORYNAME} .
docker tag ${REPOSITORYNAME}:latest ${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORYNAME}:latest
docker push ${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORYNAME}:latest
DIGEST=$(aws ecr list-images --repository-name ${REPOSITORYNAME} --out text --query 'imageIds[?imageTag==`latest`].imageDigest')
aws lambda update-function-code --function-name ${LAMBDANAME} --output text --image-uri ${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORYNAME}@${DIGEST}
