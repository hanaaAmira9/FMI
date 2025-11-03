import sys
import os
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize

from core.integrity_monitoring import  start_monitoring

from core.gestion_db import insert_folder_and_baseline_for_path, get_connection
from PyQt6.QtCore import QThread, pyqtSignal

class MonitorThread(QThread):
    update_signal = pyqtSignal(str)  # Send messages to GUI

    def run(self):
        try:
            start_monitoring()
            self.update_signal.emit("Monitoring finished")
        except Exception as e:
            self.update_signal.emit(f"Error: {e}")


class MainPage(QWidget):
    def __init__(self, is_dark_theme=False):
        super().__init__()
        self.is_dark_theme = is_dark_theme
        self.sidebar_expanded = False

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Contenu principal avec sidebar
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Sidebar
        self.create_sidebar()
        self.content_layout.addWidget(self.sidebar)

        # Zone principale
        self.main_content = QWidget()
        self.content_layout.addWidget(self.main_content, 1)

        main_layout.addWidget(self.content_widget, 1)

        # Styles
        self.apply_styles()

        # Question auto-start
        QTimer.singleShot(500, self.ask_autostart_question)

    # ---------------- Sidebar ----------------
    def create_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setMinimumWidth(60)
        self.sidebar.setMaximumWidth(350)
        self.sidebar.setFixedWidth(60)

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(8, 15, 8, 15)
        self.sidebar_layout.setSpacing(5)

        # Header
        self.create_sidebar_header()
        self.sidebar_layout.addWidget(self.sidebar_header)

        # Boutons
        self.create_sidebar_buttons()
        self.sidebar_layout.addStretch()
        self.show_sidebar_text(False)

    def create_sidebar_header(self):
        self.sidebar_header = QWidget()
        layout = QHBoxLayout(self.sidebar_header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Logo
        self.logo_label = QLabel()
        pixmap = QPixmap("img/account.png").scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                         Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setFixedSize(32, 32)
        layout.addWidget(self.logo_label)

        # Titre
        self.title_label = QLabel("File Integrity Monitor")
        self.title_label.setFont(QFont("Poppins", 14, QFont.Weight.DemiBold))
        layout.addWidget(self.title_label)

    def create_sidebar_buttons(self):
        """Créer les boutons avec icônes images et actions spécifiques"""
        icon_paths = [
            "img/dashboard.png",
            "img/scanne.png",
            "img/account.png",
            "img/biometrics.png",
            "img/settings.png",
            "img/document.png",
            "img/help-.png"
        ]
        texts = ["Dashboard", "Scanner", "Profil", "Identity", "Settings", "Raports", "Help"]

        self.sidebar_buttons = []
        self.sidebar_texts = texts

        # Définition des actions pour chaque bouton
        actions = [
            self.open_dashboard,
            self.open_scanner,
            self.open_profile,
            self.open_identity,
            self.open_settings,
            self.open_reports,
            self.open_help
        ]

        for i, path in enumerate(icon_paths):
            btn = QPushButton()
            btn.setFixedHeight(50)
            btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            btn.setIcon(QIcon(path))
            btn.setIconSize(QSize(30, 30))

            # Connexion à l'action + toggle sidebar
            btn.clicked.connect(lambda checked, func=actions[i]: [self.toggle_sidebar(), func()])

            self.sidebar_buttons.append(btn)
            self.sidebar_layout.addWidget(btn)

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded

        self.animation_min = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation_max = QPropertyAnimation(self.sidebar, b"maximumWidth")
        for anim in (self.animation_min, self.animation_max):
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuart)

        if self.sidebar_expanded:
            self.animation_min.setStartValue(60)
            self.animation_min.setEndValue(280)
            self.animation_max.setStartValue(60)
            self.animation_max.setEndValue(280)
            self.animation_max.finished.connect(lambda: self.show_sidebar_text(True))
        else:
            self.show_sidebar_text(False)
            self.animation_min.setStartValue(280)
            self.animation_min.setEndValue(60)
            self.animation_max.setStartValue(280)
            self.animation_max.setEndValue(60)

        self.animation_min.start()
        self.animation_max.start()

    def show_sidebar_text(self, show):
        """Afficher ou masquer le texte des boutons"""
        try:
            for i, btn in enumerate(self.sidebar_buttons):
                btn.setText(self.sidebar_texts[i] if show else "")
                btn.setIconSize(QSize(30, 30))
            self.title_label.setVisible(show)
        except Exception as e:
            print(f"Error in show_sidebar_text: {e}")


    # ---------------- Styles ----------------
    def apply_styles(self):
        self.apply_sidebar_style()
        self.apply_main_content_style()

    def apply_sidebar_style(self):
        style = """
            QWidget { background-color: #041240; border: none; }
            QPushButton { background-color: transparent; color: white; border: none; text-align: left; padding: 12px 8px; border-radius: 8px; }
            QPushButton:hover { background-color: #5b6da6; }
        """
        self.sidebar.setStyleSheet(style)

    def apply_main_content_style(self):
        self.main_content.setStyleSheet("background-color: #EDF2FF;")

    # ---------------- Auto-start Question ----------------
    def ask_autostart_question(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Paramètre de démarrage")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(
            "Souhaitez-vous autoriser le lancement automatique de l'application au démarrage de Windows ?"
        )

        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Activer le démarrage automatique")
        msg.button(QMessageBox.StandardButton.No).setText("Lancer manuellement")

        self.apply_theme_to_messagebox(msg)
        result = msg.exec()

        if result == QMessageBox.StandardButton.Yes:
            self.show_confirmation("Le démarrage automatique a été activé avec succès.")
        else:
            self.show_confirmation("Le mode manuel a été sélectionné.")

    def apply_theme_to_messagebox(self, msg_box):
        light_style = """
            QMessageBox { background-color: #FFFFFF; color: #2D3748; }
            QMessageBox QLabel { color: #2D3748; }
            QMessageBox QPushButton {
                background-color: #6A5FF5;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
            }
            QMessageBox QPushButton:hover { background-color: #5A4FDF; }
            QMessageBox QPushButton:pressed { background-color: #4A3FCF; }
        """
        msg_box.setStyleSheet(light_style)

    def show_confirmation(self, message):
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmation")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        self.apply_theme_to_messagebox(msg)
        msg.exec()

    # ---------------- Main Content ----------------
    def create_scanne_content(self):

        layout = QVBoxLayout(self.main_content)
        layout.setContentsMargins(7, 7, 7, 7)
        layout.setSpacing(5)

        # Liste des dossiers/fichiers
        self.files_tree = QTreeWidget()
        self.files_tree.setHeaderLabels(["Nom", "Taille (octets)", "Modifié le", "État"])
        layout.addWidget(self.files_tree)

        # Bouton pour ajouter un dossier
        add_folder_btn = QPushButton("Ajouter un dossier")
        add_folder_btn.clicked.connect(self.add_folder)
        layout.addWidget(add_folder_btn)

    # ---------------- Charger la liste depuis la base ----------------
    def load_folders_and_files(self):
        self.files_tree.clear()
        try:
            conn = get_connection()
            c = conn.cursor()

            try:
                c.execute("SELECT id, path FROM folders WHERE status='active'")
                folders = c.fetchall()
            except Exception as e:
                self.show_confirmation(f"Erreur lors de la lecture des dossiers : {e}")
                return

            for folder_id, folder_path in folders:
                folder_item = QTreeWidgetItem([folder_path, "", "", "Dossier"])
                folder_item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
                folder_item.setBackground(0, Qt.GlobalColor.lightGray)
                self.files_tree.addTopLevelItem(folder_item)

                try:
                    c.execute("SELECT path, size, modified_time FROM baseline WHERE folder_id=?", (folder_id,))
                    files = c.fetchall()
                except Exception as e:
                    self.show_confirmation(f"Erreur lors de la lecture des fichiers du dossier '{folder_path}': {e}")
                    continue

                for file_path, size, mtime in files:
                    if os.path.basename(file_path).startswith("~$"):
                        continue
                    file_name = os.path.basename(file_path)
                    file_item = QTreeWidgetItem([file_name, str(size), mtime, "OK"])
                    file_item.setForeground(3, Qt.GlobalColor.green)
                    folder_item.addChild(file_item)

        except Exception as e:
            self.show_confirmation(f"Erreur de connexion à la base de données : {e}")
        finally:
            try:
                conn.close()
            except:
                pass

        self.files_tree.expandAll()

    # ---------------- Ajouter un dossier ----------------
    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier")
        if folder:
            count = insert_folder_and_baseline_for_path(folder)
            self.show_confirmation(f"{count} fichiers ajoutés depuis {folder}")
            self.load_folders_and_files()

    def clear_main_content(self):
        """Supprime tous les widgets dans la zone principale (hors sidebar)."""
        layout = self.main_content.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    # ---------------- ACTIONS DES BOUTONS ----------------
    def open_dashboard(self):
        self.show_confirmation("Dashboard ouvert !")

    def open_scanner(self):
        self.show_confirmation("Scanner lancé !")
        self.create_scanne_content()

        self.monitor_thread = MonitorThread()
        self.monitor_thread.update_signal.connect(lambda msg: self.show_confirmation(msg))
        self.monitor_thread.start()

        self.load_folders_and_files()

    def open_profile(self):
        self.show_confirmation("Profil ouvert !")

    def open_identity(self):
        self.show_confirmation("Identity ouvert !")

    def open_settings(self):
        self.show_confirmation("Settings ouvert !")

    def open_reports(self):
        self.show_confirmation("Raports ouverts !")

    def open_help(self):
        self.show_confirmation("Help ouvert !")
