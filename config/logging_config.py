import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import os

# Base directory for the project
BASE_DIR = Path(__file__).parent.parent.resolve()
LOGS_DIR = BASE_DIR / "logs"

def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Set up centralized logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to files
        log_to_console: Whether to log to console
        max_file_size: Maximum size of log files before rotation
        backup_count: Number of backup files to keep
    """
    
    # Ensure logs directory exists
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if log_to_file:
        # Main application log
        app_log_file = LOGS_DIR / "app.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        app_handler.setLevel(numeric_level)
        app_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(app_handler)
        
        # Error log (only errors and above)
        error_log_file = LOGS_DIR / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # API access log
        api_log_file = LOGS_DIR / "api.log"
        api_handler = logging.handlers.RotatingFileHandler(
            api_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(detailed_formatter)
        
        # Create API logger
        api_logger = logging.getLogger("api")
        api_logger.setLevel(logging.INFO)
        api_logger.addHandler(api_handler)
        api_logger.propagate = False  # Don't propagate to root logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def log_system_info():
    """Log system information at startup."""
    logger = get_logger(__name__)
    logger.info("=" * 60)
    logger.info("Generic RAG System Starting")
    logger.info("=" * 60)
    logger.info(f"Python version: {os.sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Logs directory: {LOGS_DIR}")
    logger.info(f"Log files: {list(LOGS_DIR.glob('*.log'))}")
    logger.info("=" * 60)

# Initialize logging when module is imported
if __name__ != "__main__":
    # Set up logging with environment variable overrides
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    log_to_console = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
    
    setup_logging(
        log_level=log_level,
        log_to_file=log_to_file,
        log_to_console=log_to_console
    )
