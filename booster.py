#Custom text editor. Dark theme, emacs inspired.
#WORKNAME: darkscrawl
#This file handles the setup of the application.
#2018 Cody Azevedo

import sys

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from textbox import TextBox_Window

#Create instance of text box
main_text_window = TextBox_Window()

#Create main window, handles key inputs and initializes application
class MainWindow(QMainWindow, TextBox_Window):
	
	exit_displayed = False

	def __init__(self, parent = None):
		super(MainWindow, self).__init__(parent)
		self.create_widget(self)

	#Handle all keypress events (saves, shortcuts, keybindings etc)
	def keyPressEvent(self, event):
   		k = event.key()
		m = int(event.modifiers())
		
		if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+S'):
			self.file_save()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence("Ctrl+O"):
			if not TextBox_Window.dir_browser_open:
				self.open_dir_browser()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+F'):
			if TextBox_Window.search_displayed:
				self.search_in_file()
			else:
				self.setup_search_box()
								
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+G'):
			if TextBox_Window.search_displayed:
				self.remove_search_box()
			elif TextBox_Window.new_file_displayed:
				self.remove_new_file_box()
			elif TextBox_Window.dir_browser_open:
				self.close_dir_browser()
				TextBox_Window.dir_browser_open = False
			else:
				self.reset_browser_bar()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+N'):
			self.setup_new_file()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+P'):
			self.open_preference_menu()
			
		elif k == QtCore.Qt.Key_Escape:
			if TextBox_Window.dir_browser_open:
				self.close_dir_browser()
				TextBox_Window.dir_browser_open = False
		elif k == QtCore.Qt.Key_F11:
			if self.windowState() != Qt.WindowMaximized:
				self.setWindowState(Qt.WindowMaximized)
			else:
				self.setWindowState(Qt.WindowFullScreen)
			
	def closeEvent(self, event):
		if TextBox_Window.file_1_is_modified:
			event.ignore()
			
			if not MainWindow.exit_displayed:
				MainWindow.exit = ExitLineEdit("")
				self.exit.setFixedHeight(self.font_metrics.height() + 6)
				self.exit.setFont(TextBox_Window.font)
				self.exit.returnPressed.connect(self.exit_app)

			self.file_label.setParent(None)
			self.file_modified_label.setParent(None)
			self.filemode_label.setParent(None)
			self.editmode_label.setParent(None)
			self.line_label.setParent(None)

			self.browser_layout.addWidget(self.exit)
			self.browser_layout.addWidget(self.file_modified_label)
			self.browser_layout.addWidget(self.file_label)
			self.browser_layout.addWidget(self.filemode_label)
			self.browser_layout.addWidget(self.editmode_label)
			self.browser_layout.addWidget(self.line_label)
			
			self.exit.setFocus()
			MainWindow.exit_displayed = True

			self.main_text_label.setText("Buffer 1 has unsaved changes. Exit anyway? (Yes/No):")

		elif TextBox_Window.file_2_is_modified:
			event.ignore()
			
			if not MainWindow.exit_displayed:
				MainWindow.exit = ExitLineEdit("")
				self.exit.setFixedHeight(self.font_metrics.height() + 6)
				self.exit.setFont(TextBox_Window.font)
				self.exit.returnPressed.connect(self.exit_app)

			self.file_label2.setParent(None)
			self.file_modified_label2.setParent(None)
			self.filemode_label2.setParent(None)
			self.editmode_label2.setParent(None)
			self.line_label2.setParent(None)

			self.browser_layout2.addWidget(self.exit)
			self.browser_layout2.addWidget(self.file_modified_label2)
			self.browser_layout2.addWidget(self.file_label2)
			self.browser_layout2.addWidget(self.filemode_label2)
			self.browser_layout2.addWidget(self.editmode_label2)
			self.browser_layout2.addWidget(self.line_label2)
			
			self.outer_widget_2.show()
			self.textbox2.setFocus()
			
			self.exit.setFocus()
			MainWindow.exit_displayed = True

			self.main_text_label2.setText("Buffer 2 has unsaved changes. Exit anyway? (Yes/No):")

	def exit_app(self):
		if self.exit.text() == "yes":
			sys.exit()
		else:
			MainWindow.exit.setParent(None)
			MainWindow.exit.setText("")
			self.main_text_label.setText("")

			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setFocus()
			else:
				self.textbox.setFocus()
								
class ExitLineEdit(QtGui.QLineEdit, TextBox_Window):

	def __init__(self, parent = None):
		super(ExitLineEdit, self).__init__(parent)
		self.exit_line_edit = QLineEdit()
		self.setStyleSheet("""
							ExitLineEdit { background-color: #17181C; color: white; border: 0px solid black; font-size: 14px; font-weight: bold; }
						""")
		
   	def focusOutEvent(self, event):
		if MainWindow.exit_displayed == True:
			MainWindow.exit_displayed == False
			self.remove_exit()
		elif MainWindow.exit_displayed == True:
			MainWindow.exit_displayed == False
			self.remove_exit()

	def remove_exit(self):
		MainWindow.exit.setParent(None)
		self.main_text_label.setText("")
		self.main_text_label2.setText("")
		if TextBox_Window.active_window == "Textbox2":
			self.textbox2.setFocus()
		else:
			self.textbox.setFocus()
									
if __name__ == '__main__':
	#Every PyQt4 app must create an application object, sys.argv is arguments from cmd line
	app = QtGui.QApplication(sys.argv)
	app.setWindowIcon(QIcon('icon.png'))

	w = MainWindow()
	w.resize(TextBox_Window.font_metrics.width(" ") * 110, TextBox_Window.font_metrics.lineSpacing() * 40)
	w.show()

	sys.exit(app.exec_())
