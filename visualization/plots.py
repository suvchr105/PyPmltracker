import matplotlib.pyplot as plt
import numpy as np
import io
import os
from PIL import Image

class Plotter:
    """Utility for creating and logging plots."""
    
    def __init__(self, experiment):
        """
        Initialize plotter.
        
        Args:
            experiment: The experiment to log plots to
        """
        self.experiment = experiment
    
    def line_plot(self, data, x=None, y=None, title=None, xlabel=None, ylabel=None, name="plot"):
        """
        Create and log a line plot.
        
        Args:
            data: DataFrame or dictionary of data
            x: x-axis column/key
            y: y-axis column/key or list of columns/keys
            title: Plot title
            xlabel: x-axis label
            ylabel: y-axis label
            name: Name for the saved plot
        
        Returns:
            str: Path to the saved plot
        """
        plt.figure(figsize=(10, 6))
        
        if hasattr(data, 'plot'):  # DataFrame
            if y is None:
                data.plot(x=x)
            else:
                if isinstance(y, (list, tuple)):
                    data.plot(x=x, y=y)
                else:
                    data.plot(x=x, y=y)
        else:  # Dictionary
            if x is None:
                x = list(range(len(next(iter(data.values())))))
            
            if y is None:
                y = list(data.keys())
            elif not isinstance(y, (list, tuple)):
                y = [y]
            
            for key in y:
                if key in data:
                    plt.plot(x, data[key], label=key)
        
        if title:
            plt.title(title)
        if xlabel:
            plt.xlabel(xlabel)
        if ylabel:
            plt.ylabel(ylabel)
        
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save plot to a temporary file
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        
        # Create a temporary file
        tmp_dir = os.path.join(self.experiment.run_dir, "plots")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, f"{name}.png")
        
        # Save the image
        img = Image.open(buf)
        img.save(tmp_path)
        
        # Log the plot as an artifact
        artifact_path = self.experiment.log_artifact(
            name=f"plot_{name}",
            file_path=tmp_path,
            metadata={
                'type': 'plot',
                'format': 'png'
            }
        )
        
        plt.close()
        
        return artifact_path
    
    def confusion_matrix(self, cm, classes=None, normalize=False, title='Confusion Matrix', name="confusion_matrix"):
        """
        Create and log a confusion matrix plot.
        
        Args:
            cm: Confusion matrix array
            classes: List of class names
            normalize: Whether to normalize the confusion matrix
            title: Plot title
            name: Name for the saved plot
        
        Returns:
            str: Path to the saved plot
        """
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        plt.figure(figsize=(10, 8))
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title(title)
        plt.colorbar()
        
        if classes:
            tick_marks = np.arange(len(classes))
            plt.xticks(tick_marks, classes, rotation=45)
            plt.yticks(tick_marks, classes)
        
        fmt = '.2f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(j, i, format(cm[i, j], fmt),
                        horizontalalignment="center",
                        color="white" if cm[i, j] > thresh else "black")
        
        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        
        # Save plot to a temporary file
        tmp_dir = os.path.join(self.experiment.run_dir, "plots")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, f"{name}.png")
        
        plt.savefig(tmp_path, format='png', dpi=100)
        
        # Log the plot as an artifact
        artifact_path = self.experiment.log_artifact(
            name=f"plot_{name}",
            file_path=tmp_path,
            metadata={
                'type': 'plot',
                'format': 'png',
                'plot_type': 'confusion_matrix'
            }
        )
        
        plt.close()
        
        return artifact_path
