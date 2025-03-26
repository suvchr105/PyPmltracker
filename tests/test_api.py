# tests/test_api.py
import unittest
import os
import shutil
import tempfile
import threading
import time
import requests
from tests.conftest import get_free_port
from pypmltracker.api.server import MLTrackerServer
from pypmltracker.api.client import MLTrackerClient
from pypmltracker.core.experiment import Experiment

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
        # Use dynamic port allocation
        self.port = get_free_port()
        
        # Create some test data
        self.experiment = Experiment(
            project_name="test_project",
            run_name="test_run",
            config={"learning_rate": 0.01},
            storage_dir=self.test_dir
        )
        self.experiment.log({"accuracy": 0.85})
        
        # Create a test file
        self.test_file = os.path.join(self.test_dir, "test_artifact.txt")
        with open(self.test_file, "w") as f:
            f.write("test content")
        
        # Log the artifact
        self.experiment.log_artifact("test_artifact", self.test_file)
        self.experiment.finish()
        
        # Start server with dynamic port
        self.server = MLTrackerServer(
            storage_dir=self.test_dir,
            host="127.0.0.1",
            port=self.port
        )
        
        # Start the server in a way that won't block
        self.server.start()
        
        # Wait for server to be ready
        self.wait_for_server(f"http://127.0.0.1:{self.port}/api/projects", max_retries=5)
        
        # Create client with dynamic port
        self.client = MLTrackerClient(
            base_url=f"http://127.0.0.1:{self.port}"
        )
    
    def tearDown(self):
        if hasattr(self, 'server'):
            self.server.stop()
            time.sleep(0.5)  # Add a small delay to ensure port is released
        shutil.rmtree(self.test_dir)

    
    def wait_for_server(self, url, max_retries=5, delay=1):
        for i in range(max_retries):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return
            except requests.exceptions.ConnectionError:
                pass
            
            if i < max_retries - 1:
                time.sleep(delay)
        
        raise Exception(f"Server failed to start after {max_retries} attempts")



    
    def test_list_projects(self):
        projects = self.client.list_projects()
        self.assertIn("test_project", projects)
    
    def test_list_runs(self):
        runs = self.client.list_runs("test_project")
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["name"], "test_run")
    
    def test_get_metrics(self):
        metrics = self.client.get_metrics("test_project", "test_run")
        self.assertIn("accuracy", metrics)
    
    def test_get_artifacts(self):
        artifacts = self.client.get_artifacts("test_project", "test_run")
        self.assertIn("test_artifact", artifacts)

if __name__ == "__main__":
    unittest.main()
