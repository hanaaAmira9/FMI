from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.is_dark_theme = False

        # Layout principal vertical (Header + Content)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- HEADER (menu horizontal) ---
        self.create_header_menu()

        # --- Zone centrale (StackedWidget pour les pages) ---
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # Pages
        self.home_page = None
        self.dashboard_page = None
        self.scan_page = None
        self.settings_page = None
        self.load_home(username="User")

        # Taille de la fenêtre
        self.setMinimumSize(1000, 600)

    def create_header_menu(self):
        """Menu horizontal dans le header"""
        self.header = QWidget()
        self.header.setFixedHeight(60)
        self.header.setStyleSheet("background-color: #151B54;")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(15)

        # Logo
        logo_label = QLabel("FortiFile")
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: white;")
        header_layout.addWidget(logo_label)

        # Menu horizontal
        self.menu_buttons = []
        menu_items = [
            ("Home", "scanner"),
            ("Dashboard", "dashboard"),
            ("Identity", "identity"),
            ("Settings", "setting"),
            ("Help", "question"),
            ("About", "about")
        ]
        for text, btn_id in menu_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("button_id", btn_id)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    font-weight: normal;
                }
                QPushButton:checked {
                    background-color: #5A4FDF;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #3A3A8D;
                }
            """)
            btn.clicked.connect(lambda checked, b=btn: self.on_nav_button_clicked(b))
            self.menu_buttons.append(btn)
            header_layout.addWidget(btn)

        header_layout.addStretch()
        self.main_layout.addWidget(self.header)

    def load_home(self, username):
        if self.home_page is None:
            from ui.gui_home import MainPage
            self.home_page = MainPage(username=username, is_dark_theme=False)
            self.stack.addWidget(self.home_page)
        self.stack.setCurrentWidget(self.home_page)

    def load_dashboard(self, username):
        if self.dashboard_page is None:
            from ui.gui_dashboard import DashboardPage
            self.dashboard_page = DashboardPage(username=username)
            self.stack.addWidget(self.dashboard_page)
        self.stack.setCurrentWidget(self.dashboard_page)

    def load_scan(self, username):
        if self.scan_page is None:
            from ui.gui_scanner import ScanPage
            self.scan_page = ScanPage(username=username)
            self.stack.addWidget(self.scan_page)
        self.stack.setCurrentWidget(self.scan_page)

    def load_setting(self, username):
        if self.settings_page is None:
            from ui.gui_settings import SettingsPage
            self.settings_page = SettingsPage(username=username)
            self.stack.addWidget(self.settings_page)
        self.stack.setCurrentWidget(self.settings_page)

    def on_nav_button_clicked(self, clicked_button):
        # Décocher tous les autres boutons
        for btn in self.menu_buttons:
            btn.setChecked(False)
        clicked_button.setChecked(True)

        button_id = clicked_button.property("button_id")
        # Charger la page correspondante
        if button_id == "scanner":
            self.load_home("User")
        elif button_id == "dashboard":
            self.load_dashboard("User")
        elif button_id == "identity":
            self.load_scan("User")
        elif button_id == "setting":
            self.load_setting("User")
        elif button_id == "question":
            print("Help page pas encore implémentée")
        elif button_id == "about":
            print("About page pas encore implémentée")
