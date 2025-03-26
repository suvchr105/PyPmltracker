# benchmarks/benchmark_logging.py
import time
import os
import shutil
import tempfile
import numpy as np
from pypmltracker import Experiment

def benchmark_logging_speed(num_metrics=100, num_iterations=10):
    """Benchmark logging speed."""
    test_dir = tempfile.mkdtemp()
    
    try:
        # Setup
        experiment = Experiment(
            project_name="benchmark",
            run_name="logging_speed",
            storage_dir=test_dir
        )
        
        # Prepare metrics
        metrics = {f"metric_{i}": 0.0 for i in range(num_metrics)}
        
        # Benchmark
        start_time = time.time()
        
        for i in range(num_iterations):
            # Update metrics with random values
            for key in metrics:
                metrics[key] = np.random.random()
            
            # Log metrics
            experiment.log(metrics)
        
        end_time = time.time()
        
        # Calculate results
        total_time = end_time - start_time
        metrics_per_second = (num_metrics * num_iterations) / total_time
        
        print(f"Logged {num_metrics * num_iterations} metrics in {total_time:.2f} seconds")
        print(f"Metrics per second: {metrics_per_second:.2f}")
        
        return metrics_per_second
    finally:
        # Clean up
        shutil.rmtree(test_dir)

def benchmark_artifact_logging(file_size_mb=10, num_artifacts=5):
    """Benchmark artifact logging speed."""
    test_dir = tempfile.mkdtemp()
    artifact_files = []
    
    try:
        # Create test artifact files
        for i in range(num_artifacts):
            file_path = os.path.join(test_dir, f"artifact_{i}.bin")
            with open(file_path, 'wb') as f:
                f.write(os.urandom(file_size_mb * 1024 * 1024))  # Random data
            artifact_files.append(file_path)
        
        # Setup experiment
        experiment = Experiment(
            project_name="benchmark",
            run_name="artifact_logging",
            storage_dir=test_dir
        )
        
        # Benchmark
        start_time = time.time()
        
        for i, file_path in enumerate(artifact_files):
            experiment.log_artifact(f"artifact_{i}", file_path)
        
        end_time = time.time()
        
        # Calculate results
        total_time = end_time - start_time
        mb_per_second = (file_size_mb * num_artifacts) / total_time
        
        print(f"Logged {num_artifacts} artifacts ({file_size_mb * num_artifacts} MB) in {total_time:.2f} seconds")
        print(f"MB per second: {mb_per_second:.2f}")
        
        return mb_per_second
    finally:
        # Clean up
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    print("=== Benchmarking Metric Logging ===")
    benchmark_logging_speed(num_metrics=100, num_iterations=10)
    benchmark_logging_speed(num_metrics=1000, num_iterations=5)
    
    print("\n=== Benchmarking Artifact Logging ===")
    benchmark_artifact_logging(file_size_mb=10, num_artifacts=5)
    benchmark_artifact_logging(file_size_mb=50, num_artifacts=2)
