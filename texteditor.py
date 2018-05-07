#Custom text editor. For fun and getting used to Python again.
#WORKNAME: darkscrawl
#2018 Cody Azevedo

import sys
import os
import threading
import re
import string
from threading import Thread
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4 import QtGui
from PyQt4.QtGui import *

class TextBox_Window(QObject):

	file_opened = False
		
	def __init__(self, parent):
		super(TextBox_Window, self).__init__(parent)
	
	def setup_app(self):
		self.create_widget()
	
	def create_widget(self, MainWindow):
		#Widget is base UI objects in PyQt4
		self.widget = QtGui.QWidget()

		self.MIN_WIDTH = 800
		self.MIN_HEIGHT = 615
		self.widget.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
		self.widget.setAutoFillBackground(True)
		MainWindow.setCentralWidget(self.widget)
		MainWindow.setWindowTitle("darkscrawl 0.0.1")

		#Set widget background color to dark gray for debug purposes
		palette = self.widget.palette()
		role = self.widget.backgroundRole()
		palette.setColor(role, QColor(17, 17, 17))
		self.widget.setPalette(palette)
		
		self.create_text_box()
		
		#Bottom command label, for use in seeing what the editor is doing
		self.bottom_label = QtGui.QLabel("", self)
		self.bottom_label.setFixedHeight(15)
		self.bottom_label.setFont(self.font)
		self.bottom_label.setStyleSheet("""
							.QLabel {
							background-color: #0D0D0D;
							color: #BFBFBF;
							}
						""")

		#Line widget, for keeping line, char count
		self.line_label = QtGui.QLabel("", parent = self.bottom_label)
		self.line_label.setFixedHeight(15)
		self.line_label.setFixedWidth(75)
		self.line_label.setFont(self.font)
		self.line_label.setAlignment(QtCore.Qt.AlignRight)
		self.line_label.setStyleSheet("""
							.QLabel {
							background-color: #0D0D0D;
							color: #BFBFBF;
							}
						""")

		#Setup GridLayout, for window stretching purposes
		self.grid_layout = QtGui.QGridLayout(self.widget)
		self.grid_layout.setMargin(0)
		self.grid_layout.setSpacing(0)
		self.grid_layout.addWidget(self.textbox)

		#Setup HBoxLayout for bottom_label sections
		self.horizontal_layout = QtGui.QHBoxLayout()
		self.horizontal_layout.setMargin(0)
		self.horizontal_layout.setSpacing(0)
		self.horizontal_layout.addWidget(self.bottom_label)
		self.horizontal_layout.addWidget(self.line_label)

		self.widget.setLayout(self.grid_layout)
		self.grid_layout.addLayout(self.horizontal_layout, 600, 0)

		self.update_bottom_label("darkscrawl 0.0.1 by lostboycody")
		self.update_cursor_position()

		self.next_empty_line()
		
   	def create_text_box(self):
   		self.textbox = QPlainTextEdit(self.widget)
		self.textbox.setMinimumSize(10, 10)
		self.textbox.setLineWrapMode(0)
		self.textbox.setFocusPolicy(QtCore.Qt.StrongFocus)				
   		self.textbox.setStyleSheet("""
   				.QPlainTextEdit {
           		background-color: #121212;
           		color: #454545;
           		}
       		""")
   		self.textbox.setFrameStyle(QFrame.NoFrame)
   		self.textbox.setCursorWidth(8)
		self.textbox.ensureCursorVisible()

   		self.font = QtGui.QFont()
   		self.font.setPointSize(11)
   		self.font.setFamily("Consolas")
   		self.textbox.setFont(self.font)

		#On cursor position update, update the label
		self.textbox.cursorPositionChanged.connect(self.update_cursor_position)

		#Set default tab width to 4 spaces
		metrics = QFontMetrics(self.font)
		self.textbox.setTabStopWidth(4 * metrics.width(' '))

		self.block = self.textbox.firstVisibleBlock()

	#Updates cursor label text, better way to do this?
	def update_cursor_position(self):
		self.cursor = self.textbox.textCursor()
		self.line = self.cursor.blockNumber() + 1
	   	self.col = self.cursor.columnNumber()
		self.line_label.setText("L{}|C{}".format(self.line, self.col))
		
   	def file_save(self):
		text = self.textbox.toPlainText()
		
		if TextBox_Window.file_opened:
			self.file = open(self.open_name, 'w')
			self.file.write(text)
			self.file.close()
			self.update_bottom_label("Saved {}".format(self.open_name))
		else:
			self.save_name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
			self.file = open(self.save_name, 'w')
			self.file.write(text)
			self.file.close()
			self.update_bottom_label("Saved {}".format(self.save_name))
			
	def file_open(self):
		TextBox_Window.file_opened = True

		self.open_name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
		if os.path.isfile(self.open_name):
			self.file = open(self.open_name, 'r')
			with self.file:
				text = self.file.read()
				self.textbox.setPlainText(text)
				self.file_length = len(text)

		else:
			self.file_save()

		self.update_bottom_label("Opened {}".format(self.open_name))

		self.block = self.textbox.firstVisibleBlock()

		
	#Set the bottom label text, reset after 5 seconds
	def update_bottom_label(self, bottomtext):
		self.bottom_label.setText(bottomtext)
		t = threading.Timer(5.0, self.remove_bottom_label)
		t.start()
		
	def remove_bottom_label(self):
		self.bottom_label.setText("")

	#Ctrl + Down scrolling: moves cursor to next empty line below cursor
	def next_empty_line(self):
		#For checking first line in document
		self.first_block = self.textbox.firstVisibleBlock()
		
		while self.block.isValid():
			if re.search('[Space-~]', self.block.text()) and self.block.next().next().text() != self.first_block.text():
				self.block = self.block.next()
			else:
				if self.block.next().position() >= self.cursor.position() and self.block.next().position() != 0:
  					self.block = self.block.next()
				self.cursor = self.textbox.textCursor()
				self.cursor.setPosition(self.block.position())
				self.textbox.setTextCursor(self.cursor)
 				break

	#Ctrl + Up scrolling: moves cursor to next empty line above cursor
	def previous_empty_line(self):
		self.first_block = self.textbox.firstVisibleBlock()
		
		while self.block.isValid():
			if re.search('[Space-~]', self.block.text()) and self.block.previous().previous().text() != "":
				self.block = self.block.previous()
			else:
				if self.block.previous().position() > 0:
   					self.block = self.block.previous()
				self.cursor = self.textbox.textCursor()
				self.cursor.setPosition(self.block.position())
				self.textbox.setTextCursor(self.cursor)
				break

class MainWindow(QMainWindow, TextBox_Window):
	
	def __init__(self, parent = None):
		super(MainWindow, self).__init__(parent)
		self.create_widget(self)
	
	def keyPressEvent(self, event):
   		k = event.key()
		m = int(event.modifiers())

		#TODO(Cody): Handle Ctrl+X+S, Ctrl+X+F etc.
		#self.connect(QtGui.QShortcut(QtGui.QKeySequence('Crtl+X, Ctrl+S'), self), QtCore.SIGNAL('activated()'), self.file_save())
		if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+S'):
			self.file_save()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+O'):
			self.file_open()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Down'):
			self.next_empty_line()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Up'):
			self.previous_empty_line()

			
if __name__ == '__main__':
   	#Every PyQt4 app must create an application object, sys.argv is arguments from cmd line
	app = QtGui.QApplication(sys.argv)
	w = MainWindow()
	w.show()
	sys.exit(app.exec_())
