# tests/test_all.py
import unittest
from tests.test_core import TestExperiment, TestSystemMonitor
from tests.test_integrations import TestPyTorchIntegration, TestTensorFlowIntegration, TestSklearnIntegration
from tests.test_storage import TestLocalStorage
from tests.test_api import TestAPI
from tests.test_visualization import TestPlotter
from tests.conftest import get_free_port

if __name__ == "__main__":
    unittest.main()
