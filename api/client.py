import requests
import json
import os
from pathlib import Path

class MLTrackerClient:
    """Client for interacting with a remote MLTracker server."""
    
    def __init__(self, base_url, api_key=None):
        """
        Initialize client.
        
        Args:
            base_url (str): Base URL of the MLTracker server
            api_key (str, optional): API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def list_projects(self):
        """
        List all projects.
        
        Returns:
            list: List of project names
        """
        response = requests.get(f"{self.base_url}/api/projects", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def list_runs(self, project_name):
        """
        List all runs for a project.
        
        Args:
            project_name (str): Project name
        
        Returns:
            list: List of run information
        """
        response = requests.get(f"{self.base_url}/api/projects/{project_name}/runs", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_run(self, project_name, run_name):
        """
        Get run information.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
        
        Returns:
            dict: Run information
        """
        response = requests.get(f"{self.base_url}/api/projects/{project_name}/runs/{run_name}", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self, project_name, run_name):
        """
        Get run metrics.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
        
        Returns:
            dict: Run metrics
        """
        response = requests.get(f"{self.base_url}/api/projects/{project_name}/runs/{run_name}/metrics", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_artifacts(self, project_name, run_name):
        """
        Get run artifacts.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
        
        Returns:
            dict: Run artifacts
        """
        response = requests.get(f"{self.base_url}/api/projects/{project_name}/runs/{run_name}/artifacts", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def download_artifact(self, project_name, run_name, artifact_name, destination=None):
        """
        Download an artifact.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
            artifact_name (str): Artifact name
            destination (str, optional): Destination path
        
        Returns:
            str: Path to the downloaded artifact
        """
        response = requests.get(f"{self.base_url}/api/projects/{project_name}/runs/{run_name}/artifacts/{artifact_name}", 
                               headers=self.headers, stream=True)
        response.raise_for_status()
        
        # Create destination path
        if destination is None:
            destination = os.getcwd()
        
        destination_path = os.path.join(destination, artifact_name)
        
        # Download the artifact
        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return destination_path
