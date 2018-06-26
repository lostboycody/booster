#Custom text editor. Dark theme, emacs inspired.
#WORKNAME: darkscrawl
#2018 Cody Azevedo

import sys
import os
import threading
import re
import string
import ntpath
import platform
import syntax
from textbox import TextBox_Window
from threading import Thread
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4 import QtGui
from PyQt4.QtGui import *
from functools import partial

#Create instance of text box
main_text_window = TextBox_Window()

#Create main window, handles key inputs and initializes application
class MainWindow(QMainWindow, TextBox_Window):

	def __init__(self, parent = None):
		super(MainWindow, self).__init__(parent)
		self.create_widget(self)

	#Handle all keypress events (saves, shortcuts, keybindings etc)
	def keyPressEvent(self, event):
   		k = event.key()
		m = int(event.modifiers())

		#TODO(Cody): Handle Ctrl+X+S, Ctrl+X+F etc.
		#self.textbox.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_X, Qt.CTRL + Qt.Key_F), self), QtCore.SIGNAL('activated()'), self.file_open())
		
		if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+S'):
			self.file_save()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence("Ctrl+O"):
			if not TextBox_Window.dir_browser_open:
				self.open_dir_browser()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+F'):
			self.setup_search_box()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+G'):
			if TextBox_Window.search_displayed == 1:
				self.remove_search_box()
			elif TextBox_Window.new_file_displayed == 1:
				self.remove_new_file_box()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+N'):
			self.setup_new_file()
		elif TextBox_Window.dir_browser_open == True and k == QtCore.Qt.Key_Backspace:
			self.open_previous_dir()
		elif  k == QtCore.Qt.Key_Escape:
			self.close_dir_browser()				
if __name__ == '__main__':
	#Every PyQt4 app must create an application object, sys.argv is arguments from cmd line
	app = QtGui.QApplication(sys.argv)
	w = MainWindow()
	w.resize(TextBox_Window.font_metrics.width(" ") * 88, TextBox_Window.font_metrics.lineSpacing() * 40)
	w.show()

	sys.exit(app.exec_())
