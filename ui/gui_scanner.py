import os
import json
from PyQt6.QtGui import QFont, QPixmap, QIcon, QColor , QAction
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from integrityCode import  build_baseline_for_folder
from core.config_manager import get_mode , update_mode

class ScanPage(QWidget):
    def __init__(self, username="User"):
        super().__init__()
        self.username = username

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # --- Top Bar ---
        self._setup_top_bar(self.main_layout)

        # --- Splitter ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        self.labelScan = QLabel()
        self.main_layout.addWidget(self.labelScan )

        # --- Left: Table Widget ---
        self._setup_table_widget()

        # --- Right: Detail Panel ---
        self.right_panel = self._create_detail_panel()
        self.splitter.addWidget(self.right_panel)


        # Style général
        self.setStyleSheet("""
            QWidget { background-color: #f0f0f5; font-family: Segoe UI; }
            QLineEdit { border: 1px solid #B0B0B0; border-radius: 6px; padding: 6px 10px; font-size: 14px; }
            QPushButton { background-color: #2301C0; color: white; border-radius: 6px; padding: 10px 20px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #120A37; }
            QTableWidget { border: 1px solid #D0D0D0; border-radius: 6px; background-color: #ffffff; }
            QTableWidget::item:selected { background-color: #E6F3FF; color:black,ont-size: 12px; }
        """)
        self.load_json_to_table()

    # -------------------------
    # Top Bar
    # -------------------------
    def _setup_top_bar(self, parent_layout):
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select folder here...")
        self.path_edit.setReadOnly(True)
        self.path_edit.setFixedHeight(40)
        top_bar.addWidget(self.path_edit, stretch=1)

        add_button = QPushButton()
        add_button.setIcon(QIcon("img/plus.png"))  # ton icône personnalisée

        add_button.setToolTip("Show / Hide Details")
        add_button.setIcon(QIcon.fromTheme("view-right"))

        menu = QMenu()
        menu.addAction(QAction("Add Folder", self, triggered=self.add_folder))
        menu.addAction(QAction("Create File in Folder", self, triggered=self.create_file_in_folder))
        add_button.setMenu(menu)
        top_bar.addWidget(add_button)

        self.scan_button = QPushButton("Scan")

        self.scan_button.clicked.connect(self.lance_scan)
        top_bar.addWidget(self.scan_button)
        self.mode_button = QPushButton("Live Mode :")
        self.mode_button.setStyleSheet(
            """ QPushButton { background-color: none ;color: gris ; border-radius: 6px; font-size: 14px; font-weight: bold; } """)
        self.mode_button.clicked.connect(self.change_mode)
        self.mode_button.setObjectName("modeButton")
        top_bar.addWidget(self.mode_button)
        self.label = QLabel('<span style="color: green; font-weight: bold;"> Running </span>')
        top_bar.addWidget(self.label)
        toggle_button = QPushButton()
        toggle_button.setIcon(QIcon("img/details.png"))  # ton icône personnalisée

        toggle_button.setToolTip("Show / Hide Details")
        toggle_button.setIcon(QIcon.fromTheme("view-right"))
        toggle_button.setFixedSize(40, 40)
        toggle_button.clicked.connect(self._toggle_right_panel)
        top_bar.addWidget(toggle_button)

        parent_layout.addLayout(top_bar)

    # -------------------------
    # Table Widget
    # -------------------------
    def _toggle_right_panel(self):
        """Montre ou cache le panneau de détails."""
        self.right_panel.setVisible(not self.right_panel.isVisible())

    def _setup_table_widget(self):
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Path", "User"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.splitter.addWidget(self.table)

    def load_json_to_table(self):

        json_file = "baseline.json"

        if not os.path.exists(json_file):
            QMessageBox.warning(self, "Error", f"JSON file not found:\n{json_file}")
            return

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(data)
            self.table.setRowCount(0)
            for row_index, (file_path, info) in enumerate(sorted(data.items())):
                self.table.insertRow(row_index)
                file_name = os.path.basename(file_path)
                folder_name = os.path.dirname(file_path)
                user = info.get("user", "-")
                self.table.setItem(row_index, 0, QTableWidgetItem(file_name))
                self.table.setItem(row_index, 1, QTableWidgetItem(folder_name))
                self.table.setItem(row_index, 2, QTableWidgetItem(user))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON:\n{e}")

    # -------------------------
    # Detail Panel
    # -------------------------
    def load_log_details(self):
        """Lit le fichier log.txt dans le dossier sélectionné et affiche son contenu."""
        folder_path = self.path_edit.text().strip()

        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.warning(self, "Error", "Please select a valid folder.")
            return

        log_file = os.path.join(folder_path,"data", "log.txt")

        if not os.path.exists(log_file):
            QMessageBox.warning(self, "Error", f"log.txt not found in:\n{folder_path}")
            return

        # 🔄 Nettoyage du contenu précédent
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                label = QLabel("Log file is empty.")
                label.setStyleSheet("color: gray; font-style: italic;")
                self.scroll_layout.addWidget(label)
                return

            for line in lines:
                line = line.strip()
                if line:
                    item = QLabel(f"• {line}")
                    item.setWordWrap(True)
                    item.setStyleSheet("""
                        QLabel {
                            background-color: #E8EAF6;
                            border: 1px solid #C5CAE9;
                            border-radius: 6px;
                            padding: 6px 10px;
                            color: #1A237E;
                        }
                        QLabel:hover {
                            background-color: #C5CAE9;
                        }
                    """)
                    self.scroll_layout.addWidget(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unable to read log.txt:\n{e}")

    def _create_detail_panel(self):
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(10)

        title = QLabel("DETAIL")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: green;")
        vbox.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(scroll_content)

        vbox.addWidget(scroll)
        return widget


    def create_file_in_folder(self):
        folder = self.path_edit.text().strip()
        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "Error", "Please select a valid folder.")
            return

        file_name, ok = QInputDialog.getText(self, "Create File", "File name (e.g., log.txt):")
        if ok and file_name:
            file_path = os.path.join(folder, file_name)
            try:
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write("")
                    QMessageBox.information(self, "Success", f"File created:\n{file_path}")
                else:
                    QMessageBox.warning(self, "Warning", "The file already exists.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Unable to create the file:\n{e}")

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select a folder")
        if folder:
            self.path_edit.setText(folder)
            build_baseline_for_folder(folder)
            self.load_json_to_table()

        else :
            QMessageBox.warning(self, "Error", "Please select a valid folder.")
            return


    def lance_scan(self):

        try:
            if self.scan_button.text().strip()=="scan":
                if get_mode() == "manuel":
                    self.load_log_details
                    self.scan_button.setText("Arreter")
                    # check intergrity
                    self.labelScan.setText("Strat Scan ....... ")
                    # label Strat Scan .......
                    # changer la valeur de button scan
                else:
                    QMessageBox.critical(self, "Erreur", f"Scann deja en cours ... pour relence click sur live mode  :\n")

            else :
                self.scan_button.setText("scan")
                self.labelScan.setText("Arreter  Scan ....... ")


        except Exception as error:
            QMessageBox.critical(self, "Erreur", f"Impossible :\n{error}")

    def change_mode(self):
        if get_mode() == "manuel":
            update_mode("auto")
            self.label.setText('<span style="color: green; font-weight: bold;"> Running </span>')
        else :
            update_mode("manuel")
            self.label.setText('<span style="color: red; font-weight: bold;"> Disebled </span>')



# =========================
# Test standalone
# =========================
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ScanPage()
    window.setWindowTitle("Scan Page Test")
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec())
