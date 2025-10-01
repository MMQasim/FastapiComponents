import pytest
from fastapicomponents.common_util.AppLogger import AppLogger


class TestSetup:
    def setup_method(self) -> None:
        pass

    def test_setup(self) -> None:
        # Example test to check if setup is working
        logger_instance = AppLogger(name="TestLogger", log_file="test_app.log")
        logger = logger_instance.get_logger()
        assert logger.name == "TestLogger"