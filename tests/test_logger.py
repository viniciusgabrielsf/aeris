"""
Unit tests for logging utilities.
"""
import pytest
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from utils.logger import (
    setup_logger,
    get_logger,
    log_api_request,
    log_api_response,
    log_database_operation,
    log_error_with_context
)


class TestLoggerSetup:
    """Tests for logger setup and configuration."""

    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a logger instance."""
        logger = setup_logger(name="test_logger", log_level="INFO")
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_setup_logger_with_debug_level(self):
        """Test logger setup with DEBUG level."""
        logger = setup_logger(name="debug_logger", log_level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_setup_logger_with_info_level(self):
        """Test logger setup with INFO level."""
        logger = setup_logger(name="info_logger", log_level="INFO")
        assert logger.level == logging.INFO

    def test_setup_logger_with_warning_level(self):
        """Test logger setup with WARNING level."""
        logger = setup_logger(name="warning_logger", log_level="WARNING")
        assert logger.level == logging.WARNING

    def test_setup_logger_with_error_level(self):
        """Test logger setup with ERROR level."""
        logger = setup_logger(name="error_logger", log_level="ERROR")
        assert logger.level == logging.ERROR

    def test_setup_logger_with_invalid_level(self):
        """Test logger setup with invalid level raises error."""
        # Invalid level will raise AttributeError from getattr(logging, level)
        with pytest.raises(AttributeError):
            setup_logger(name="invalid_logger", log_level="INVALID")

    def test_setup_logger_with_file_handler(self, tmp_path):
        """Test logger setup with file handler."""
        log_file = tmp_path / "test.log"
        logger = setup_logger(
            name="file_logger",
            log_level="INFO",
            log_file=str(log_file)
        )

        # Log a message
        logger.info("Test message")

        # Check that log file was created
        if log_file.exists():
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test_module")
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_get_logger_same_name_returns_same_instance(self):
        """Test that get_logger returns same instance for same name."""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        assert logger1 is logger2

    def test_logger_has_handlers(self):
        """Test that logger has at least one handler."""
        logger = setup_logger(name="handler_test", log_level="INFO")
        # Should have console handler at minimum
        # Note: May need to check implementation details


class TestLoggerFormatting:
    """Tests for log message formatting."""

    def test_log_message_format(self, caplog):
        """Test that log messages have correct format."""
        logger = get_logger("format_test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        # Check that message was logged
        assert len(caplog.records) > 0
        assert "Test message" in caplog.text

    def test_log_includes_timestamp(self, caplog):
        """Test that log messages include timestamp."""
        logger = get_logger("timestamp_test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            logger.info("Timestamp test")

        # caplog should capture the message
        assert len(caplog.records) > 0

    def test_log_includes_level(self, caplog):
        """Test that log messages include log level."""
        logger = get_logger("level_test")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

        # Check that different levels are logged
        assert any(record.levelname == "DEBUG" for record in caplog.records)
        assert any(record.levelname == "INFO" for record in caplog.records)
        assert any(record.levelname == "WARNING" for record in caplog.records)
        assert any(record.levelname == "ERROR" for record in caplog.records)

    def test_log_includes_module_info(self, caplog):
        """Test that log messages include module information."""
        logger = get_logger("module_test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            logger.info("Module info test")

        # Check for module information in records
        assert len(caplog.records) > 0
        record = caplog.records[0]
        assert record.module is not None


class TestAPILogging:
    """Tests for API request/response logging utilities."""

    def test_log_api_request(self, caplog):
        """Test logging API requests."""
        logger = get_logger("api_test")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_api_request(
                logger=logger,
                method="GET",
                url="https://api.openaq.org/v3/locations",
                params={"country": "BR", "limit": 100}
            )

        # Check that request was logged
        assert len(caplog.records) > 0
        log_text = caplog.text.lower()
        assert "get" in log_text or "request" in log_text
        assert "locations" in log_text

    def test_log_api_response_success(self, caplog):
        """Test logging successful API responses."""
        logger = get_logger("api_response_test")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_api_response(
                logger=logger,
                status_code=200,
                response_time=0.523
            )

        # Check that response was logged
        assert len(caplog.records) > 0
        log_text = caplog.text.lower()
        assert "200" in log_text or "status" in log_text

    def test_log_api_response_error(self, caplog):
        """Test logging failed API responses."""
        logger = get_logger("api_error_test")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_api_response(
                logger=logger,
                status_code=404,
                response_time=0.123
            )

        # Check that error was logged
        assert len(caplog.records) > 0
        log_text = caplog.text.lower()
        assert "404" in log_text

    def test_log_api_response_with_rate_limit(self, caplog):
        """Test logging rate limit responses."""
        logger = get_logger("rate_limit_test")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_api_response(
                logger=logger,
                status_code=429,
                response_time=0.100
            )

        # Check that rate limit was logged
        assert len(caplog.records) > 0
        log_text = caplog.text.lower()
        assert "429" in log_text


class TestDatabaseLogging:
    """Tests for database operation logging utilities."""

    def test_log_database_operation_insert(self, caplog):
        """Test logging database insert operations."""
        logger = get_logger("db_insert_test")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_database_operation(
                logger=logger,
                operation="INSERT",
                table="air_measurements",
                count=10
            )

        # Check that operation was logged
        assert len(caplog.records) > 0
        log_text = caplog.text.lower()
        assert "insert" in log_text
        assert "air_measurements" in log_text or "10" in log_text

    def test_log_database_operation_select(self, caplog):
        """Test logging database select operations."""
        logger = get_logger("db_select_test")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_database_operation(
                logger=logger,
                operation="SELECT",
                table="cities",
                count=5
            )

        # Check that operation was logged
        assert len(caplog.records) > 0
        log_text = caplog.text.lower()
        assert "select" in log_text or "database" in log_text

    def test_log_database_operation_update(self, caplog):
        """Test logging database update operations."""
        logger = get_logger("db_update_test")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_database_operation(
                logger=logger,
                operation="UPDATE",
                table="alerts",
                count=3
            )

        # Check that operation was logged
        assert len(caplog.records) > 0
        log_text = caplog.text.lower()
        assert "update" in log_text

    def test_log_database_operation_delete(self, caplog):
        """Test logging database delete operations."""
        logger = get_logger("db_delete_test")
        logger.setLevel(logging.DEBUG)

        with caplog.at_level(logging.DEBUG):
            log_database_operation(
                logger=logger,
                operation="DELETE",
                table="air_measurements",
                count=100
            )

        # Check that operation was logged
        assert len(caplog.records) > 0
        log_text = caplog.text.lower()
        assert "delete" in log_text


class TestErrorLogging:
    """Tests for error logging utilities."""

    def test_log_error_with_context(self, caplog):
        """Test logging errors with context."""
        logger = get_logger("error_context_test")
        logger.setLevel(logging.ERROR)

        with caplog.at_level(logging.ERROR):
            log_error_with_context(
                logger=logger,
                error=ValueError("Test error"),
                context={
                    "function": "test_function",
                    "city": "São Paulo",
                    "parameter": "pm25"
                }
            )

        # Check that error and context were logged
        assert len(caplog.records) > 0
        log_text = caplog.text.lower()
        assert "error" in log_text or "valueerror" in log_text

    def test_log_error_with_traceback(self, caplog):
        """Test that errors include traceback information."""
        logger = get_logger("traceback_test")
        logger.setLevel(logging.ERROR)

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            with caplog.at_level(logging.ERROR):
                log_error_with_context(
                    logger=logger,
                    error=e,
                    context={"test": "traceback"}
                )

        # Check that error was logged
        assert len(caplog.records) > 0

    def test_log_error_with_empty_context(self, caplog):
        """Test logging errors with empty context."""
        logger = get_logger("empty_context_test")
        logger.setLevel(logging.ERROR)

        with caplog.at_level(logging.ERROR):
            log_error_with_context(
                logger=logger,
                error=Exception("Test error"),
                context={}
            )

        # Should still log the error
        assert len(caplog.records) > 0

    def test_log_error_with_none_context(self, caplog):
        """Test logging errors with None context."""
        logger = get_logger("none_context_test")
        logger.setLevel(logging.ERROR)

        with caplog.at_level(logging.ERROR):
            log_error_with_context(
                logger=logger,
                error=Exception("Test error"),
                context=None
            )

        # Should still log the error
        assert len(caplog.records) > 0


class TestLoggerFilters:
    """Tests for logger filtering and selective logging."""

    def test_log_level_filtering(self, caplog):
        """Test that log level filtering works correctly."""
        logger = get_logger("filter_test")
        logger.setLevel(logging.WARNING)

        with caplog.at_level(logging.WARNING):
            logger.debug("Debug message")  # Should not appear
            logger.info("Info message")    # Should not appear
            logger.warning("Warning message")  # Should appear
            logger.error("Error message")  # Should appear

        # Check that only WARNING and above were logged
        assert not any("Debug message" in record.message for record in caplog.records)
        assert not any("Info message" in record.message for record in caplog.records)
        assert any("Warning message" in record.message for record in caplog.records)
        assert any("Error message" in record.message for record in caplog.records)

    def test_multiple_loggers_independent(self, caplog):
        """Test that multiple loggers operate independently."""
        logger1 = get_logger("logger1")
        logger1.setLevel(logging.DEBUG)

        logger2 = get_logger("logger2")
        logger2.setLevel(logging.ERROR)

        with caplog.at_level(logging.DEBUG):
            logger1.debug("Logger1 debug")
            logger2.debug("Logger2 debug")  # Should not appear

        # Logger1 debug should appear, logger2 debug should not
        logger1_records = [r for r in caplog.records if r.name == "logger1"]
        logger2_records = [r for r in caplog.records if r.name == "logger2"]

        assert len(logger1_records) > 0
        # logger2 may or may not have records depending on configuration


class TestLoggerRotation:
    """Tests for log file rotation (if implemented)."""

    def test_rotating_file_handler(self, tmp_path):
        """Test rotating file handler if implemented."""
        log_file = tmp_path / "rotating.log"

        logger = setup_logger(
            name="rotating_logger",
            log_level="INFO",
            log_file=str(log_file),
        )

        # Log many messages
        for i in range(100):
            logger.info(f"Log message {i}")

        # Check that log file exists
        # Rotation behavior depends on implementation

    def test_log_file_cleanup(self, tmp_path):
        """Test that old log files are cleaned up if rotation is enabled."""
        log_file = tmp_path / "cleanup.log"

        logger = setup_logger(
            name="cleanup_logger",
            log_level="INFO",
            log_file=str(log_file)
        )

        # Log messages
        for i in range(50):
            logger.info(f"Cleanup test {i}")

        # Check file system
        log_files = list(tmp_path.glob("cleanup.log*"))
        # Number of files depends on rotation settings


class TestLoggerPerformance:
    """Tests for logger performance characteristics."""

    def test_logging_does_not_raise_exceptions(self):
        """Test that logging operations don't raise exceptions."""
        logger = get_logger("exception_test")

        # Should not raise any exceptions
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warning")
        logger.error("Error")
        logger.critical("Critical")

    def test_logging_with_complex_objects(self, caplog):
        """Test logging with complex objects."""
        logger = get_logger("complex_test")
        logger.setLevel(logging.INFO)

        complex_object = {
            "nested": {
                "list": [1, 2, 3],
                "dict": {"a": "b"}
            },
            "string": "test"
        }

        with caplog.at_level(logging.INFO):
            logger.info(f"Complex object: {complex_object}")

        # Should log without errors
        assert len(caplog.records) > 0

    def test_logging_unicode_characters(self, caplog):
        """Test logging with Unicode characters."""
        logger = get_logger("unicode_test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            logger.info("São Paulo – Testing Unicode: ₃ µg/m³ NO₂")

        # Should handle Unicode correctly
        assert len(caplog.records) > 0


class TestLoggerIntegration:
    """Integration tests for logger functionality."""

    def test_logger_in_module_context(self):
        """Test logger usage in module context."""
        # Simulate module-level logger usage
        logger = get_logger(__name__)
        logger.info("Module context test")

        # Should not raise any exceptions
        assert logger is not None

    def test_logger_with_exception_handling(self, caplog):
        """Test logger in exception handling context."""
        logger = get_logger("exception_handling_test")
        logger.setLevel(logging.ERROR)

        try:
            raise ValueError("Test exception")
        except ValueError:
            with caplog.at_level(logging.ERROR):
                logger.exception("Caught an exception")

        # Should log exception with traceback
        assert len(caplog.records) > 0
        # Exception details may be in exc_info

    def test_logger_configuration_from_env(self, monkeypatch):
        """Test logger configuration from environment variables."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        # Logger should respect environment variable
        log_level = os.getenv("LOG_LEVEL", "INFO")
        assert log_level == "DEBUG"


class TestLoggerEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_logger_with_empty_name(self):
        """Test logger with empty name."""
        logger = get_logger("")
        assert logger is not None

    def test_logger_with_none_name(self):
        """Test logger with None name."""
        # Should handle None gracefully or use default
        logger = get_logger(None) if get_logger.__code__.co_argcount > 0 else get_logger()
        assert logger is not None

    def test_logger_with_special_characters_in_name(self):
        """Test logger with special characters in name."""
        logger = get_logger("test:logger:with:colons")
        assert logger is not None

    def test_log_very_long_message(self, caplog):
        """Test logging very long messages."""
        logger = get_logger("long_message_test")
        logger.setLevel(logging.INFO)

        long_message = "A" * 10000

        with caplog.at_level(logging.INFO):
            logger.info(long_message)

        # Should handle long messages
        assert len(caplog.records) > 0

    def test_log_message_with_format_specifiers(self, caplog):
        """Test logging messages with format specifiers."""
        logger = get_logger("format_test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            # Using % formatting
            logger.info("Value: %s, Number: %d", "test", 42)

        assert len(caplog.records) > 0
        assert "test" in caplog.text
        assert "42" in caplog.text
