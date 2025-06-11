from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QTextEdit,
    QLabel,
    QLineEdit,
    QTabWidget,
    QComboBox,
    QMessageBox,
    QApplication,
    QDialog,
    QFileDialog,
    QScrollArea,
    QProgressBar,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
import json
import os
import ctypes
import sys
from .filter import ContentFilter
from .utils import is_valid_url


class AppreciationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome!")
        self.setFixedSize(500, 300)

        layout = QVBoxLayout()

        # Title
        title = QLabel("NSFW Blocker")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Create scroll area for message
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #888;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Message container widget
        message_container = QWidget()
        message_layout = QVBoxLayout(message_container)

        # Message
        message = QLabel(
            "Special thanks to GitHub user Mustaffa96 for creating this valuable "
            "tool to help make the internet a safer place. This NSFW content blocker "
            "represents a commitment to online safety and content filtering.\n\n"
            "Key Features:\n"
            "• URL and Domain Blocking\n"
            "- Block specific websites and domains\n"
            "- Import multiple URLs from text files\n"
            "- Automatic URL validation\n\n"
            "• Keyword-based Content Filtering\n"
            "- Block content based on keywords\n"
            "- Separate explicit and moderate categories\n"
            "- Customizable filtering rules\n\n"
            "• System Tray Integration\n"
            "- Run in background\n"
            "- Quick access to controls\n"
            "- Minimize to system tray\n\n"
            "• User-friendly Interface\n"
            "- Easy to use controls\n"
            "- Clear status indicators\n"
            "- Intuitive layout\n\n"
            "Visit: github.com/Mustaffa96/NSFW_BlockerQT\n\n"
            "Usage Tips:\n"
            "1. Run as administrator to modify system files\n"
            "2. Use the URL import feature for bulk blocking\n"
            "3. Customize keyword categories as needed\n"
            "4. Keep the application running in the background\n"
            "5. Check the blocking status indicator"
        )
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        message_font = QFont()
        message_font.setPointSize(10)
        message.setFont(message_font)

        message_layout.addWidget(message)
        message_layout.addStretch()

        scroll_area.setWidget(message_container)
        layout.addWidget(scroll_area)

        # OK button
        ok_button = QPushButton("Start Application")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class BlockerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Show appreciation dialog
        dialog = AppreciationDialog(self)
        dialog.exec_()

        self.setWindowTitle("NSFW Blocker")
        # Set window icon - handle both development and PyInstaller environments
        try:
            base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
            icon_path = os.path.join(base_path, "icon.png")
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Could not load icon: {e}")

        self.setGeometry(100, 100, 800, 600)

        # Check for admin privileges
        if not is_admin():
            QMessageBox.warning(
                self,
                "Admin Rights Required",
                "This application requires administrator privileges to modify the hosts file.\n"
                "Please run the application as administrator.",
            )

        # Initialize content filter
        self.content_filter = ContentFilter()

        # Initialize blocking state
        self.blocking_enabled = False

        # Setup UI
        self.setup_ui()
        self.setup_tray()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        tabs = QTabWidget()

        # URL blocking tab
        url_tab = QWidget()
        url_layout = QVBoxLayout(url_tab)

        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL to block...")
        add_url_button = QPushButton("Add URL")
        add_url_button.clicked.connect(self.add_url)
        check_url_button = QPushButton("Check URL")
        check_url_button.clicked.connect(self.check_url)
        url_input_layout.addWidget(self.url_input)
        url_input_layout.addWidget(add_url_button)
        url_input_layout.addWidget(check_url_button)
        url_layout.addLayout(url_input_layout)

        self.url_list = QTextEdit()
        self.url_list.setReadOnly(True)
        url_layout.addWidget(self.url_list)

        # Keyword blocking tab
        keyword_tab = QWidget()
        keyword_layout = QVBoxLayout(keyword_tab)

        keyword_label = QLabel("Enter keyword to block:")
        self.keyword_input = QLineEdit()

        category_layout = QHBoxLayout()
        category_label = QLabel("Category:")
        self.keyword_category = QComboBox()
        self.keyword_category.addItems(["explicit", "moderate"])
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.keyword_category)

        add_keyword_button = QPushButton("Add Keyword")
        add_keyword_button.clicked.connect(self.add_keyword)

        self.keyword_list = QTextEdit()
        self.keyword_list.setReadOnly(True)
        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.keyword_input)
        keyword_layout.addLayout(category_layout)
        keyword_layout.addWidget(add_keyword_button)
        keyword_layout.addWidget(self.keyword_list)

        # Add tabs
        tabs.addTab(url_tab, "URL Blocking")
        tabs.addTab(keyword_tab, "Keyword Blocking")

        # Add tabs to main layout
        layout.addWidget(tabs)

        # Add feedback section
        feedback_group = QWidget()
        feedback_layout = QVBoxLayout(feedback_group)

        # Detection results label with custom styling
        self.detection_label = QLabel("Detection Results")
        self.detection_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        """)
        feedback_layout.addWidget(self.detection_label)

        # Score bars
        scores_widget = QWidget()
        scores_layout = QVBoxLayout(scores_widget)

        # Safe score
        safe_layout = QHBoxLayout()
        safe_label = QLabel("Safe:")
        self.safe_score = QProgressBar()
        self.safe_score.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #28a745;
            }
        """)
        safe_layout.addWidget(safe_label)
        safe_layout.addWidget(self.safe_score)
        scores_layout.addLayout(safe_layout)

        # Moderate score
        moderate_layout = QHBoxLayout()
        moderate_label = QLabel("Moderate:")
        self.moderate_score = QProgressBar()
        self.moderate_score.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #ffc107;
            }
        """)
        moderate_layout.addWidget(moderate_label)
        moderate_layout.addWidget(self.moderate_score)
        scores_layout.addLayout(moderate_layout)

        # Explicit score
        explicit_layout = QHBoxLayout()
        explicit_label = QLabel("Explicit:")
        self.explicit_score = QProgressBar()
        self.explicit_score.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #dc3545;
            }
        """)
        explicit_layout.addWidget(explicit_label)
        explicit_layout.addWidget(self.explicit_score)
        scores_layout.addLayout(explicit_layout)

        feedback_layout.addWidget(scores_widget)

        # Matches text area
        self.matches_text = QTextEdit()
        self.matches_text.setReadOnly(True)
        self.matches_text.setMaximumHeight(100)
        self.matches_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        feedback_layout.addWidget(self.matches_text)

        # Add feedback section to main layout
        layout.addWidget(feedback_group)

        # Status and control
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Blocking is currently disabled")
        self.toggle_button = QPushButton("Enable Blocking")
        self.toggle_button.clicked.connect(self.toggle_blocking)

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.toggle_button)
        layout.addLayout(status_layout)

        # Bottom buttons layout
        button_layout = QHBoxLayout()

        # Close button with red background
        close_button = QPushButton("Close Application")
        close_button.clicked.connect(self.quit_application)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Load current lists
        self.update_url_list()
        self.update_keyword_list()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            self.style().standardIcon(self.style().SP_DialogNoButton)
        )

        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)

        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def flush_dns(self):
        """Manually flush the DNS cache"""
        if not is_admin():
            QMessageBox.warning(
                self,
                "Admin Rights Required",
                "Administrator privileges are required to flush DNS cache.",
            )
            return

        try:
            if self.content_filter.flush_dns_cache():
                QMessageBox.information(
                    self, "Success", "DNS cache flushed successfully"
                )
            else:
                QMessageBox.warning(self, "Error", "Failed to flush DNS cache")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def close_application(self):
        """Properly close the application"""
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Are you sure you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Ensure blocking is disabled when quitting
            if self.blocking_enabled:
                self.content_filter.disable_blocking()
            QApplication.quit()

    def add_url(self):
        if not is_admin():
            QMessageBox.warning(
                self,
                "Admin Rights Required",
                "Administrator privileges are required to modify the hosts file.",
            )
            return

        url = self.url_input.text().strip()
        if url:
            if is_valid_url(url):
                if self.content_filter.block_url(url):
                    self.update_url_list()
                    self.url_input.clear()
                    # Check the URL after adding
                    self.check_url()
                else:
                    QMessageBox.warning(self, "Error", "Failed to block URL")
            else:
                QMessageBox.warning(self, "Error", "Invalid URL format")

    def check_url(self):
        """Check the current URL for NSFW content"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL to check")
            return

        if not is_valid_url(url):
            QMessageBox.warning(self, "Error", "Invalid URL format")
            return

        try:
            is_blocked = self.check_webpage(url)
            if is_blocked:
                reply = QMessageBox.question(
                    self,
                    "Block URL?",
                    "NSFW content detected. Would you like to block this URL?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )
                if reply == QMessageBox.Yes:
                    self.content_filter.block_url(url)
                    self.update_url_list()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to check URL: {str(e)}")

    def add_keyword(self):
        keyword = self.keyword_input.text().strip()
        category = self.keyword_category.currentText()
        if keyword:
            if self.content_filter.add_keyword(keyword, category):
                self.update_keyword_list()
                self.keyword_input.clear()
            else:
                QMessageBox.warning(self, "Error", "Keyword already exists")

    def update_url_list(self):
        urls = self.content_filter.get_blocked_urls()
        self.url_list.setText("\n".join(urls))

    def update_keyword_list(self):
        keywords = self.content_filter.get_keywords()
        text = []
        for category, words in keywords.items():
            if words:
                text.append(f"{category.upper()}:")
                text.extend(f"  - {word}" for word in words)
        self.keyword_list.setText("\n".join(text))

    def apply_settings(self):
        pass  # Remove settings functionality since it was only for NSFW detection

    def toggle_blocking(self):
        if not is_admin():
            QMessageBox.warning(
                self,
                "Admin Rights Required",
                "Administrator privileges are required to modify the hosts file.",
            )
            return

        try:
            if not self.blocking_enabled:
                if self.content_filter.enable_blocking():
                    self.blocking_enabled = True
                    self.toggle_button.setText("Disable Blocking")
                    self.status_label.setText("Blocking is currently enabled")
                    QMessageBox.information(
                        self, "Success", "Blocking has been enabled"
                    )
                else:
                    QMessageBox.warning(self, "Error", "Failed to enable blocking")
            else:
                if self.content_filter.disable_blocking():
                    self.blocking_enabled = False
                    self.toggle_button.setText("Enable Blocking")
                    self.status_label.setText("Blocking is currently disabled")
                    QMessageBox.information(
                        self, "Success", "Blocking has been disabled"
                    )
                else:
                    QMessageBox.warning(self, "Error", "Failed to disable blocking")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def quit_application(self):
        """Properly close the application"""
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Are you sure you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Ensure blocking is disabled when quitting
            if self.blocking_enabled:
                self.content_filter.disable_blocking()
            QApplication.quit()

    def changeEvent(self, event):
        """Handle window state changes"""
        if event.type() == event.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                event.accept()
                self.hide()  # Hide from taskbar
                self.tray_icon.show()  # Ensure tray icon is visible

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def check_webpage(self, url):
        """Check webpage and update feedback display"""
        try:
            is_blocked, scores = self.content_filter.check_webpage(url)
            self.update_feedback_display(scores)
            return is_blocked
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to check webpage: {str(e)}")
            return False

    def update_feedback_display(self, scores):
        """Update the feedback display with detection results"""
        # Update progress bars
        self.safe_score.setValue(int(scores["safe"] * 100))
        self.moderate_score.setValue(int(scores["moderate"] * 100))
        self.explicit_score.setValue(int(scores["explicit"] * 100))

        # Update matches text
        matches_text = []
        if scores["matches"]["explicit"]:
            matches_text.append("Explicit Matches:")
            for keyword, count in scores["matches"]["explicit"]:
                matches_text.append(f"  • {keyword} ({count} occurrences)")

        if scores["matches"]["moderate"]:
            if matches_text:
                matches_text.append("")
            matches_text.append("Moderate Matches:")
            for keyword, count in scores["matches"]["moderate"]:
                matches_text.append(f"  • {keyword} ({count} occurrences)")

        if not matches_text:
            matches_text = ["No inappropriate content detected"]

        self.matches_text.setText("\n".join(matches_text))

        # Update detection label based on scores
        if scores["explicit"] >= 0.3:
            status = "Explicit Content Detected"
            color = "#dc3545"  # Red
        elif scores["moderate"] >= 0.45:
            status = "Moderate Content Detected"
            color = "#ffc107"  # Yellow
        else:
            status = "Safe Content"
            color = "#28a745"  # Green

        self.detection_label.setText(status)
        self.detection_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                color: white;
                background-color: {color};
                border-radius: 4px;
            }}
        """)
