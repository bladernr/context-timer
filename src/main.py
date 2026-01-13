"""Main entry point for Context Timer application."""
import sys
from PyQt6.QtWidgets import QApplication
from .gui import MainWindow


def main():
    """Run the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Context Timer")
    app.setOrganizationName("Context Timer")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
