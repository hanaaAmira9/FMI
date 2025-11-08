import sys , os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QComboBox, QCheckBox,
    QGridLayout, QScrollArea, QDateEdit, QInputDialog, QMessageBox,
    QSplitter, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QDate, Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon , QFont
from plyer.platforms.win.libs.wifi_defs import connect

# NOTE: Assurez-vous d'avoir une structure 'core/user_manager.py' fonctionnelle
from core.user_manager import (
    load_current_user, get_email_by_username, get_hashed_password_by_username,
    get_date_of_birth_by_username, edit_user, hash_password, list_users
)
from ui.gui_file_user import FileSelectionDialog

# --- Constantes pour l'animation ---
SIDEBAR_WIDTH_MIN = 0
SIDEBAR_WIDTH_MAX = 220
ANIMATION_DURATION = 300

# --- Structure de Données ---
BUTTONS_DATA = [
    ("Personal Info", "icons/user_icon.png"),
    ("Security", "icons/lock_icon.png"),
    ("Roles", "icons/users_icon.png"),
]

# --- Stylesheet (Inchangé) ---
LIGHT_STYLESHEET = """
    /* 🌞 --- Thème Clair Global --- */
    QMainWindow, QWidget {
        background-color: #F9F9F9;
        color: #1E1E1E;
        border: none;
        font-family: "Segoe UI", Arial, sans-serif;
    }

    /* ---------------- Header ---------------- */
    #Header {
        background-color: #E6E6E6;
        padding: 10px;
        border-bottom: 1px solid #D0D0D0;
    }
    #header_label {
       font-size: 24px; font-weight: bold; color: #2301C0;
    }
   
    QDateEdit {
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 15px;
        background-color: #fff;
        color: #1E1E1E;
        selection-background-color: #2301C0;
        selection-color: white;
    }
    QDateEdit:focus {
        border: 1px solid #2301C0;
    }
    QDateEdit::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid #ccc;
    }

    #subtitle {
     font-size: 15pt; 
     font-weight: bold;
     color: black;
     margin-top: 15px;
    }

    /* ---------------- Footer ---------------- */
    #Footer {
        background-color: #E6E6E6;
        padding: 8px;
        border-top: 1px solid #D0D0D0;
    }

    #SettingsButton {
        background-color: transparent;
        border: none;
        color: #1E1E1E;
        font-size: 18pt;
        padding: 5px 10px;
    }
    #SettingsButton:hover {
        color: #2301C0;
    }

    /* ---------------- Sidebar ---------------- */
    #Sidebar {
        background-color: #F0F0F0;
        border-right: 1px solid #D0D0D0;
    }

    #Sidebar QPushButton {
        background-color: transparent;
        border: none;
        color: #1E1E1E;
        text-align: left;
        padding: 14px 12px;
        font-size: 11pt;
    }

    #Sidebar QPushButton:hover {
        background-color: #E0E0E0;
        border-left: 5px solid #2301C0;
    }

    #Sidebar QPushButton:checked {
        background-color: #2301C0;
        color: white;
        font-weight: bold;
        border-left: 5px solid #2301C0;
    }
    #Sidebar QPushButton[text=""] {
        text-align: center; 
    }

    /* ---------------- Contenu Principal ---------------- */
    #ContentArea {
        padding: 20px;
    }

    /* ---------------- QLabel ---------------- */
    QLabel {
        color: #1E1E1E;
        font-size: 14pt;
    }

    QLabel[property="title"] {
        font-size: 15pt;
        font-weight: bold;
        color: #000;
        margin-bottom: 15px;
    }

    QLabel[property="subtitle"] {
        font-size: 16pt;
        color: #333;
        margin-top: 10px;
        margin-bottom: 5px;
    }


    /* ---------------- QLineEdit ---------------- */
    QLineEdit {
        border: 1px solid #CCC;
        border-radius: 6px;
        padding: 10px;
        font-size: 15px;
        background-color: white;
        color: #1E1E1E;
    }
    QLineEdit:focus {
        border: 1px solid #2301C0;
        background-color: #FDFDFE;
    }

    /* ---------------- QPushButton (principal) ---------------- */
    QPushButton#saveButton {
        background-color: #2301C0;
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-size: 15px;
        font-weight: bold;
    }
    QPushButton#saveButton:hover {
        background-color: #120A37;
    }

    /* ---------------- QPushButton (secondaire) ---------------- */
    QPushButton#grayButton {
        background-color: #E0E0E0;
        color: #1E1E1E;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }
    QPushButton#grayButton:hover {
        background-color: #D0D0D0;
    }
     QLabel {
        font-size: 12pt;
        color: #1E1E1E;
    }
    QLabel[property="property"] {
        font-weight: bold;
    }
    
    QGridLayout {
        spacing: 10px;
    }
    QWidget {
        background-color: #FAFAFA;
        border-radius: 6px;
        padding: 10px;
    }
    QTableWidget[role="Admin"] {
        color: red ;
        font-weight: bold;
    }

"""


