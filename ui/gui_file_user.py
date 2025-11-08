from PyQt6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QMessageBox
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize
import os

class FileSelectionDialog(QDialog):
    def __init__(self, folder_path="", is_dark_theme=False, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 500)
        self.selected_file = None  # ← le fichier choisi

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("📁 Select a File")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.file_list)

        if folder_path:
            for f in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, f)):
                    self.file_list.addItem(f)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setIcon(QIcon("img/ok.png"))
        self.ok_btn.setIconSize(QSize(16, 16))
        self.ok_btn.clicked.connect(self.accept_selection)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setIcon(QIcon("img/close.png"))
        self.cancel_btn.setIconSize(QSize(16, 16))
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.apply_theme(is_dark_theme)

    def accept_selection(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a file.")
            return
        self.selected_file = selected_items[0].text()
        self.accept()  # ferme le QDialog avec succès

    def apply_theme(self, dark):
        if dark:
            self.setStyleSheet("""
                            QWidget {
                                background-color: #1A202C;
                                border-radius: 15px;
                                color: #E2E8F0;
                            }
                            QListWidget {
                                background-color: #2D3748;
                                border: 1px solid #4A5568;
                                border-radius: 8px;
                                padding: 6px;
                                color: #E2E8F0;
                            }
                            QPushButton {
                                background-color: #2B6CB0;
                                color: white;
                                border-radius: 8px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #3182CE;
                            }
                            QLabel {
                                color: #63B3ED;
                            }
                        """)
        else:
            self.setStyleSheet("""
                            QWidget {
                                background-color: #F7F7FD;
                                border-radius: 15px;
                                color: #3342CC;
                            }
                            QListWidget {
                                background-color: white;
                                border: 2px solid #3342CC;
                                border-radius: 8px;
                                padding: 6px;
                                color: #1A202C;
                            }
                            QPushButton {
                                background-color: #3342CC;
                                color: white;
                                border-radius: 8px;
                                font-weight: bold;
                                height: 35px;
                            }
                            QPushButton:hover {
                                background-color: #4752E8;
                            }
                            QLabel {
                                color: #3342CC;
                            }
                        """)




