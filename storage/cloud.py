import os
import json
import tempfile
import boto3
from botocore.exceptions import ClientError
from pathlib import Path

class S3Storage:
    """AWS S3 storage for experiments."""
    
    def __init__(self, bucket_name, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
        """
        Initialize S3 storage.
        
        Args:
            bucket_name (str): S3 bucket name
            aws_access_key_id (str, optional): AWS access key ID
            aws_secret_access_key (str, optional): AWS secret access key
            region_name (str, optional): AWS region name
        """
        self.bucket_name = bucket_name
        
        # Initialize S3 client
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        # Create bucket if it doesn't exist
        try:
            self.s3.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                if region_name:
                    self.s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region_name}
                    )
                else:
                    self.s3.create_bucket(Bucket=bucket_name)
    
    def _get_s3_key(self, project_name, run_name, filename):
        """Get S3 key for a file."""
        return f"{project_name}/{run_name}/{filename}"
    
    def save_run(self, project_name, run_name, run_data):
        """
        Save run data to S3.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
            run_data (dict): Run data to save
        
        Returns:
            str: S3 key of the saved run
        """
        # Convert run data to JSON
        run_json = json.dumps(run_data, indent=2)
        
        # Upload to S3
        key = self._get_s3_key(project_name, run_name, "run_info.json")
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=run_json,
            ContentType='application/json'
        )
        
        return key
    
    def save_metrics(self, project_name, run_name, metrics):
        """
        Save metrics to S3.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
            metrics (dict): Metrics to save
        
        Returns:
            str: S3 key of the saved metrics
        """
        # Convert metrics to JSON
        metrics_json = json.dumps(metrics, indent=2)
        
        # Upload to S3
        key = self._get_s3_key(project_name, run_name, "metrics.json")
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=metrics_json,
            ContentType='application/json'
        )
        
        return key
    
    def save_artifact(self, project_name, run_name, artifact_name, file_path, metadata=None):
        """
        Save an artifact to S3.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
            artifact_name (str): Artifact name
            file_path (str): Path to the artifact file
            metadata (dict, optional): Additional metadata about the artifact
        
        Returns:
            str: S3 key of the saved artifact
        """
        # Upload file to S3
        artifact_key = self._get_s3_key(project_name, run_name, f"artifacts/{os.path.basename(file_path)}")
        with open(file_path, 'rb') as f:
            self.s3.upload_fileobj(f, self.bucket_name, artifact_key)
        
        # Update artifacts registry
        artifacts_key = self._get_s3_key(project_name, run_name, "artifacts.json")
        
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=artifacts_key)
            artifacts = json.loads(response['Body'].read().decode('utf-8'))
        except ClientError:
            artifacts = {}
        
        artifacts[artifact_name] = {
            'key': artifact_key,
            'original_path': file_path,
            'metadata': metadata or {}
        }
        
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=artifacts_key,
            Body=json.dumps(artifacts, indent=2),
            ContentType='application/json'
        )
        
        return artifact_key
    
    def load_run(self, project_name, run_name):
        """
        Load run data from S3.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
        
        Returns:
            dict: Run data
        """
        key = self._get_s3_key(project_name, run_name, "run_info.json")
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError:
            return None
    
    def load_metrics(self, project_name, run_name):
        """
        Load metrics from S3.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
        
        Returns:
            dict: Metrics data
        """
        key = self._get_s3_key(project_name, run_name, "metrics.json")
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError:
            return None
    
    def download_artifact(self, project_name, run_name, artifact_name, destination=None):
        """
        Download an artifact from S3.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
            artifact_name (str): Artifact name
            destination (str, optional): Destination path
        
        Returns:
            str: Path to the downloaded artifact
        """
        # Get artifact metadata
        artifacts_key = self._get_s3_key(project_name, run_name, "artifacts.json")
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=artifacts_key)
            artifacts = json.loads(response['Body'].read().decode('utf-8'))
        except ClientError:
            return None
        
        if artifact_name not in artifacts:
            return None
        
        artifact = artifacts[artifact_name]
        artifact_key = artifact['key']
        
        # Create destination path
        if destination is None:
            destination = tempfile.gettempdir()
        
        destination_path = os.path.join(destination, os.path.basename(artifact_key))
        
        # Download the artifact
        self.s3.download_file(self.bucket_name, artifact_key, destination_path)
        
        return destination_path
    
    def list_projects(self):
        """
        List all projects.
        
        Returns:
            list: List of project names
        """
        projects = set()
        paginator = self.s3.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=self.bucket_name, Delimiter='/'):
            if 'CommonPrefixes' in page:
                for prefix in page['CommonPrefixes']:
                    project = prefix['Prefix'].rstrip('/')
                    projects.add(project)
        
        return list(projects)
    
    def list_runs(self, project_name):
        """
        List all runs for a project.
        
        Args:
            project_name (str): Project name
        
        Returns:
            list: List of run names
        """
        runs = set()
        prefix = f"{project_name}/"
        paginator = self.s3.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter='/'):
            if 'CommonPrefixes' in page:
                for prefix in page['CommonPrefixes']:
                    run = prefix['Prefix'].split('/')[1]
                    runs.add(run)
        
        return list(runs)
