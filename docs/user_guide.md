# PyPMLTracker User Guide

## Installation

- **Install the base package:**
```bash
pip install pypmltracker
```

- **Install with optional dependencies:**
```bash
pip install pypmltracker[pytorch,tensorflow,sklearn,cloud]
```

## Quick Start
```bash
**import pypmltracker**
```

**Initialize an experiment**
```bash
experiment = pypmltracker.Experiment(
project_name="my_project",
run_name="first_run",
config={"learning_rate": 0.01, "batch_size": 32}
)
```

**Log metrics**
```bash
experiment.log({"accuracy": 0.85, "loss": 0.35})
```

**Log artifacts**
```bash
experiment.log_artifact("model", "model.pkl")
```

**Finish the experiment**
```bash
experiment.finish()
```

**Visualize results**
```bash
dashboard = pypmltracker.Dashboard()
dashboard.start(open_browser=True)
```



## Framework Integrations

### PyTorch Integration
```bash
import torch
import torch.nn as nn
import pypmltracker

experiment = pypmltracker.Experiment(project_name="pytorch_example")
tracker = pypmltracker.PyTorchTracker(experiment, log_gradients=True)

model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 1))
tracker.watch(model)
```


**Training loop**
```bash
for epoch in range(10):
# Training code here
loss = 0.5 # Your actual loss calculation
tracker.track_metrics({"loss": loss})



# Validation
val_accuracy = 0.8  # Your actual validation
tracker.on_epoch_end(epoch, model, {"val_accuracy": val_accuracy})



Save the final model
tracker.save_model(model, "final_model")
```


### TensorFlow Integration
```bash
import tensorflow as tf
import pypmltracker

experiment = pypmltracker.Experiment(project_name="tensorflow_example")
tracker = pypmltracker.TensorFlowTracker(experiment)

Create and train your TensorFlow model
model = tf.keras.Sequential([
tf.keras.layers.Dense(5, activation='relu', input_shape=(10,)),
tf.keras.layers.Dense(1)
])

Training loop with tracking
tracker.save_model(model, "final_model")
```

### scikit-learn Integration
```bash
from sklearn.linear_model import LogisticRegression
import pypmltracker

experiment = pypmltracker.Experiment(project_name="sklearn_example")
tracker = pypmltracker.SklearnTracker(experiment)

Create and train your scikit-learn model
model = LogisticRegression()
model.fit(X_train, y_train)

Log parameters and metrics
tracker.log_params(model)
tracker.track_metrics({
"accuracy": model.score(X_test, y_test)
})

tracker.save_model(model, "final_model")
```

## System Monitoring
```bash
import pypmltracker
import time

experiment = pypmltracker.Experiment(project_name="system_monitoring")
monitor = pypmltracker.SystemMonitor(experiment)

monitor.start()

for i in range(10):
time.sleep(1)
experiment.log({"step": i, "value": i * 2})

monitor.stop()
experiment.finish()
```

## Team Collaboration

### Server Setup
```bash
import pypmltracker

server = pypmltracker.MLTrackerServer(
storage_dir="./mltracker_data",
host="0.0.0.0",
port=5000
)
server.start()

```

### Client Usage
```bash
import pypmltracker

client = pypmltracker.MLTrackerClient(
base_url="http://server-address:5000"
)
```

List projects
```bash
projects = client.list_projects()
print("Projects:", projects)
```

Get experiment runs
```bash
runs = client.list_runs("my_project")
print("Runs:", runs)
```

Get metrics
```bash
metrics = client.get_metrics("my_project", "first_run")
print("Metrics:", metrics)
```

API Reference
Create an api_reference.md file:
```bash
touch docs/api_reference.md
```


# PyPMLTracker API Reference

## Core Module

### Experiment
```bash
class Experiment:

def init(self, project_name, run_name=None, config=None, storage_dir=None):
"""

    Args:
        project_name (str): Name of the project
        run_name (str, optional): Name of the run. If None, a timestamp will be used.
        config (dict, optional): Configuration parameters for the experiment.
        storage_dir (str, optional): Directory to store experiment data.
    """
    
def log(self, metrics):
    """
    Log metrics for the current experiment.
    
    Args:
        metrics (dict): Dictionary of metric names and values.
    """
    
def log_artifact(self, name, path):
    """
    Log an artifact for the current experiment.
    
    Args:
        name (str): Name of the artifact.
        path (str): Path to the artifact file.
    """
    
def finish(self):
    """
    Finish the experiment and save all data.
    """
```

