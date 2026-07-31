import sys
import traceback

from PySide6.QtWidgets import QApplication

from app.application import Application
from core.logging import configure_logging, get_logger
from database.initialization import initialize_database

logger = get_logger(__name__)


def main() -> int:
    configure_logging()
    logger.info("Application startup initiated")

    try:
        initialize_database()
        app = QApplication(sys.argv)
        main_app = Application()
        main_app.run()
        exit_code = app.exec()
        logger.info("Application shutdown completed")
        return exit_code
    except Exception:
        logger.exception("Unhandled exception during application execution")
        raise


if __name__ == "__main__":
    sys.excepthook = lambda exc_type, exc_value, exc_tb: (
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))
        or None
    )
    sys.exit(main())
