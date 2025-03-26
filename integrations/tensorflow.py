import os
import tempfile
import tensorflow as tf

class TensorFlowTracker:
    """Integration with TensorFlow for automatic tracking."""
    
    def __init__(self, experiment):
        """
        Initialize TensorFlow tracker.
        
        Args:
            experiment: The experiment to log to
        """
        self.experiment = experiment
        self.step = 0
    
    class MetricsLogger(tf.keras.callbacks.Callback):
        """Keras callback for logging metrics during training."""
        
        def __init__(self, tracker):
            super().__init__()
            self.tracker = tracker
        
        def on_epoch_end(self, epoch, logs=None):
            logs = logs or {}
            epoch_metrics = {f'epoch/{k}': v for k, v in logs.items()}
            epoch_metrics['epoch'] = epoch
            self.tracker.experiment.log(epoch_metrics, step=self.tracker.step)
            self.tracker.step += 1
        
        def on_batch_end(self, batch, logs=None):
            logs = logs or {}
            if batch % 10 == 0:  # Log every 10 batches to avoid overwhelming storage
                batch_metrics = {f'batch/{k}': v for k, v in logs.items()}
                batch_metrics['batch'] = batch
                self.tracker.experiment.log(batch_metrics)
    
    def get_callback(self):
        """Get a Keras callback for automatic logging."""
        return self.MetricsLogger(self)
    
    def track_metrics(self, metrics, step=None):
        
        if step is not None:
            self.step = step
        
        self.experiment.log(metrics, step=self.step)
        
        if step is None:
            self.step += 1
    
    def save_model(self, model, name="model"):
        """
        Save a TensorFlow model.
        
        Args:
            model: TensorFlow model to save
            name (str): Name for the saved model
        
        Returns:
            str: Path to the saved model
        """
        # Create a temporary directory to save the model
        tmp_dir = tempfile.mkdtemp()
        model_path = os.path.join(tmp_dir, name)
        
        # Save the model
        model.save(model_path)
        
        # For SavedModel format, we need to zip it for easier handling
        import shutil
        zip_path = os.path.join(tmp_dir, f"{name}.zip")
        shutil.make_archive(
            os.path.join(tmp_dir, name),
            'zip',
            model_path
        )
        
        # Log the artifact
        artifact_path = self.experiment.log_artifact(
            name=name,
            file_path=zip_path,
            metadata={
                'framework': 'tensorflow',
                'type': 'model',
                'format': 'SavedModel'
            }
        )
        
        # Clean up temporary directory
        shutil.rmtree(tmp_dir)
        
        return artifact_path

