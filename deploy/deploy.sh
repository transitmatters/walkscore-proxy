#!/bin/bash
set -e

export AWS_PROFILE=transitmatters
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
export AWS_PAGER=""

# Ensure required secrets are set
if [[ -z "$DD_API_KEY" || -z "$WALKSCORE_API_KEY" ]]; then
    echo "Must provide DD_API_KEY and WALKSCORE_API_KEY in environment to deploy" 1>&2
    exit 1
fi

# Setup environment stuff
CHALICE_STAGE="production"
BACKEND_ZONE="labs.transitmatters.org"
BACKEND_CERT_ARN="$TM_LABS_WILDCARD_CERT_ARN"
BACKEND_DOMAIN_PREFIX="walkscore."

# Fetch repository tags
git fetch --tags

# Identify the version and commit of the current deploy
GIT_VERSION=`git describe --always`
GIT_SHA=`git rev-parse HEAD`
echo "Deploying version $GIT_VERSION | $GIT_SHA"

# Adding some datadog tags to get better data
DD_TAGS="git.commit.sha:$GIT_SHA,git.repository_url:github.com/transitmatters/walkscore-proxy"

BACKEND_BUCKET=walkscore-proxy$ENV_SUFFIX
BACKEND_HOSTNAME=$BACKEND_DOMAIN_PREFIX$BACKEND_ZONE # Must match in .chalice/config.json!
CF_STACK_NAME=walkscore-proxy$ENV_SUFFIX

configurationArray=("$CHALICE_STAGE" "$BACKEND_BUCKET" "$CF_STACK_NAME" "$BACKEND_CERT_ARN")
for i in ${!configurationArray[@]}; do
    if [ -z "${configurationArray[$i]}" ]; then
        echo "Failed: index [$i] in configuration array is null or empty";
        exit;
    fi
done

echo "Starting $CHALICE_STAGE deployment"
echo "Backend bucket: $BACKEND_BUCKET"
echo "Backend hostname: $BACKEND_HOSTNAME"
echo "CloudFormation stack name: $CF_STACK_NAME"

pushd server/ > /dev/null
poetry export --without-hashes --output requirements.txt
poetry run chalice package --stage $CHALICE_STAGE --merge-template cloudformation.json cfn/
aws cloudformation package --template-file cfn/sam.json --s3-bucket $BACKEND_BUCKET --output-template-file cfn/packaged.yaml
aws cloudformation deploy --template-file cfn/packaged.yaml --stack-name $CF_STACK_NAME --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset \
    --tags service=walkscore-proxy env=prod \
    --parameter-overrides \
    TMBackendCertArn=$BACKEND_CERT_ARN \
    TMBackendHostname=$BACKEND_HOSTNAME \
    TMBackendZone=$BACKEND_ZONE \
    WalkscoreApiKey=$WALKSCORE_API_KEY \
    DDApiKey=$DD_API_KEY \
    GitVersion=$GIT_VERSION \
    DDTags=$DD_TAGS

popd > /dev/null

echo
echo
echo "Complete"