### SystemMonitor
```bash
class SystemMonitor:
def init(self, experiment, interval=1.0):
"""
    Args:
        experiment (Experiment): The experiment to log system metrics to.
        interval (float): Interval in seconds between measurements.
    """
    
def start(self):
    """
    Start monitoring system resources.
    """
    
def stop(self):
    """
    Stop monitoring system resources.
    """
```

## Integrations Module

### PyTorchTracker
```bash
class PyTorchTracker:
def init(self, experiment, log_gradients=False):
"""
Initialize a PyTorch tracker.

text
    Args:
        experiment (Experiment): The experiment to log to.
        log_gradients (bool): Whether to log gradients.
    """
    
def watch(self, model):
    """
    Watch a PyTorch model.
    
    Args:
        model (torch.nn.Module): The model to watch.
    """
    
def track_metrics(self, metrics):
    """
    Track metrics for the current step.
    
    Args:
        metrics (dict): Dictionary of metric names and values.
    """
    
def on_epoch_end(self, epoch, model, metrics=None):
    """
    Log metrics at the end of an epoch.
    
    Args:
        epoch (int): The epoch number.
        model (torch.nn.Module): The model.
        metrics (dict, optional): Additional metrics to log.
    """
    
def save_model(self, model, name):
    """
    Save a PyTorch model as an artifact.
    
    Args:
        model (torch.nn.Module): The model to save.
        name (str): Name for the saved model.
        
    Returns:
        str: Path to the saved model.
    """
```

### TensorFlowTracker


```bash
class TensorFlowTracker:
def init(self, experiment):
"""
Initialize a TensorFlow tracker.

text
    Args:
        experiment (Experiment): The experiment to log to.
    """
    
def track_metrics(self, metrics):
    """
    Track metrics for the current step.
    
    Args:
        metrics (dict): Dictionary of metric names and values.
    """
    
def save_model(self, model, name):
    """
    Save a TensorFlow model as an artifact.
    
    Args:
        model (tf.keras.Model): The model to save.
        name (str): Name for the saved model.
        
    Returns:
        str: Path to the saved model.
    """
```

### SklearnTracker
```bash
class SklearnTracker:
def init(self, experiment):
"""
Initialize a scikit-learn tracker.

text
    Args:
        experiment (Experiment): The experiment to log to.
    """
    
def log_params(self, model):
    """
    Log model parameters.
    
    Args:
        model: The scikit-learn model.
    """
    
def track_metrics(self, metrics):
    """
    Track metrics for the current step.
    
    Args:
        metrics (dict): Dictionary of metric names and values.
    """
    
def save_model(self, model, name):
    """
    Save a scikit-learn model as an artifact.
    
    Args:
        model: The scikit-learn model to save.
        name (str): Name for the saved model.
        
    Returns:
        str: Path to the saved model.
    """
```

## Visualization Module

### Dashboard
```bash
class Dashboard:
def init(self, storage_dir=None, host="127.0.0.1", port=8000):
"""
Initialize a dashboard for visualizing experiments.

text
    Args:
        storage_dir (str, optional): Directory containing experiment data.
        host (str): Host to bind the dashboard server to.
        port (int): Port to bind the dashboard server to.
    """
    
def start(self, open_browser=True):
    """
    Start the dashboard server.
    
    Args:
        open_browser (bool): Whether to open a browser window.
    """
    
def stop(self):
    """
    Stop the dashboard server.
    """
```

### Plotter
```bash
class Plotter:
def init(self, experiment):
"""
Initialize a plotter for creating visualizations.

text
    Args:
        experiment (Experiment): The experiment to create plots for.
    """
    
def line_plot(self, data, title=None, xlabel=None, ylabel=None, name=None):
    """
    Create a line plot.
    
    Args:
        data (dict): Dictionary of series names and values.
        title (str, optional): Plot title.
        xlabel (str, optional): X-axis label.
        ylabel (str, optional): Y-axis label.
        name (str, optional): Name for the saved plot.
        
    Returns:
        str: Path to the saved plot.
    """
    
def confusion_matrix(self, cm, classes=None, normalize=False, name=None):
    """
    Create a confusion matrix plot.
    
    Args:
        cm (array): Confusion matrix array.
        classes (list, optional): List of class names.
        normalize (bool): Whether to normalize the confusion matrix.
        name (str, optional): Name for the saved plot.
        
    Returns:
        str: Path to the saved plot.
    """
```

