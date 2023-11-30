#!/bin/bash
set -e

export AWS_PROFILE=transitmatters
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
export AWS_PAGER=""

if [[ -z "$DD_API_KEY" ]]; then
    echo "Must provide DD_API_KEY in environment to deploy" 1>&2
    exit 1
fi

STACK_NAME="walkscore-proxy-stack"

timestamp=$(date +%s)
zip_name="deployment-$timestamp.zip"

# Identify the version and commit of the current deploy
GIT_VERSION=`git describe --tags --always`
GIT_SHA=`git rev-parse HEAD`
echo "Deploying version $GIT_VERSION | $GIT_SHA"

# Adding some datadog tags to get better data
DD_TAGS="git.commit.sha:$GIT_SHA,git.repository_url:github.com/transitmatters/walkscore-proxy"

poetry export --output requirements.txt --without-hashes
pushd server/
pip3 install -r ../requirements.txt --only-binary=:all: --platform manylinux2014_x86_64 --implementation cp --abi cp311 --target ./package --upgrade

# Reduce size of deployment https://stackoverflow.com/a/69355796
find ./package -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

pushd ./package && zip -r ../../$zip_name . && popd
pushd .. && zip -gr $zip_name resources/* && popd
zip -gr ../$zip_name *.py
popd

aws s3 cp ./$zip_name s3://tm-walkscore-proxy-deploy/$zip_name

aws cloudformation deploy --stack-name $STACK_NAME \
  --template-file deploy/cf.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset \
  --parameter-overrides S3Key=$zip_name DDApiKey=$DD_API_KEY GitVersion=$GIT_VERSION DDTags=$DD_TAGS

rm -r ./$zip_name
