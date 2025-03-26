# tests/test_integrations.py
import unittest
import os
import shutil
import tempfile
import numpy as np
from tests.conftest import get_free_port
from pypmltracker.core.experiment import Experiment

class TestPyTorchIntegration(unittest.TestCase):
    def setUp(self):
        try:
            import torch
            import torch.nn as nn
            self.skip_test = False
        except ImportError:
            self.skip_test = True
            return
            
        self.test_dir = tempfile.mkdtemp()
        self.experiment = Experiment(
            project_name="test_project",
            run_name="test_run",
            storage_dir=self.test_dir
        )
        
        from pypmltracker.integrations.pytorch import PyTorchTracker
        self.tracker = PyTorchTracker(self.experiment, log_gradients=True)
        
        # Create a simple model
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1)
        )
    
    def tearDown(self):
        if hasattr(self, 'test_dir'):
            self.experiment.finish()
            shutil.rmtree(self.test_dir)
    
    def test_watch_model(self):
        if self.skip_test:
            self.skipTest("PyTorch not installed")
        
        self.tracker.watch(self.model)
        
        # Track some metrics
        self.tracker.track_metrics({"loss": 0.5})
        
        # Check if metrics were logged
        self.assertIn("loss", self.experiment.metrics)
    
    def test_save_model(self):
        if self.skip_test:
            self.skipTest("PyTorch not installed")
        
        # Save the model
        artifact_path = self.tracker.save_model(self.model, "test_model")
        
        # Check if artifact was logged
        self.assertIn("test_model", self.experiment.artifacts)

class TestTensorFlowIntegration(unittest.TestCase):
    def setUp(self):
        try:
            import tensorflow as tf
            self.skip_test = False
        except ImportError:
            self.skip_test = True
            return
            
        self.test_dir = tempfile.mkdtemp()
        self.experiment = Experiment(
            project_name="test_project",
            run_name="test_run",
            storage_dir=self.test_dir
        )
        
        from pypmltracker.integrations.tensorflow import TensorFlowTracker
        self.tracker = TensorFlowTracker(self.experiment)
    
    def tearDown(self):
        if hasattr(self, 'test_dir'):
            self.experiment.finish()
            shutil.rmtree(self.test_dir)
    
    def test_track_metrics(self):
        if self.skip_test:
            self.skipTest("TensorFlow not installed")
        
        # Track some metrics
        self.tracker.track_metrics({"loss": 0.5})
        
        # Check if metrics were logged
        self.assertIn("loss", self.experiment.metrics)

class TestSklearnIntegration(unittest.TestCase):
    def setUp(self):
        try:
            from sklearn.linear_model import LinearRegression
            self.skip_test = False
        except ImportError:
            self.skip_test = True
            return
            
        self.test_dir = tempfile.mkdtemp()
        self.experiment = Experiment(
            project_name="test_project",
            run_name="test_run",
            storage_dir=self.test_dir
        )
        
        from pypmltracker.integrations.sklearn import SklearnTracker
        self.tracker = SklearnTracker(self.experiment)
        
        # Create a simple model
        from sklearn.linear_model import LinearRegression
        self.model = LinearRegression()
        
        # Fit the model with some dummy data
        X = np.random.rand(100, 5)
        y = np.random.rand(100)
        self.model.fit(X, y)
    
    def tearDown(self):
        if hasattr(self, 'test_dir'):
            self.experiment.finish()
            shutil.rmtree(self.test_dir)
    
    def test_log_params(self):
        if self.skip_test:
            self.skipTest("scikit-learn not installed")
        
        # Log model parameters
        self.tracker.log_params(self.model)
        
        # Check if parameters were logged (at least one)
        metrics_path = os.path.join(self.test_dir, "test_project", "test_run", "metrics.json")
        self.assertTrue(os.path.exists(metrics_path))
    
    def test_save_model(self):
        if self.skip_test:
            self.skipTest("scikit-learn not installed")
        
        # Save the model
        artifact_path = self.tracker.save_model(self.model, "test_model")
        
        # Check if artifact was logged
        self.assertIn("test_model", self.experiment.artifacts)

if __name__ == "__main__":
    unittest.main()
