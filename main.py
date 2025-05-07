from PyQt6 import QtWidgets
import sys
from logic import ProjectWindow 

def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = ProjectWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
