import os
import shutil
import json
from pathlib import Path

class LocalStorage:
    """Local filesystem storage for experiments."""
    
    def __init__(self, base_dir="./mltracker_data"):
        """
        Initialize local storage.
        
        Args:
            base_dir (str): Base directory for storing experiment data
        """
        self.base_dir = Path(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
    
    def save_run(self, project_name, run_name, run_data):
        """
        Save run data to local storage.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
            run_data (dict): Run data to save
        
        Returns:
            str: Path to the saved run
        """
        run_dir = self.base_dir / project_name / run_name
        os.makedirs(run_dir, exist_ok=True)
        
        # Save run data
        run_path = run_dir / "run_info.json"
        with open(run_path, 'w') as f:
            json.dump(run_data, f, indent=2)
        
        return str(run_dir)
    
    def save_metrics(self, project_name, run_name, metrics):
        """
        Save metrics to local storage.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
            metrics (dict): Metrics to save
        
        Returns:
            str: Path to the saved metrics
        """
        run_dir = self.base_dir / project_name / run_name
        os.makedirs(run_dir, exist_ok=True)
        
        # Save metrics
        metrics_path = run_dir / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return str(metrics_path)
    
    def save_artifact(self, project_name, run_name, artifact_name, file_path, metadata=None):
        """
        Save an artifact to local storage.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
            artifact_name (str): Artifact name
            file_path (str): Path to the artifact file
            metadata (dict, optional): Additional metadata about the artifact
        
        Returns:
            str: Path to the saved artifact
        """
        artifacts_dir = self.base_dir / project_name / run_name / "artifacts"
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Copy the file to artifacts directory
        dest_path = artifacts_dir / os.path.basename(file_path)
        shutil.copy2(file_path, dest_path)
        
        # Update artifacts registry
        artifacts_path = self.base_dir / project_name / run_name / "artifacts.json"
        
        artifacts = {}
        if os.path.exists(artifacts_path):
            with open(artifacts_path, 'r') as f:
                artifacts = json.load(f)
        
        artifacts[artifact_name] = {
            'path': str(dest_path),
            'original_path': file_path,
            'metadata': metadata or {}
        }
        
        with open(artifacts_path, 'w') as f:
            json.dump(artifacts, f, indent=2)
        
        return str(dest_path)
    
    def load_run(self, project_name, run_name):
        """
        Load run data from local storage.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
        
        Returns:
            dict: Run data
        """
        run_path = self.base_dir / project_name / run_name / "run_info.json"
        if not run_path.exists():
            return None
        
        with open(run_path, 'r') as f:
            return json.load(f)
    
    def load_metrics(self, project_name, run_name):
        """
        Load metrics from local storage.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
        
        Returns:
            dict: Metrics data
        """
        metrics_path = self.base_dir / project_name / run_name / "metrics.json"
        if not metrics_path.exists():
            return None
        
        with open(metrics_path, 'r') as f:
            return json.load(f)
    
    def load_artifact(self, project_name, run_name, artifact_name):
        """
        Load artifact metadata from local storage.
        
        Args:
            project_name (str): Project name
            run_name (str): Run name
            artifact_name (str): Artifact name
        
        Returns:
            dict: Artifact metadata including path
        """
        artifacts_path = self.base_dir / project_name / run_name / "artifacts.json"
        if not artifacts_path.exists():
            return None
        
        with open(artifacts_path, 'r') as f:
            artifacts = json.load(f)
        
        return artifacts.get(artifact_name)
    
    def list_projects(self):
        """
        List all projects.
        
        Returns:
            list: List of project names
        """
        projects = []
        for path in self.base_dir.glob("*"):
            if path.is_dir():
                projects.append(path.name)
        return projects
    
    def list_runs(self, project_name):
        """
        List all runs for a project.
        
        Args:
            project_name (str): Project name
        
        Returns:
            list: List of run names
        """
        runs = []
        project_dir = self.base_dir / project_name
        if not project_dir.exists():
            return runs
        
        for path in project_dir.glob("*"):
            if path.is_dir():
                runs.append(path.name)
        return runs

