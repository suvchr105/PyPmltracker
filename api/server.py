from flask import Flask, request, jsonify, send_file
import os
import json
from pathlib import Path
from werkzeug.utils import secure_filename
import threading

class MLTrackerServer:
    """Server for exposing MLTracker functionality via a REST API."""
    
    def __init__(self, storage_dir="./mltracker_data", host="127.0.0.1", port=5000, api_key=None):
        """
        Initialize server.
        
        Args:
            storage_dir (str): Base directory for experiment data
            host (str): Host to run the server on
            port (int): Port to run the server on
            api_key (str, optional): API key for authentication
        """
        self.storage_dir = Path(storage_dir)
        self.host = host
        self.port = port
        self.api_key = api_key
        self.app = Flask(__name__)
        self.thread = None
        self._setup_routes()
    
    def _check_auth(self):
        """Check API key authentication."""
        if not self.api_key:
            return True
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return False
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != 'bearer':
                return False
            return token == self.api_key
        except:
            return False
    
    def _setup_routes(self):
        """Set up Flask routes."""
        
        @self.app.before_request
        def check_auth():
            if not self._check_auth():
                return jsonify({"error": "Unauthorized"}), 401
        
        @self.app.route('/api/projects', methods=['GET'])
        def list_projects():
            projects = []
            for path in self.storage_dir.glob("*"):
                if path.is_dir():
                    projects.append(path.name)
            return jsonify(projects)
        
        @self.app.route('/api/projects/<project_name>/runs', methods=['GET'])
        def list_runs(project_name):
            runs = []
            project_dir = self.storage_dir / project_name
            if not project_dir.exists():
                return jsonify([])
            
            for path in project_dir.glob("*"):
                if path.is_dir():
                    run_name = path.name
                    run_info_path = path / "run_info.json"
                    
                    if run_info_path.exists():
                        with open(run_info_path, 'r') as f:
                            run_info = json.load(f)
                        runs.append({
                            "name": run_name,
                            "info": run_info
                        })
            
            return jsonify(runs)
        
        @self.app.route('/api/projects/<project_name>/runs/<run_name>', methods=['GET'])
        def get_run(project_name, run_name):
            run_info_path = self.storage_dir / project_name / run_name / "run_info.json"
            config_path = self.storage_dir / project_name / run_name / "config.json"
            
            if not run_info_path.exists():
                return jsonify({"error": "Run not found"}), 404
            
            with open(run_info_path, 'r') as f:
                run_info = json.load(f)
            
            config = {}
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            
            return jsonify({
                "name": run_name,
                "info": run_info,
                "config": config
            })
        
        @self.app.route('/api/projects/<project_name>/runs/<run_name>/metrics', methods=['GET'])
        def get_metrics(project_name, run_name):
            metrics_path = self.storage_dir / project_name / run_name / "metrics.json"
            
            if not metrics_path.exists():
                return jsonify({"error": "Metrics not found"}), 404
            
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            return jsonify(metrics)
        
        @self.app.route('/api/projects/<project_name>/runs/<run_name>/artifacts', methods=['GET'])
        def get_artifacts(project_name, run_name):
            artifacts_path = self.storage_dir / project_name / run_name / "artifacts.json"
            
            if not artifacts_path.exists():
                return jsonify({"error": "Artifacts not found"}), 404
            
            with open(artifacts_path, 'r') as f:
                artifacts = json.load(f)
            
            return jsonify(artifacts)
        
        @self.app.route('/api/projects/<project_name>/runs/<run_name>/artifacts/<artifact_name>', methods=['GET'])
        def get_artifact(project_name, run_name, artifact_name):
            artifacts_path = self.storage_dir / project_name / run_name / "artifacts.json"
            
            if not artifacts_path.exists():
                return jsonify({"error": "Artifacts not found"}), 404
            
            with open(artifacts_path, 'r') as f:
                artifacts = json.load(f)
            
            if artifact_name not in artifacts:
                return jsonify({"error": "Artifact not found"}), 404
            
            artifact = artifacts[artifact_name]
            file_path = artifact['path']
            
            return send_file(file_path, as_attachment=True)
        
        @self.app.route('/api/projects/<project_name>/runs/<run_name>/log', methods=['POST'])
        def log_metrics(project_name, run_name):
            metrics = request.json
            
            if not metrics:
                return jsonify({"error": "No metrics provided"}), 400
            
            metrics_path = self.storage_dir / project_name / run_name / "metrics.json"
            
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    existing_metrics = json.load(f)
            else:
                existing_metrics = {}
            
            # Update existing metrics with new ones
            for key, value in metrics.items():
                if key not in existing_metrics:
                    existing_metrics[key] = []
                existing_metrics[key].append(value)
            
            with open(metrics_path, 'w') as f:
                json.dump(existing_metrics, f, indent=2)
            
            return jsonify({"message": "Metrics logged successfully"})
        
        @self.app.route('/api/projects/<project_name>/runs/<run_name>/artifact', methods=['POST'])
        def log_artifact(project_name, run_name):
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400
            
            file = request.files['file']
            artifact_name = request.form.get('name', file.filename)
            metadata = request.form.get('metadata', '{}')
            
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            
            if file:
                filename = secure_filename(file.filename)
                artifact_dir = self.storage_dir / project_name / run_name / "artifacts"
                artifact_dir.mkdir(parents=True, exist_ok=True)
                file_path = artifact_dir / filename
                file.save(file_path)
                
                artifacts_path = self.storage_dir / project_name / run_name / "artifacts.json"
                
                if artifacts_path.exists():
                    with open(artifacts_path, 'r') as f:
                        artifacts = json.load(f)
                else:
                    artifacts = {}
                
                artifacts[artifact_name] = {
                    "path": str(file_path),
                    "metadata": json.loads(metadata)
                }
                
                with open(artifacts_path, 'w') as f:
                    json.dump(artifacts, f, indent=2)
                
                return jsonify({"message": "Artifact logged successfully"})
            
            return jsonify({"error": "Failed to save artifact"}), 500
    
    def start(self, debug=False):
        """
        Start the server.
        
        Args:
            debug (bool): Whether to run in debug mode
        """
        if debug:
            self.app.run(host=self.host, port=self.port, debug=debug)
        else:
            self.thread = threading.Thread(target=self.app.run, 
                                          kwargs={'host': self.host, 'port': self.port})
            self.thread.daemon = True
            self.thread.start()
            print(f"MLTracker: Server running at http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the server."""
        if self.thread:
            # This is a bit hacky but works for development purposes
            import requests
            try:
                requests.get(f"http://{self.host}:{self.port}/shutdown")
            except:
                pass
            self.thread.join(timeout=1.0)

