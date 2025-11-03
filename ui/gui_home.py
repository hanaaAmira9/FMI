# ui/gui_home.py
import os
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout
from PyQt6.QtGui import QFont, QIcon, QCursor
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve


def get_img_path(filename):
    """Return absolute path to /img/filename."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(base_dir), "img", filename)


class AnimatedButton(QPushButton):
    """Custom QPushButton with hover animation."""
    def __init__(self, text, icon_path=None):
        super().__init__(text)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(36, 36))

        self.setFixedSize(160, 90)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("homeButton")

        # Animation setup
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.setDuration(150)

    def enterEvent(self, event):
        """Zoom in on hover."""
        geo = self.geometry()
        self.anim.stop()
        self.anim.setStartValue(geo)
        self.anim.setEndValue(geo.adjusted(-3, -3, 3, 3))  # slightly bigger
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Zoom out when leaving hover."""
        geo = self.geometry()
        self.anim.stop()
        self.anim.setStartValue(geo)
        self.anim.setEndValue(geo.adjusted(3, 3, -3, -3))
        self.anim.start()
        super().leaveEvent(event)


class MainPage(QWidget):
    def __init__(self, username="User", is_dark_theme=False):
        super().__init__()
        self.username = username
        self.is_dark_theme = is_dark_theme
        self.init_ui(username)
        self.apply_theme()


    def init_ui(self, username):

        self.setObjectName("MainPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(35)

        # --- 🏠 Welcome section ---
        title = QLabel(f"Welcome  to FortiFile <b>{username}</b>")
        title.setFont(QFont("Poppins", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("titleLabel")

        """subtitle = QLabel("Your security workspace is ready.")
        subtitle.setFont(QFont("Poppins", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitleLabel")"""

        desc = QLabel(
            "Manage folders, monitor file integrity, and scan your system for potential threats — all in one place."
        )
        desc.setFont(QFont("Poppins", 11))
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setObjectName("descLabel")

        layout.addWidget(title)
        #layout.addWidget(subtitle)
        layout.addWidget(desc)

        grid = QGridLayout()
        grid.setSpacing(25)
        layout.addLayout(grid)

        buttons_data = [
            ("dashboard.png", "Add Folder"),
            ("scanne.png", "Start Scan"),
            ("dashboard.png", "Dashboard"),
            ("biometrics.png", "Identity"),
            ("account.png", "Profile"),
            ("account.png", "Auto Scan Mode"),
            ("biometrics.png", "About"),
            ("settings.png", "Settings"),
            ("document.png", "Reports"),
        ]

        for i, (img, text) in enumerate(buttons_data):
            btn = AnimatedButton(text, get_img_path(img))
            row, col = divmod(i, 3)
            grid.addWidget(btn, row, col)

        self.buttons = self.findChildren(QPushButton)

    def apply_theme(self):
        """Apply light or dark theme."""
        if self.is_dark_theme:
            self.setStyleSheet("""
                QWidget#MainPage {
                    background-color: #1e1e1e;
                    color: white;
                }
                QPushButton#homeButton {
                    background-color: #2a2a2a;
                    color: #f2f2f2;
                    border: 1px solid #3d3d3d;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 600;
                    transition: all 0.2s ease;
                }
                QPushButton#homeButton:hover {
                    background-color: #3a3a3a;
                    border: 1px solid #666;
                }
                
                QLabel#titleLabel {
                    color: #F0F0F0;
                    font-weight: 800;
                }
                QLabel#subtitleLabel {
                    color: #A0AEC0;
                }
                QLabel#descLabel {
                    color: #CBD5E0;
                }

            """)
        else:
            self.setStyleSheet("""
                QWidget#MainPage {
                    background-color: #FFFFFF;
                    color: #2D3748;
                }
                QPushButton#homeButton {
                    background-color: #FFFFFF;
                    color: #2D3748;
                    border: 1px solid #E0E0E0;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 600;
                    transition: all 0.2s ease;
                }
                QPushButton#homeButton:hover {
                    background-color: #f5f4ff;
                    border: 1px solid #BEBBFF;
                }
                
                QLabel#titleLabel {
                    color: #2D3748;
                    font-weight: 800;
                }
                QLabel#subtitleLabel {
                    color: #4A5568;
                }
                QLabel#descLabel {
                    color: #718096;
                }

            """)


# ✅ Add this to run directly without login
if __name__ == "__main__":
    app = QApplication(sys.argv)
    current_user = "Inna Vin"  # change as needed

    window = MainPage(username=current_user, is_dark_theme=False)

    # Center the window on any screen size
    window.resize(800, 600)
    screen = app.primaryScreen().availableGeometry()
    x = (screen.width() - window.width()) // 2
    y = (screen.height() - window.height()) // 2
    window.move(x, y)

    window.setWindowTitle("FortiFile Home")
    window.setWindowIcon(QIcon(get_img_path("account.png")))
    window.show()

    sys.exit(app.exec())