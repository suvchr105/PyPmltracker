# tests/test_visualization.py
import unittest
import os
import shutil
import tempfile
import numpy as np
from tests.conftest import get_free_port
from pypmltracker.core.experiment import Experiment
from pypmltracker.visualization.plots import Plotter

class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.experiment = Experiment(
            project_name="test_project",
            run_name="test_run",
            storage_dir=self.test_dir
        )
        self.plotter = Plotter(self.experiment)
    
    def tearDown(self):
        self.experiment.finish()
        shutil.rmtree(self.test_dir)
    
    def test_line_plot(self):
        # Create some test data
        data = {
            "accuracy": [0.7, 0.8, 0.85, 0.9],
            "loss": [0.5, 0.4, 0.3, 0.2]
        }
        
        # Create a line plot
        artifact_path = self.plotter.line_plot(
            data,
            title="Test Plot",
            xlabel="Epoch",
            ylabel="Value",
            name="test_plot"
        )
        
        # Check if plot was saved
        self.assertTrue(os.path.exists(artifact_path))
        
        # Check if artifact was logged
        self.assertIn("plot_test_plot", self.experiment.artifacts)
    
    def test_confusion_matrix(self):
        # Create a test confusion matrix
        cm = np.array([[10, 2], [3, 15]])
        
        # Create a confusion matrix plot
        artifact_path = self.plotter.confusion_matrix(
            cm,
            classes=["Class 0", "Class 1"],
            name="test_cm"
        )
        
        # Check if plot was saved
        self.assertTrue(os.path.exists(artifact_path))
        
        # Check if artifact was logged
        self.assertIn("plot_test_cm", self.experiment.artifacts)

if __name__ == "__main__":
    unittest.main()
