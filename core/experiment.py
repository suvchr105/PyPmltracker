import os
import json
import time
import uuid
from datetime import datetime
import threading
from pathlib import Path

class Experiment:
    """
    Core experiment tracking class that logs metrics, parameters, and artifacts.
    """
    def __init__(self, project_name, run_name=None, config=None, tags=None, storage_dir="./mltracker_data"):
        """
        Initialize a new experiment run.
        
        Args:
            project_name (str): Name of the project
            run_name (str, optional): Name of the run. Defaults to auto-generated name.
            config (dict, optional): Configuration parameters for the run.
            tags (list, optional): List of tags for the run.
            storage_dir (str, optional): Base directory for storing experiment data.
        """
        self.project_name = project_name
        self.run_id = str(uuid.uuid4())[:8]
        self.run_name = run_name or f"run_{self.run_id}"
        self.start_time = datetime.now()
        self.config = config or {}
        self.tags = tags or []
        self.metrics = {}
        self.artifacts = {}
        self._step = 0
        self._lock = threading.Lock()
        
        # Create project directory structure
        self.storage_dir = Path(storage_dir)
        self.project_dir = self.storage_dir / project_name
        self.run_dir = self.project_dir / self.run_name
        self.artifacts_dir = self.run_dir / "artifacts"
        
        os.makedirs(self.run_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)
        
        # Save initial metadata
        self._save_config()
        self._save_run_info()
        
        print(f"MLTracker: Experiment '{self.run_name}' initialized in project '{project_name}'")
    
    def _save_config(self):
        """Save configuration to disk."""
        config_path = self.run_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _save_run_info(self):
        """Save run metadata to disk."""
        info = {
            'run_id': self.run_id,
            'run_name': self.run_name,
            'project': self.project_name,
            'start_time': self.start_time.isoformat(),
            'tags': self.tags,
            'status': 'running'
        }
        
        info_path = self.run_dir / "run_info.json"
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
    
    def log(self, metrics, step=None):
        """
        Log metrics at a specific step.
        
        Args:
            metrics (dict): Dictionary of metric names and values
            step (int, optional): Step number. If None, uses auto-incrementing counter.
        """
        with self._lock:
            timestamp = time.time()
            step = step if step is not None else self._step
            
            for key, value in metrics.items():
                if key not in self.metrics:
                    self.metrics[key] = []
                
                # Convert to float if possible, otherwise store as string
                try:
                    value_float = float(value)
                except (ValueError, TypeError):
                    value_float = str(value)
                
                self.metrics[key].append({
                    'value': value_float,
                    'step': step,
                    'timestamp': timestamp
                })
            
            # Auto-increment step if using internal counter
            if step == self._step:
                self._step += 1
            
            # Save metrics after each update
            self._save_metrics()
    
    def _save_metrics(self):
        """Save metrics to disk."""
        metrics_path = self.run_dir / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def log_artifact(self, name, file_path, metadata=None):
        """
        Log an artifact file.
        
        Args:
            name (str): Name of the artifact
            file_path (str): Path to the artifact file
            metadata (dict, optional): Additional metadata about the artifact
        
        Returns:
            str: Path where the artifact was saved
        """
        import shutil
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Artifact file not found: {file_path}")
        
        # Copy the file to artifacts directory
        dest_path = self.artifacts_dir / file_path.name
        shutil.copy2(file_path, dest_path)
        
        # Record artifact metadata
        artifact_info = {
            'name': name,
            'path': str(dest_path),
            'original_path': str(file_path),
            'size_bytes': os.path.getsize(dest_path),
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        
        self.artifacts[name] = artifact_info
        
        # Save artifacts registry
        artifacts_path = self.run_dir / "artifacts.json"
        with open(artifacts_path, 'w') as f:
            json.dump(self.artifacts, f, indent=2)
        
        return str(dest_path)
    
    def finish(self):
        """End the experiment run and record final metadata."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Update run info with completion details
        info_path = self.run_dir / "run_info.json"
        with open(info_path, 'r') as f:
            run_info = json.load(f)
        
        run_info.update({
            'end_time': end_time.isoformat(),
            'duration': duration,
            'status': 'completed'
        })
        
        with open(info_path, 'w') as f:
            json.dump(run_info, f, indent=2)
        
        print(f"MLTracker: Experiment '{self.run_name}' completed in {duration:.2f} seconds")
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()