class SettingsPage(QWidget):
    def __init__(self, username="User"):
        super().__init__()
        self.username = load_current_user()

        self.setStyleSheet(LIGHT_STYLESHEET)

        app_layout = QVBoxLayout(self)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(0)



        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        app_layout.addLayout(body_layout)

        self.create_sidebar(body_layout)

        self.create_content_area(body_layout)

        self.create_footer(app_layout)

        self.setup_animation()
        self.setup_connections()

        # Initialisation: la barre latérale commence fermée sur la page d'accueil (index 0)
        self.stacked_widget.setCurrentIndex(0)
        self.update_button_text()



    def create_footer(self, parent_layout):
        footer_widget = QWidget()
        footer_widget.setObjectName("Footer")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)

        self.settings_button = QPushButton("⚙️")
        self.settings_button.setObjectName("SettingsButton")
        self.settings_button.setFixedSize(QSize(40, 40))

        footer_layout.addWidget(self.settings_button)
        footer_layout.addStretch(1)

        parent_layout.addWidget(footer_widget)

    def create_sidebar(self, parent_layout):
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("Sidebar")
        self.sidebar_widget.setFixedWidth(SIDEBAR_WIDTH_MIN)

        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.buttons = []
        for text, icon_path in BUTTONS_DATA:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setMinimumHeight(45)

            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(20, 20))

            btn.full_text = text
            self.buttons.append(btn)
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch(1)
        parent_layout.addWidget(self.sidebar_widget)

    def create_content_area(self, parent_layout):
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("ContentArea")

        # Index 0: Page d'accueil (pour l'état initial "fermé")
        self.stacked_widget.addWidget(self._create_welcome_page())

        # Index 1: Personal Info (premier bouton de la sidebar)
        self.stacked_widget.addWidget(self._create_personal_info_page())

        # Index 2: Security
        self.stacked_widget.addWidget(self._create_security_page())


        # Index 3: Roles
        self.stacked_widget.addWidget(self._create_roles_page())

        parent_layout.addWidget(self.stacked_widget)

    # --- Pages de Contenu ---

    def _create_roles_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        container = QWidget()
        main_layout = QVBoxLayout(container)

        # --- Titre ---
        header_label = QLabel("Roles Management")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2301C0;")
        main_layout.addWidget(header_label)

        # --- Sous-titre ---
        subtitle = QLabel(
            "Overview of all application users and their assigned roles ."
        )
        subtitle.setStyleSheet("font-size: 15pt; color: #333; margin-bottom: 10px;")
        main_layout.addWidget(subtitle)
        bar = QWidget()
        main_layout.addWidget(bar)
        top_bar = QHBoxLayout(bar)
        top_bar.setSpacing(10)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select folder here...")
        self.path_edit.setReadOnly(True)
        self.path_edit.setFixedHeight(40)
        self.btn = QPushButton("Browse File")
        self.btn.setObjectName("saveButton")
        self.btn.clicked.connect(self.add_file)
        top_bar.addWidget(self.path_edit, stretch=1)
        top_bar.addWidget(self.btn, stretch=0)
        self.defaultLabel = QLabel("Default List : ")
        main_layout.addWidget(self.defaultLabel)
        # --- Splitter horizontal ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # --- Table des utilisateurs ---
        self.table = QTableWidget()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Username", "Email", "Role"])

        # --- Configuration des colonnes ---
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # --- Apparence générale ---
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)

        # --- Style simple avec coins arrondis ---
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fafafa;
                alternate-background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                gridline-color: #bbb;
                font-size: 13px;
            }

           

            QTableWidget::item:selected {
                background-color: #d0d7ff;
                color: black;
            }
        """)

        # Remplir le tableau (list_users doit retourner une liste de dicts)
        users = list_users() or []
        for user in users:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(user.get("username", "")))
            self.table.setItem(row_position, 1, QTableWidgetItem(user.get("email", "")))
            self.table.setItem(row_position, 2, QTableWidgetItem(user.get("role", "")))

        splitter.addWidget(self.table)
        main_layout.addStretch()


        splitter.setSizes([400, 150])  # Largeur initiale des panneaux
        btn_change = QPushButton("Change role")
        btn_change.setObjectName("saveButton")
        main_layout.addWidget(btn_change, alignment=Qt.AlignmentFlag.AlignRight)
        page.setWidget(container)
        return page

    def add_file(self):
        dialog = FileSelectionDialog(folder_path=".", is_dark_theme=False, parent=self)
        result = dialog.exec()  # ← bloque jusqu’à ce que l’utilisateur ferme le dialog
        if result == QDialog.DialogCode.Accepted:
            file = dialog.selected_file
            print("Fichier choisi :", file)
            self.path_edit.setText(file)
            # ici tu peux faire ce que tu veux avec ce fichier

    def after_file_selected(self):
        # Récupère le fichier sélectionné
        selected = getattr(self.file_window, "selected_file", None)
        if selected:
            print(selected)
            self.path_edit.setText(selected)

    def change_role(self, user, role_label):
        # Exemple simple : toggle User <-> Admin
        if user.get('role') == "UserStandard":
            user['role'] = "Admin"
        else:
            user['role'] = "UserStandard"
        role_label.setText(user['role'])

    def _create_welcome_page(self):
        page = QWidget()
        page.setLayout(QVBoxLayout())
        header_label = QLabel("Welcome to Settings")
        header_label.setProperty("property", "title")
        page.layout().addWidget(header_label)
        page.layout().addWidget(QLabel("Click the ⚙️ icon to open the **Settings** sidebar and navigate."))
        page.layout().addStretch(1)
        return page

    def _create_generic_page(self, title, content_text):
        page = QWidget()
        layout = QVBoxLayout(page)
        header_label = QLabel(title)
        header_label.setProperty("property", "title")
        layout.addWidget(header_label)
        layout.addWidget(QLabel(content_text))
        layout.addStretch(1)
        return page

    def _create_personal_info_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        container = QWidget()
        self.layout_personal_info = QVBoxLayout(container)

        header_label = QLabel("Personal Information")
        header_label.setProperty("property", "title")
        header_label.setObjectName("header_label")
        self.layout_personal_info.addWidget(header_label)

        subtitle1 = QLabel("User Identification")
        subtitle1.setObjectName("subtitle")
        subtitle1.setProperty("property", "subtitle")
        self.layout_personal_info.addWidget(subtitle1)

        self.grid_personal_info = QGridLayout()

        self.grid_personal_info.addWidget(QLabel("Username:"), 0, 0)
        self.usernameEdit = QLineEdit(f"{self.username}")
        self.usernameEdit.setReadOnly(True)
        self.grid_personal_info.addWidget(self.usernameEdit, 0, 1)

        self.grid_personal_info.addWidget(QLabel("Email Address:"), 1, 0)
        self.emaiEdit = QLineEdit(get_email_by_username(self.username))
        self.emaiEdit.setReadOnly(True)
        self.grid_personal_info.addWidget(self.emaiEdit, 1, 1)

        self.grid_personal_info.addWidget(QLabel("Date of Birth:"), 2, 0)
        self.dobEdit = QDateEdit()
        self.dobEdit.setCalendarPopup(True)
        self.dobEdit.setDisplayFormat("yyyy-MM-dd")
        self.dobEdit.setReadOnly(True)

        dob_str = get_date_of_birth_by_username(self.username)

        if dob_str and dob_str != "N/A":
            try:
                year, month, day = map(int, dob_str.split("-"))
                self.dobEdit.setDate(QDate(year, month, day))
            except ValueError:
                self.dobEdit.setDate(QDate(2000, 1, 1))
        else:
            self.dobEdit.setDate(QDate(2000, 1, 1))

        self.grid_personal_info.addWidget(self.dobEdit, 2, 1)

        self.edit_btn = QPushButton("Edit Profil")
        self.edit_btn.setObjectName("saveButton")
        self.edit_btn.clicked.connect(self.edit_func)

        self.layout_personal_info.addLayout(self.grid_personal_info)

        self.button_container = QHBoxLayout()
        self.button_container.addStretch(1)
        self.button_container.addWidget(self.edit_btn)
        self.layout_personal_info.addLayout(self.button_container)




        self.layout_personal_info.addStretch(1)
        page.setWidget(container)
        return page

    # --- Méthodes de Logique (edit_func, cancel_edit, etc.) ---

    def edit_func(self):

        if self.edit_btn.text().strip() == "Edit Profil":
            self.usernameEdit.setReadOnly(False)
            self.emaiEdit.setReadOnly(False)
            self.dobEdit.setReadOnly(False)

            self.edit_btn.setText("Save")
            self.cancel_btn = QPushButton("Cancel")
            self.cancel_btn.setObjectName("grayButton")
            self.cancel_btn.clicked.connect(self.cancel_edit)

            self.button_container.insertWidget(0, self.cancel_btn)

        elif self.edit_btn.text().strip() == "Save" :

            password, ok = QInputDialog.getText(self, "Confirm Password",
                                                 "Enter your current password: ")


            if  password and ok:
                hashed_password_stored = get_hashed_password_by_username(self.username)

                if hashed_password_stored == hash_password(password):

                    new_username = self.usernameEdit.text().strip()
                    new_email = self.emaiEdit.text().strip()

                    dob = self.dobEdit.date()

                    edit_user( new_username, new_email, password, dob.toString("yyyy-MM-dd"))

                    self.username = new_username

                    QMessageBox.information(self, "Success", "Profile updated successfully!")

                    self.finish_edit_mode()
                else:

                    QMessageBox.warning(self, "Error", "Incorrect password! Changes not saved.")
            else:

                QMessageBox.warning(self, "Error", "Incorrect passwo   rd! Changes not saved.")

    def cancel_edit(self):
        self.usernameEdit.setText(self.username)
        self.emaiEdit.setText(get_email_by_username(self.username))

        dob_str = get_date_of_birth_by_username(self.username)
        if dob_str:
            try:
                year, month, day = map(int, dob_str.split("-"))
                self.dobEdit.setDate(QDate(year, month, day))
            except ValueError:
                self.dobEdit.setDate(QDate(2000, 1, 1))
        else:
            self.dobEdit.setDate(QDate(2000, 1, 1))

        self.finish_edit_mode()

    def finish_edit_mode(self):
        self.usernameEdit.setReadOnly(True)
        self.emaiEdit.setReadOnly(True)
        self.dobEdit.setReadOnly(True)

        self.edit_btn.setText("Edit Profil")

        if hasattr(self, "cancel_btn") and self.cancel_btn.parent():
            self.button_container.removeWidget(self.cancel_btn)
            self.cancel_btn.deleteLater()

    def _create_security_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        container = QWidget()
        self.layout = QVBoxLayout(container)

        header_label = QLabel("Security")
        header_label.setObjectName("header_label")
        header_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2301C0;
        """)

        header_label.setProperty("property", "title")
        header_label.setObjectName("header_Label")
        self.layout.addWidget(header_label)
        self.create_password_section()
        self.create_history_section()
        self.layout.addStretch(1)
        page.setWidget(container)
        return page

    def create_settings_section(self, title, widgets, open_by_default=False):
        """Crée une section pliable avec un bouton et des détails."""
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)

        # Bouton principal
        btn = QPushButton(f"{'🔽' if open_by_default else '▶️'} {title}")
        btn.setStyleSheet("""
            QPushButton { 
    text-align: left; 
    padding: 12px; 
 
    border: #d8d7de; 
    border-radius: 5px; 
    color: black ; 
    font-size: 14pt;   /* taille de la police */
    font-weight: bold; /* texte gras */
}
      """  )
        section_layout.addWidget(btn)

        # Widget détails
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(20, 5, 5, 5)
        details_layout.setSpacing(10)

        for w in widgets:
            details_layout.addWidget(w)

        details_widget.setVisible(open_by_default)
        section_layout.addWidget(details_widget)

        # Connecter toggle
        btn.clicked.connect(lambda: self.toggle_section(btn, details_widget))

        self.layout.addWidget(section_widget)
        return details_widget

    def toggle_section(self, button, details_widget):
        visible = details_widget.isVisible()
        details_widget.setVisible(not visible)
        # Changer icône
        text = button.text()
        if visible:
            text = text.replace("🔽", "▶️")
        else:
            text = text.replace("▶️", "🔽")
        button.setText(text)

    def create_password_section(self):
        # Champs
        current_pwd = QLineEdit()
        current_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        current_pwd.setPlaceholderText("Current Password")

        new_pwd = QLineEdit()
        new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        new_pwd.setPlaceholderText("New Password")

        confirm_pwd = QLineEdit()
        confirm_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_pwd.setPlaceholderText("Confirm Password")

        # Boutons
        btn_save = QPushButton("Save")
        btn_save.setObjectName("saveButton")
        btn_save.clicked.connect(lambda: QMessageBox.information(self, "Saved", "Password saved!"))
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("saveButton")
        btn_cancel.clicked.connect(lambda: QMessageBox.information(self, "Cancelled", "Action cancelled!"))

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        btn_container = QWidget()
        btn_container.setLayout(btn_layout)

        # Créer section (ouverte par défaut)
        self.create_settings_section("Password", [current_pwd, new_pwd, confirm_pwd, btn_container],
                                     open_by_default=True)

    def create_history_section(self):
        list_widget = QListWidget()
        log_folder = "./logs"
        if os.path.exists(log_folder):
            for f in os.listdir(log_folder):
                if os.path.isfile(os.path.join(log_folder, f)):
                    list_widget.addItem(f)

        # Section fermée par défaut
        self.create_settings_section("Historique", [list_widget], open_by_default=False)

    def setup_animation(self):
        self.animation = QPropertyAnimation(self.sidebar_widget, b"minimumWidth")
        self.animation.setDuration(ANIMATION_DURATION)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.sidebar_widget.setMinimumWidth(SIDEBAR_WIDTH_MIN)
        self.is_sidebar_open = False

        self.animation.finished.connect(self.update_button_text)

    def setup_connections(self):
        self.settings_button.clicked.connect(self.toggle_sidebar)

        for index, btn in enumerate(self.buttons):
            # Index + 1 car l'index 0 est la page de bienvenue
            btn.clicked.connect(lambda checked, i=index + 1, b=btn: self.switch_page(i, b))

        for btn in self.buttons:
            btn.setChecked(False)

    def toggle_sidebar(self):
        """Lance l'animation pour ouvrir ou fermer la sidebar."""

        if self.is_sidebar_open:
            # Animation de fermeture
            target_width = SIDEBAR_WIDTH_MIN
            start_width = SIDEBAR_WIDTH_MAX
            self.is_sidebar_open = False

            # Optionnel: Revenir à la page d'accueil (index 0) lors de la fermeture
            # self.stacked_widget.setCurrentIndex(0)
            # for btn in self.buttons: btn.setChecked(False)

        else:
            # Animation d'ouverture
            target_width = SIDEBAR_WIDTH_MAX
            start_width = SIDEBAR_WIDTH_MIN
            self.is_sidebar_open = True

            # CORRECTION: Ouvrir la sidebar et sélectionner la page "Personal Info" (Index 1)
            self.switch_page(1, self.buttons[0])

        self.animation.setStartValue(start_width)
        self.animation.setEndValue(target_width)

        if not self.is_sidebar_open:
            self.update_button_text()

        self.animation.start()

    def update_button_text(self):
        """Met à jour le texte des boutons de la sidebar (Icône seule vs Icône + Texte)."""
        width = self.sidebar_widget.minimumWidth()

        if width <= SIDEBAR_WIDTH_MIN:
            for btn in self.buttons:
                btn.setText("")
                btn.setToolTip(btn.full_text)

        else:
            for btn in self.buttons:
                btn.setText(f" {btn.full_text}")
                btn.setToolTip("")

    def switch_page(self, index, clicked_button):
        for btn in self.buttons:
            btn.setChecked(False)

        clicked_button.setChecked(True)

        self.stacked_widget.setCurrentIndex(index)


if __name__ == "__main__":
    # Assurez-vous d'avoir une icône nommée 'icons/user_icon.png' ou changez les chemins dans BUTTONS_DATA.
    # Pour tester rapidement, vous pouvez définir une icône par défaut si les fichiers manquent.
    if not QIcon("icons/user_icon.png").isNull():
        print("Icônes trouvées. Démarrage de l'application.")
    else:
        print("AVERTISSEMENT: Icônes non trouvées. Les boutons n'auront pas d'images.")

    app = QApplication(sys.argv)

    main_window = QMainWindow()

    settings_widget = SettingsPage()
    main_window.setCentralWidget(settings_widget)

    main_window.setWindowTitle("Modern Settings Panel")
    main_window.setGeometry(100, 100, 800, 600)

    main_window.show()
    sys.exit(app.exec())