## Storage Module

### LocalStorage
```bash
class LocalStorage:
def init(self, base_dir):
"""
Initialize local storage.

text
    Args:
        base_dir (str): Base directory for storing data.
    """
    
def save_run(self, project_name, run_name, run_data):
    """
    Save run information.
    
    Args:
        project_name (str): Name of the project.
        run_name (str): Name of the run.
        run_data (dict): Run data to save.
        
    Returns:
        str: Path to the saved run.
    """
    
def save_metrics(self, project_name, run_name, metrics):
    """
    Save metrics for a run.
    
    Args:
        project_name (str): Name of the project.
        run_name (str): Name of the run.
        metrics (dict): Metrics to save.
        
    Returns:
        str: Path to the saved metrics.
    """
    
def save_artifact(self, project_name, run_name, name, path):
    """
    Save an artifact for a run.
    
    Args:
        project_name (str): Name of the project.
        run_name (str): Name of the run.
        name (str): Name of the artifact.
        path (str): Path to the artifact file.
        
    Returns:
        str: Path to the saved artifact.
    """
```

### S3Storage
```bash
class S3Storage:
def init(self, bucket_name, base_prefix="", aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
"""
Initialize S3 storage.

text
    Args:
        bucket_name (str): Name of the S3 bucket.
        base_prefix (str, optional): Base prefix for S3 keys.
        aws_access_key_id (str, optional): AWS access key ID.
        aws_secret_access_key (str, optional): AWS secret access key.
        region_name (str, optional): AWS region name.
    """
    
def save_run(self, project_name, run_name, run_data):
    """
    Save run information to S3.
    
    Args:
        project_name (str): Name of the project.
        run_name (str): Name of the run.
        run_data (dict): Run data to save.
        
    Returns:
        str: S3 key of the saved run.
    """
    
def save_metrics(self, project_name, run_name, metrics):
    """
    Save metrics for a run to S3.
    
    Args:
        project_name (str): Name of the project.
        run_name (str): Name of the run.
        metrics (dict): Metrics to save.
        
    Returns:
        str: S3 key of the saved metrics.
    """
    
def save_artifact(self, project_name, run_name, name, path):
    """
    Save an artifact for a run to S3.
    
    Args:
        project_name (str): Name of the project.
        run_name (str): Name of the run.
        name (str): Name of the artifact.
        path (str): Path to the artifact file.
        
    Returns:
        str: S3 key of the saved artifact.
    """
```

## API Module

### MLTrackerServer
```bash
class MLTrackerServer:
def init(self, storage_dir=None, host="127.0.0.1", port=5000, api_key=None):
"""
Initialize an MLTracker server.

text
    Args:
        storage_dir (str, optional): Directory containing experiment data.
        host (str): Host to bind the server to.
        port (int): Port to bind the server to.
        api_key (str, optional): API key for authentication.
    """
    
def start(self):
    """
    Start the server.
    """
    
def stop(self):
    """
    Stop the server.
    """
```

### MLTrackerClient
```bash
class MLTrackerClient:
def init(self, base_url, api_key=None):
"""
Initialize an MLTracker client.

text
    Args:
        base_url (str): Base URL of the MLTracker server.
        api_key (str, optional): API key for authentication.
    """
    
def list_projects(self):
    """
    List all projects.
    
    Returns:
        list: List of project names.
    """
    
def list_runs(self, project_name):
    """
    List all runs for a project.
    
    Args:
        project_name (str): Name of the project.
        
    Returns:
        list: List of run information.
    """
    
def get_metrics(self, project_name, run_name):
    """
    Get metrics for a run.
    
    Args:
        project_name (str): Name of the project.
        run_name (str): Name of the run.
        
    Returns:
        dict: Metrics for the run.
    """
    
def get_artifacts(self, project_name, run_name):
    """
    Get artifacts for a run.
    
    Args:
        project_name (str): Name of the project.
        run_name (str): Name of the run.
        
    Returns:
        dict: Artifacts for the run.
    """

```
