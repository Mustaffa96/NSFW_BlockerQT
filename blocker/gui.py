from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QSystemTrayIcon, QMenu, QAction, QTextEdit, QLabel,
                             QLineEdit, QTabWidget, QComboBox, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import json
import os
import ctypes
from .filter import ContentFilter
from .utils import is_valid_url

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class BlockerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NSFW Blocker")
        self.setGeometry(100, 100, 800, 600)
        
        # Check for admin privileges
        if not is_admin():
            QMessageBox.warning(self, "Admin Rights Required", 
                              "This application requires administrator privileges to modify the hosts file.\n"
                              "Please run the application as administrator.")
        
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
        
        url_label = QLabel("Enter URL to block:")
        self.url_input = QLineEdit()
        
        add_url_button = QPushButton("Add URL")
        add_url_button.clicked.connect(self.add_url)
        
        self.url_list = QTextEdit()
        self.url_list.setReadOnly(True)
        self.update_url_list()
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(add_url_button)
        url_layout.addWidget(QLabel("Blocked URLs:"))
        url_layout.addWidget(self.url_list)
        
        # Keyword blocking tab
        keyword_tab = QWidget()
        keyword_layout = QVBoxLayout(keyword_tab)
        
        keyword_header = QHBoxLayout()
        keyword_label = QLabel("Enter keyword to block:")
        self.keyword_category = QComboBox()
        self.keyword_category.addItems(["explicit", "moderate"])
        keyword_header.addWidget(keyword_label)
        keyword_header.addWidget(self.keyword_category)
        
        self.keyword_input = QLineEdit()
        add_keyword_button = QPushButton("Add Keyword")
        add_keyword_button.clicked.connect(self.add_keyword)
        
        self.keyword_list = QTextEdit()
        self.keyword_list.setReadOnly(True)
        self.update_keyword_list()
        
        keyword_layout.addLayout(keyword_header)
        keyword_layout.addWidget(self.keyword_input)
        keyword_layout.addWidget(add_keyword_button)
        keyword_layout.addWidget(QLabel("Blocked Keywords:"))
        keyword_layout.addWidget(self.keyword_list)
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # NSFW detection status
        nsfw_status = QLabel()
        if self.content_filter.nsfw_detector.is_available():
            nsfw_status.setText("NSFW Detection: Available")
            
            # NSFW detection threshold
            threshold_layout = QHBoxLayout()
            threshold_label = QLabel("NSFW Detection Threshold:")
            self.threshold_input = QLineEdit()
            self.threshold_input.setText("0.85")
            self.threshold_input.setMaximumWidth(100)
            threshold_layout.addWidget(threshold_label)
            threshold_layout.addWidget(self.threshold_input)
            threshold_layout.addStretch()
            
            apply_settings = QPushButton("Apply Settings")
            apply_settings.clicked.connect(self.apply_settings)
            
            settings_layout.addLayout(threshold_layout)
            settings_layout.addWidget(apply_settings)
        else:
            nsfw_status.setText("NSFW Detection: Not Available\nInstall TensorFlow to enable image detection")
        
        settings_layout.addWidget(nsfw_status)
        settings_layout.addStretch()
        
        # Add tabs
        tabs.addTab(url_tab, "URL Blocking")
        tabs.addTab(keyword_tab, "Keyword Blocking")
        tabs.addTab(settings_tab, "Settings")
        
        # Add tabs to main layout
        layout.addWidget(tabs)
        
        # Bottom buttons layout
        bottom_layout = QHBoxLayout()
        
        # Enable/Disable button
        self.toggle_button = QPushButton("Enable Blocking")
        self.toggle_button.clicked.connect(self.toggle_blocking)
        bottom_layout.addWidget(self.toggle_button)
        
        # Flush DNS button
        flush_dns_button = QPushButton("Flush DNS Cache")
        flush_dns_button.clicked.connect(self.flush_dns)
        bottom_layout.addWidget(flush_dns_button)
        
        # Close button
        close_button = QPushButton("Close Application")
        close_button.clicked.connect(self.close_application)
        close_button.setStyleSheet("background-color: #d9534f; color: white;")
        bottom_layout.addWidget(close_button)
        
        layout.addLayout(bottom_layout)
        
        # Status label
        self.status_label = QLabel("Blocking is currently disabled")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def flush_dns(self):
        """Manually flush the DNS cache"""
        if not is_admin():
            QMessageBox.warning(self, "Admin Rights Required", 
                              "Administrator privileges are required to flush DNS cache.")
            return
            
        try:
            if self.content_filter.flush_dns_cache():
                QMessageBox.information(self, "Success", "DNS cache flushed successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to flush DNS cache")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def close_application(self):
        """Properly close the application"""
        reply = QMessageBox.question(self, 'Confirm Exit',
                                   'Are you sure you want to exit?\nBlocking will be disabled.',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Ensure blocking is disabled
            if self.blocking_enabled:
                if not self.content_filter.disable_blocking():
                    QMessageBox.warning(self, "Warning", 
                                      "Failed to disable blocking.\nYou may need to manually restore the hosts file.")
            
            # Quit application
            self.quit_application()
    
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_DialogNoButton))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.close_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def add_url(self):
        if not is_admin():
            QMessageBox.warning(self, "Admin Rights Required", 
                              "Administrator privileges are required to modify the hosts file.")
            return
            
        url = self.url_input.text().strip()
        if url and is_valid_url(url):
            if self.content_filter.block_url(url):
                self.update_url_list()
                self.url_input.clear()
                QMessageBox.information(self, "Success", f"URL {url} has been added to the block list.")
            else:
                QMessageBox.warning(self, "Error", "Failed to block URL")
        else:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid URL")
    
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
        if not self.content_filter.nsfw_detector.is_available():
            return
            
        try:
            threshold = float(self.threshold_input.text())
            if 0 <= threshold <= 1:
                self.content_filter.nsfw_detector.set_threshold(threshold)
                QMessageBox.information(self, "Success", "Settings applied successfully")
            else:
                raise ValueError("Threshold must be between 0 and 1")
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
    
    def toggle_blocking(self):
        if not is_admin():
            QMessageBox.warning(self, "Admin Rights Required", 
                              "Administrator privileges are required to modify the hosts file.")
            return
            
        try:
            if not self.blocking_enabled:
                if self.content_filter.enable_blocking():
                    self.blocking_enabled = True
                    self.toggle_button.setText("Disable Blocking")
                    self.status_label.setText("Blocking is currently enabled")
                    QMessageBox.information(self, "Success", "Blocking has been enabled")
                else:
                    QMessageBox.warning(self, "Error", "Failed to enable blocking")
            else:
                if self.content_filter.disable_blocking():
                    self.blocking_enabled = False
                    self.toggle_button.setText("Enable Blocking")
                    self.status_label.setText("Blocking is currently disabled")
                    QMessageBox.information(self, "Success", "Blocking has been disabled")
                else:
                    QMessageBox.warning(self, "Error", "Failed to disable blocking")
            
            # Update tray icon
            icon = self.style().SP_DialogYesButton if self.blocking_enabled else self.style().SP_DialogNoButton
            self.tray_icon.setIcon(self.style().standardIcon(icon))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def quit_application(self):
        # Ensure blocking is disabled when quitting
        if self.blocking_enabled:
            self.content_filter.disable_blocking()
        QApplication.quit()
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
