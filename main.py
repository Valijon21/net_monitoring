import sys
import logging
import traceback
from utils import setup_logging, is_admin

# 1. Initialize logging IMMEDIATELY to catch any further errors
setup_logging()
logging.info("--- Starting Application Initializing Sequence ---")

try:
    logging.info("Importing GUI modules...")
    from ui import MainWindow
    from PyQt6.QtWidgets import QApplication
    logging.info("GUI modules imported successfully")
except ImportError as e:
    logging.critical(f"CRITICAL ERROR: Missing dependencies! {e}")
    logging.critical(traceback.format_exc())
    print(f"\n[CRITICAL ERROR] Kutubxonalar topilmadi: {e}")
    print("Iltimos, 'run.bat' orqali kutubxonalarni o'rnating yoki terminalda 'pip install -r requirements.txt' buyrug'ini yozing.\n")
    sys.exit(1)
except Exception as e:
    logging.critical(f"UNEXPECTED ERROR DURING STARTUP: {e}")
    logging.critical(traceback.format_exc())
    sys.exit(1)

def main():
    logging.info("Entering main execution block")
    if not is_admin():
        logging.warning("App running without Admin privileges - blocking features will be limited")
        print("Warning: Administrative privileges not found. Blocking features will be disabled.")

    app = QApplication(sys.argv)
    logging.info("PyQt6 Application instance created")
    
    try:
        window = MainWindow()
        logging.info("Main Window initialized")
        window.show()
        logging.info("Main Window visible")
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"RUNTIME ERROR: {e}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    main()
