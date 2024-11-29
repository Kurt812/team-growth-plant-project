read -p "Enter the repository name: " REPOSITORY_NAME
source .env
docker build --file pipeline/minute_pipeline_dockerfile -t team_growth_pipeline:v1.0 . --platform "linux/amd64" 
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.eu-west-2.amazonaws.com
if [[ $1 = "new" ]]; then
    echo "Creating a new repository: $REPOSITORY_NAME"
    aws ecr create-repository --repository-name "$REPOSITORY_NAME" --region eu-west-2
fi
docker tag team_growth_pipeline:v1.0 $ACCOUNT_ID.dkr.ecr.eu-west-2.amazonaws.com/$REPOSITORY_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.eu-west-2.amazonaws.com/$REPOSITORY_NAME:latest
