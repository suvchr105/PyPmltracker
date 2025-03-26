import threading
import time
import psutil
import platform
import os

class SystemMonitor:
    """Monitor system resources during experiment runs."""
    
    def __init__(self, experiment, interval=5.0):
        """
        Initialize system monitor.
        
        Args:
            experiment: The experiment to log metrics to
            interval (float): Monitoring interval in seconds
        """
        self.experiment = experiment
        self.interval = interval
        self.running = False
        self.thread = None
        self._has_gpu = self._check_gpu()
    
    def _check_gpu(self):
        """Check if GPU monitoring is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            try:
                import tensorflow as tf
                return tf.config.list_physical_devices('GPU')
            except ImportError:
                return False
    
    def _get_gpu_stats(self):
        """Get GPU statistics if available."""
        gpu_stats = {}
        
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    # Get utilization stats using nvidia-smi via subprocess
                    # This is a simplified version
                    gpu_stats[f'gpu_{i}_memory_used_percent'] = torch.cuda.memory_allocated(i) / torch.cuda.max_memory_allocated(i) * 100 if torch.cuda.max_memory_allocated(i) > 0 else 0
        except:
            pass
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            for i, gpu in enumerate(gpus):
                gpu_stats[f'gpu_{i}_utilization'] = gpu.load * 100
                gpu_stats[f'gpu_{i}_memory_used_percent'] = gpu.memoryUtil * 100
        except:
            pass
            
        return gpu_stats
    
    def _monitor(self):
        """Monitoring function that runs in a separate thread."""
        while self.running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_used_percent = memory.percent
                memory_used_gb = memory.used / (1024 ** 3)
                memory_total_gb = memory.total / (1024 ** 3)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_used_percent = disk.percent
                
                # Network stats
                net_io = psutil.net_io_counters()
                
                # System metrics
                metrics = {
                    'system.cpu.percent': cpu_percent,
                    'system.memory.used_percent': memory_used_percent,
                    'system.memory.used_gb': memory_used_gb,
                    'system.memory.total_gb': memory_total_gb,
                    'system.disk.used_percent': disk_used_percent,
                    'system.net.bytes_sent': net_io.bytes_sent,
                    'system.net.bytes_recv': net_io.bytes_recv,
                }
                
                # Add per-core CPU metrics
                for i, core_percent in enumerate(cpu_per_core):
                    metrics[f'system.cpu.core_{i}'] = core_percent
                
                # Add GPU metrics if available
                if self._has_gpu:
                    gpu_stats = self._get_gpu_stats()
                    metrics.update(gpu_stats)
                
                # Log to experiment
                self.experiment.log(metrics)
                
            except Exception as e:
                print(f"Error in system monitoring: {e}")
            
            time.sleep(self.interval)
    
    def start(self):
        """Start the monitoring thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor)
            self.thread.daemon = True
            self.thread.start()
            print("MLTracker: System monitoring started")
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=self.interval + 1.0)
            print("MLTracker: System monitoring stopped")
