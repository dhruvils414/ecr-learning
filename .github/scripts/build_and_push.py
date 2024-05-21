import sys
import boto3
import docker

def build_and_push(project_name, repository_name, aws_account_id, aws_region):
    ecr_client = boto3.client('ecr', region_name=aws_region)
    docker_client = docker.from_env()

    # Build Docker image
    image_tag = 'latest'
    image, build_logs = docker_client.images.build(path=f'./{project_name}', tag=image_tag)
    for chunk in build_logs:
        if 'stream' in chunk:
            print(chunk['stream'].strip())

    # Tag Docker image
    repository_uri = f'{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{repository_name}'
    full_image_name = f'{repository_uri}:{image_tag}'
    image.tag(repository_uri, tag=image_tag)

    # Authenticate Docker to ECR
    auth_data = ecr_client.get_authorization_token()['authorizationData'][0]
    username, password = auth_data['authorizationToken'].decode('utf-8').split(':')
    docker_client.login(username=username, password=password, registry=auth_data['proxyEndpoint'])

    # Push Docker image to ECR
    push_logs = docker_client.images.push(full_image_name, stream=True, decode=True)
    for chunk in push_logs:
        if 'status' in chunk:
            print(chunk['status'])

if __name__ == "__main__":
    project_name = sys.argv[1]
    repository_name = sys.argv[2]
    aws_account_id = sys.argv[3]
    aws_region = sys.argv[4]
    build_and_push(project_name, repository_name, aws_account_id, aws_region)
