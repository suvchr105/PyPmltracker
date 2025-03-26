# tests/test_core.py
import unittest
import os
import shutil
import tempfile
from tests.conftest import get_free_port
from pypmltracker.core.experiment import Experiment
from pypmltracker.core.system_monitor import SystemMonitor
import time

class TestExperiment(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.experiment = Experiment(
            project_name="test_project",
            run_name="test_run",
            config={"learning_rate": 0.01, "batch_size": 32},
            storage_dir=self.test_dir
        )
    
    def tearDown(self):
        self.experiment.finish()
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        self.assertEqual(self.experiment.project_name, "test_project")
        self.assertEqual(self.experiment.run_name, "test_run")
        self.assertEqual(self.experiment.config, {"learning_rate": 0.01, "batch_size": 32})
        
        # Check if directories were created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "test_project")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "test_project", "test_run")))
    
    def test_log_metrics(self):
        self.experiment.log({"accuracy": 0.85, "loss": 0.35})
        
        # Check if metrics were logged
        self.assertIn("accuracy", self.experiment.metrics)
        self.assertIn("loss", self.experiment.metrics)
        
        # Check if metrics file was created
        metrics_path = os.path.join(self.test_dir, "test_project", "test_run", "metrics.json")
        self.assertTrue(os.path.exists(metrics_path))
    
    def test_log_artifact(self):
        # Create a test file
        test_file = os.path.join(self.test_dir, "test_artifact.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        # Log the artifact
        self.experiment.log_artifact("test_artifact", test_file)
        
        # Check if artifact was logged
        self.assertIn("test_artifact", self.experiment.artifacts)
        
        # Check if artifact file was copied
        artifact_path = os.path.join(self.test_dir, "test_project", "test_run", "artifacts", "test_artifact.txt")
        self.assertTrue(os.path.exists(artifact_path))

class TestSystemMonitor(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.experiment = Experiment(
            project_name="test_project",
            run_name="test_run",
            storage_dir=self.test_dir
        )
        self.monitor = SystemMonitor(self.experiment, interval=1.0)
    
    def tearDown(self):
        self.monitor.stop()
        self.experiment.finish()
        shutil.rmtree(self.test_dir)
    
    def test_monitor_start_stop(self):
        self.monitor.start()
        self.assertTrue(self.monitor.running)
        self.assertIsNotNone(self.monitor.thread)
        
        # Let it run for a short time
        time.sleep(2)
        
        self.monitor.stop()
        self.assertFalse(self.monitor.running)
        
        # Check if metrics were logged
        metrics_path = os.path.join(self.test_dir, "test_project", "test_run", "metrics.json")
        self.assertTrue(os.path.exists(metrics_path))

if __name__ == "__main__":
    unittest.main()
