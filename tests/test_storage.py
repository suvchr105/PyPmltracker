# tests/test_storage.py
import unittest
import os
import shutil
import tempfile
from tests.conftest import get_free_port
from pypmltracker.storage.local import LocalStorage

class TestLocalStorage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = LocalStorage(self.test_dir)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_save_run(self):
        run_data = {
            "run_id": "test_run",
            "project": "test_project",
            "start_time": "2023-01-01T00:00:00",
            "tags": ["test"],
            "status": "running"
        }
        
        run_path = self.storage.save_run("test_project", "test_run", run_data)
        
        # Check if run was saved
        self.assertTrue(os.path.exists(run_path))
        self.assertTrue(os.path.exists(os.path.join(run_path, "run_info.json")))
    
    def test_save_metrics(self):
        metrics = {
            "accuracy": [{"value": 0.85, "step": 0, "timestamp": 1672531200}],
            "loss": [{"value": 0.35, "step": 0, "timestamp": 1672531200}]
        }
        
        metrics_path = self.storage.save_metrics("test_project", "test_run", metrics)
        
        # Check if metrics were saved
        self.assertTrue(os.path.exists(metrics_path))
    
    def test_list_projects_and_runs(self):
        # Create some test projects and runs
        os.makedirs(os.path.join(self.test_dir, "project1", "run1"))
        os.makedirs(os.path.join(self.test_dir, "project1", "run2"))
        os.makedirs(os.path.join(self.test_dir, "project2", "run1"))
        
        projects = self.storage.list_projects()
        self.assertIn("project1", projects)
        self.assertIn("project2", projects)
        
        runs = self.storage.list_runs("project1")
        self.assertIn("run1", runs)
        self.assertIn("run2", runs)

if __name__ == "__main__":
    unittest.main()
