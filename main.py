import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from modules.user_data import Settings, ensure_user_data_exists


ensure_user_data_exists()
DEFAULT_PAGE = Settings.get("default_page","https://duckduckgo.com/")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.title = 'PyQt5 Webbrowser - Settings'
        self.settings = QSettings('YourCompany', 'YourApp')

        # Initialize UI components
        self.initUI()

    def initUI(self):
        # Create layout and widgets
        layout = QVBoxLayout()
        self.textbox = QLineEdit(self)
        
        #create textbox to change default page
        self.textbox.setText(DEFAULT_PAGE)
        
        # Save button to apply changes
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_changes)
        
        # Add widgets to layout
        layout.addWidget(self.textbox)
        layout.addWidget(save_button)
        
        # Set dialog layout
        self.setLayout(layout)

    def save_changes(self):
        # Save the new default page setting
        Settings.set("default_page",self.textbox.text())

class MainWindow(QMainWindow):
    """
    Main application window for the PyQt5 web browser.

    This class sets up the main window, navigation toolbar, and manages tabs and URLs.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the MainWindow with a set of default properties and layouts.

        Parameters
        ----------
        *args : tuple
            Variable length argument list passed to the parent constructor.
        **kwargs : dict
            Arbitrary keyword arguments passed to the parent constructor.
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.setup_navigation_toolbar()
        self.add_new_tab(QUrl(DEFAULT_PAGE), 'Homepage')
        self.setWindowTitle("PyQT5 Webbrowser")
        self.show()

    def setup_navigation_toolbar(self):
        """
        Set up the navigation toolbar with common web browsing actions.

        This includes buttons for going back, forward, reloading, going home, and stopping the page load.
        """
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)
        actions = [
            ("Back", "Back to previous page", self.back_action),
            ("Forward", "Forward to next page", self.forward_action),
            ("Reload", "Reload page", self.reload_action),
            ("Home", "Go home", self.navigate_home),
            ("Stop", "Stop loading current page", self.stop_action)
        ]
        for name, status_tip, function in actions:
            button = QAction(name, self)
            button.setStatusTip(status_tip)
            button.triggered.connect(function)
            navtb.addAction(button)
        navtb.addSeparator()
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        navtb.addAction(settings_action)
    
    def open_settings_dialog(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_() == QDialog.Accepted:
            pass

    def add_new_tab(self, qurl=None, label="Blank"):
        """
        Add a new tab to the tab widget with the specified URL and label.

        Parameters
        ----------
        qurl : QUrl, optional
            The URL to load in the new tab, by default None which loads the homepage.
        label : str, optional
            The label for the new tab, by default 'Blank'.
        """
        
        if qurl is None:
            qurl = QUrl(DEFAULT_PAGE)
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("% s - PyQT5 Webbrowser" % title)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl(DEFAULT_PAGE))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def back_action(self):
        current_widget = self.tabs.currentWidget()
        if current_widget:
            current_widget.back()

    def forward_action(self):
        current_widget = self.tabs.currentWidget()
        if current_widget:
            current_widget.forward()

    def reload_action(self):
        current_widget = self.tabs.currentWidget()
        if current_widget:
            current_widget.reload()

    def stop_action(self):
        current_widget = self.tabs.currentWidget()
        if current_widget:
            current_widget.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()