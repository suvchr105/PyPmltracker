import os
import torch
from torch.utils.tensorboard import SummaryWriter
import tempfile

class PyTorchTracker:
    """Integration with PyTorch for automatic tracking."""
    
    def __init__(self, experiment, log_gradients=False, log_parameters=False):
        """
        Initialize PyTorch tracker.
        
        Args:
            experiment: The experiment to log to
            log_gradients (bool): Whether to log gradients
            log_parameters (bool): Whether to log model parameters
        """
        self.experiment = experiment
        self.log_gradients = log_gradients
        self.log_parameters = log_parameters
        self.step = 0
        self._tb_writer = None
        
        if log_gradients or log_parameters:
            # Create a temporary TensorBoard writer for model graphs
            self._tb_dir = tempfile.mkdtemp()
            self._tb_writer = SummaryWriter(log_dir=self._tb_dir)
    
    def watch(self, model):
        """
        Watch a PyTorch model to track parameters and gradients.
        
        Args:
            model: PyTorch model to watch
        """
        if self._tb_writer:
            # Log model graph
            try:
                # Create a dummy input based on the first parameter's size
                first_param = next(model.parameters())
                dummy_input = torch.zeros(1, *first_param.size()[1:])
                self._tb_writer.add_graph(model, dummy_input)
            except:
                print("MLTracker: Could not log model graph")
        
        # Set up hooks for parameter and gradient tracking
        if self.log_parameters or self.log_gradients:
            for name, param in model.named_parameters():
                if param.requires_grad:
                    if self.log_gradients:
                        param.register_hook(lambda grad, name=name: 
                            self._log_gradient(name, grad))
    
    def _log_gradient(self, name, grad):
        """Log gradient for a specific parameter."""
        if grad is not None:
            self.experiment.log({
                f'gradients/{name}/mean': grad.mean().item(),
                f'gradients/{name}/std': grad.std().item(),
                f'gradients/{name}/max': grad.max().item(),
                f'gradients/{name}/min': grad.min().item(),
            }, step=self.step)
    
    def _log_parameters(self, model):
        """Log model parameters."""
        for name, param in model.named_parameters():
            if param.requires_grad:
                self.experiment.log({
                    f'parameters/{name}/mean': param.data.mean().item(),
                    f'parameters/{name}/std': param.data.std().item(),
                    f'parameters/{name}/max': param.data.max().item(),
                    f'parameters/{name}/min': param.data.min().item(),
                }, step=self.step)
    
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
    
    def on_epoch_end(self, epoch, model=None, metrics=None):
        """
        Log metrics at the end of an epoch.
        
        Args:
            epoch (int): Epoch number
            model: PyTorch model (optional)
            metrics (dict): Dictionary of metrics to log
        """
        if metrics:
            epoch_metrics = {f'epoch/{k}': v for k, v in metrics.items()}
            epoch_metrics['epoch'] = epoch
            self.experiment.log(epoch_metrics, step=self.step)
        
        if model and self.log_parameters:
            self._log_parameters(model)
    
    def save_model(self, model, name="model", save_optimizer=None):
        """
        Save a PyTorch model.
        
        Args:
            model: PyTorch model to save
            name (str): Name for the saved model
            save_optimizer: Optimizer to save along with the model (optional)
        
        Returns:
            str: Path to the saved model
        """
        # Create a temporary file to save the model
        with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Save the model
        if save_optimizer:
            torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': save_optimizer.state_dict(),
            }, tmp_path)
        else:
            torch.save(model.state_dict(), tmp_path)
        
        # Log the artifact
        artifact_path = self.experiment.log_artifact(
            name=name,
            file_path=tmp_path,
            metadata={
                'framework': 'pytorch',
                'type': 'model',
                'with_optimizer': save_optimizer is not None
            }
        )
        
        # Clean up the temporary file
        os.unlink(tmp_path)
        
        return artifact_path
