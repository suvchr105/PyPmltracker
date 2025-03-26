import os
import json
import glob
import threading
from flask import Flask, render_template, jsonify, request, send_from_directory
from pathlib import Path

class Dashboard:
    """Web dashboard for visualizing experiments."""
    
    def __init__(self, storage_dir="./mltracker_data", host="127.0.0.1", port=8000):
        """
        Initialize dashboard.
        
        Args:
            storage_dir (str): Base directory for experiment data
            host (str): Host to run the dashboard on
            port (int): Port to run the dashboard on
        """
        self.storage_dir = Path(storage_dir)
        self.host = host
        self.port = port
        self.app = Flask(__name__, 
                         template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                         static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        self.thread = None
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up Flask routes."""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/projects')
        def get_projects():
            projects = []
            project_dirs = glob.glob(str(self.storage_dir / "*"))
            for project_dir in project_dirs:
                if os.path.isdir(project_dir):
                    projects.append(os.path.basename(project_dir))
            return jsonify(projects)
        
        @self.app.route('/api/projects/<project_name>/runs')
        def get_runs(project_name):
            runs = []
            run_dirs = glob.glob(str(self.storage_dir / project_name / "*"))
            for run_dir in run_dirs:
                if os.path.isdir(run_dir):
                    run_name = os.path.basename(run_dir)
                    
                    # Load run info
                    info_path = os.path.join(run_dir, "run_info.json")
                    config_path = os.path.join(run_dir, "config.json")
                    
                    run_info = {}
                    config = {}
                    
                    if os.path.exists(info_path):
                        with open(info_path, 'r') as f:
                            run_info = json.load(f)
                    
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                    
                    runs.append({
                        "name": run_name,
                        "info": run_info,
                        "config": config
                    })
            
            return jsonify(runs)
        
        @self.app.route('/api/projects/<project_name>/runs/<run_name>/metrics')
        def get_metrics(project_name, run_name):
            metrics_path = os.path.join(self.storage_dir, project_name, run_name, "metrics.json")
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    metrics = json.load(f)
                return jsonify(metrics)
            return jsonify({})
        
        @self.app.route('/api/projects/<project_name>/runs/<run_name>/artifacts')
        def get_artifacts(project_name, run_name):
            artifacts_path = os.path.join(self.storage_dir, project_name, run_name, "artifacts.json")
            if os.path.exists(artifacts_path):
                with open(artifacts_path, 'r') as f:
                    artifacts = json.load(f)
                return jsonify(artifacts)
            return jsonify({})
        
        @self.app.route('/api/projects/<project_name>/runs/<run_name>/artifacts/<artifact_name>')
        def get_artifact(project_name, run_name, artifact_name):
            artifacts_path = os.path.join(self.storage_dir, project_name, run_name, "artifacts.json")
            if os.path.exists(artifacts_path):
                with open(artifacts_path, 'r') as f:
                    artifacts = json.load(f)
                
                if artifact_name in artifacts:
                    artifact = artifacts[artifact_name]
                    artifact_path = artifact['path']
                    return send_from_directory(os.path.dirname(artifact_path), 
                                              os.path.basename(artifact_path))
            
            return jsonify({"error": "Artifact not found"}), 404
    
    def start(self, debug=False, open_browser=True):
        """
        Start the dashboard server.
        
        Args:
            debug (bool): Whether to run in debug mode
            open_browser (bool): Whether to open the browser automatically
        """
        if open_browser:
            import webbrowser
            url = f"http://{self.host}:{self.port}"
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        
        if debug:
            self.app.run(host=self.host, port=self.port, debug=debug)
        else:
            self.thread = threading.Thread(target=self.app.run, 
                                          kwargs={'host': self.host, 'port': self.port})
            self.thread.daemon = True
            self.thread.start()
            print(f"MLTracker: Dashboard running at http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the dashboard server."""
        # This is a bit hacky but works for development purposes
        import requests
        try:
            requests.get(f"http://{self.host}:{self.port}/shutdown")
        except:
            pass
        
        if self.thread:
            self.thread.join(timeout=1.0)
