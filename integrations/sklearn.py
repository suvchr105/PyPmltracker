import os
import tempfile
import pickle
import numpy as np
from sklearn.base import BaseEstimator

class SklearnTracker:
    """Integration with scikit-learn for automatic tracking."""
    
    def __init__(self, experiment):
        """
        Initialize scikit-learn tracker.
        
        Args:
            experiment: The experiment to log to
        """
        self.experiment = experiment
        self.step = 0
    
    def track_metrics(self, metrics, step=None):
        """
        Track metrics from training or evaluation.
        
        Args:
            metrics (dict): Dictionary of metrics to log
            step (int, optional): Step number. If None, uses internal counter.
        """
        if step is not None:
            self.step = step
        
        self.experiment.log(metrics, step=self.step)
        
        if step is None:
            self.step += 1
    
    def log_params(self, estimator):
        """
        Log parameters of a scikit-learn estimator.
        
        Args:
            estimator: scikit-learn estimator
        """
        if not isinstance(estimator, BaseEstimator):
            print("Warning: Object is not a scikit-learn estimator")
            return
        
        params = estimator.get_params()
        # Convert any numpy values to Python native types
        for k, v in params.items():
            if isinstance(v, (np.ndarray, np.generic)):
                params[k] = v.tolist() if hasattr(v, 'tolist') else v.item()
        
        self.experiment.log({f"params/{k}": v for k, v in params.items()})
    
    def save_model(self, model, name="model"):
        """
        Save a scikit-learn model.
        
        Args:
            model: scikit-learn model to save
            name (str): Name for the saved model
        
        Returns:
            str: Path to the saved model
        """
        # Create a temporary file to save the model
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Save the model
        with open(tmp_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Log the artifact
        artifact_path = self.experiment.log_artifact(
            name=name,
            file_path=tmp_path,
            metadata={
                'framework': 'scikit-learn',
                'type': 'model',
                'format': 'pickle'
            }
        )
        
        # Clean up the temporary file
        os.unlink(tmp_path)
        
        return artifact_path
