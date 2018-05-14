#Custom text editor. For fun and getting used to Python again.
#WORKNAME: darkscrawl
#2018 Cody Azevedo

import sys
import os
import threading
import re
import string
import ntpath
import platform
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

		self.MIN_WIDTH = 785
		self.MIN_HEIGHT = 595
		self.widget.setMinimumSize(100, 100)
		self.widget.setAutoFillBackground(True)
		MainWindow.setCentralWidget(self.widget)
		MainWindow.setWindowTitle("darkscrawl 0.2")

		#Set widget background color to dark gray for debug purposes
		palette = self.widget.palette()
		role = self.widget.backgroundRole()
		palette.setColor(role, QColor(17, 17, 17))
		palette.setColor(QPalette.HighlightedText, QColor("red"))
		self.widget.setPalette(palette)
		
		self.create_text_box()
		
		#Bottom command label, for use in seeing what the editor is doing
		self.bottom_label = QtGui.QLabel("", self)
		self.bottom_label.setFixedHeight(self.font_metrics.height() + 2)
		self.bottom_label.setFont(self.bottom_font)
		self.bottom_label.setStyleSheet("""
							.QLabel {
							background-color: #0A0A0A;
							color: #BFBFBF;
							padding-top: 2px;
							}
						""")

		#Line widget, for keeping line, char count
		self.line_label = QtGui.QLabel("", parent = self.bottom_label)
		self.line_label.setFixedHeight(self.font_metrics.height() + 2)
		self.line_label.setFixedWidth(70)
		self.line_label.setFont(self.bottom_font)
		self.line_label.setAlignment(QtCore.Qt.AlignRight)
		self.line_label.setStyleSheet("""
							.QLabel {
							background-color: #0A0A0A;
							color: #BFBFBF;
							padding-top: 2px;
							}
						""")

		self.file_label = QtGui.QLabel("", parent = self.bottom_label)
		self.file_label.setFixedHeight(self.font_metrics.height() + 2)
		self.file_label.setFont(self.bottom_font)
		self.file_label.setAlignment(QtCore.Qt.AlignRight)
		self.file_label.setStyleSheet("""
							.QLabel {
							background-color: #0A0A0A;
							color: #BFBFBF;
							padding-top: 2px;
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
		self.horizontal_layout.addWidget(self.file_label)
		self.horizontal_layout.addWidget(self.line_label)

		self.widget.setLayout(self.grid_layout)
		self.grid_layout.addLayout(self.horizontal_layout, 600, 0)
		TextBox_Window.search_displayed = 0

		self.update_bottom_label("darkscrawl 0.2 by lostboycody")

		self.textbox.setCursorWidth(self.font_metrics.width(" "))

		#Open the intro file
		self.file = open("firstfile.txt", 'r')
		with self.file:
		   	text = self.file.read()
		   	self.textbox.setPlainText(text)
		   	self.file_length = len(text)
			
		self.open_name = os.path.realpath("firstfile.txt")
		self.file_name = self.get_file_name(str(self.open_name))

		self.file_label.setFixedWidth(self.font_metrics.width(self.file_name))
		self.file_label.setText("{}".format(self.file_name))
		self.update_cursor_position()

			
   	def create_text_box(self):
   		self.textbox = QPlainTextEdit(self.widget)
		self.textbox.setMinimumSize(10, 10)
		self.textbox.setLineWrapMode(0)
   		self.textbox.setStyleSheet("""
   				.QPlainTextEdit {
           		background-color: #121212;
           		color: #454545;
           		}
				.QScrollBar {
				height: 0px;
				width: 0px;
				}
       		""")
   		self.textbox.setFrameStyle(QFrame.NoFrame)
		self.textbox.ensureCursorVisible()

   		self.font = QtGui.QFont()
   		self.font.setPointSize(11)
   		self.font.setFamily("Consolas")
   		self.textbox.setFont(self.font)

   		self.bottom_font = QtGui.QFont()
   		self.bottom_font.setPointSize(10)
   		self.bottom_font.setFamily("Consolas")
		
		#On cursor position update, update the label
		self.textbox.cursorPositionChanged.connect(self.update_cursor_position)
		self.textbox.cursorPositionChanged.connect(self.highlight_current_line)

		#Set default tab width to 4 spaces
		TextBox_Window.font_metrics = QFontMetrics(self.font)
		self.textbox.setTabStopWidth(4 * self.font_metrics.width(' '))

		self.block = self.textbox.firstVisibleBlock()
		self.last_match = None
		
	#Set cursor position text, update actual cursor position in document
	#Updates actual cursor position when cursor is moved with a click or regular scrolling
	def update_cursor_position(self):
		self.cursor = self.textbox.textCursor()
		self.line = self.cursor.blockNumber() + 1
	   	self.col = self.cursor.columnNumber()

		self.document = self.textbox.document()
		self.block = self.document.findBlockByLineNumber(self.line - 1)

		self.line_label.setText("L{}|C{}".format(self.line, self.col))
		
   	def file_save(self):
		text = self.textbox.toPlainText()
		
		if TextBox_Window.file_opened:
			self.file = open(self.open_name, 'w')
			self.file.write(text)
			self.file.close()
			self.update_bottom_label("Wrote {}".format(self.open_name))
		else:
			self.save_name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
			self.file = open(self.save_name, 'w')
			self.file.write(text)
			self.file.close()
			self.update_bottom_label("Wrote {}".format(self.save_name))
				
	def file_open(self):
		TextBox_Window.file_opened = True
		self.dialog = QtGui.QFileDialog()
		self.dialog.setFileMode(QFileDialog.AnyFile)

		self.open_name = self.dialog.getOpenFileName(self, 'Open File')

		#If the file exists, open it
		if os.path.isfile(self.open_name):
			self.file = open(self.open_name, 'r')
			with self.file:
				text = self.file.read()
				self.textbox.setPlainText(text)
				self.file_length = len(text)
		#If the file doesn't exist, create new file
		elif not os.path.isfile(self.open_name):
			text = ""
			self.textbox.setPlainText(text)
			self.file_length = len(text)
			self.file_save()

		self.file_name = self.get_file_name(str(self.open_name))
		self.update_bottom_label("Opened {}".format(self.open_name))
		self.file_label.setText(self.file_name)
	   	self.file_label.setFixedWidth(self.font_metrics.width(self.file_name))

		self.block = self.textbox.firstVisibleBlock()
		self.update_cursor_position()


	def get_file_name(self, file_path):
		if platform.system() == "Windows":
			head, tail = ntpath.split(file_path)
			return tail
		else:
			head, tail = os.path.split(file_path)
			return tail
		
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
			if re.search('[^\s*$]', self.block.text()) and self.block.next().next().text() != self.first_block.text():
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
			if re.search('[^\s*$]', self.block.text()) and self.block.previous().previous().text() != "":
				self.block = self.block.previous()
			else:
				if self.block.previous().position() > 0:
   					self.block = self.block.previous()
				self.cursor = self.textbox.textCursor()
				self.cursor.setPosition(self.block.position())
				self.textbox.setTextCursor(self.cursor)
				break

	def highlight_current_line(self):
		self.extraSelections = []
		if not self.textbox.isReadOnly():
			self.selection = QTextEdit.ExtraSelection()
			self.lineColor = QColor(Qt.black)

			self.selection.format.setBackground(self.lineColor)
			self.selection.format.setProperty(QTextFormat.FullWidthSelection, QVariant(True))
			self.selection.cursor = self.textbox.textCursor()
			self.selection.cursor.clearSelection()
			self.extraSelections.append(self.selection)

		self.textbox.setExtraSelections(self.extraSelections)

	def setup_search_box(self):
		#If not already displayed, create the search widget and add them to layout
		if TextBox_Window.search_displayed == 0:
			TextBox_Window.query = SearchLineEdit("")
			self.query.setFixedHeight(self.font_metrics.height() + 2)
			self.query.setFont(self.bottom_font)
			self.query.setStyleSheet("""
								.SearchLineEdit {
								background-color: #050505;
								color: #BFBFBF;
								border: 0px solid black;
								}
							""")

			TextBox_Window.search_text = QtGui.QLabel(" Search:", parent = self.bottom_label)
			self.search_text.setFixedHeight(self.font_metrics.height() + 2)
			self.search_text.setFont(self.bottom_font)
			self.search_text.setStyleSheet("""
								.QLabel {
								background-color: #050505;
								color: #BFBFBF;
								padding-top: 2px;
								border: 0px solid black;
								}
							""")

			self.horizontal_layout.addWidget(self.search_text)
			self.horizontal_layout.addWidget(self.query)
			TextBox_Window.search_displayed = 1

		self.query.setFocus()
		self.query.returnPressed.connect(self.search_in_file)

	def remove_search_box(self):
		TextBox_Window.search_text.setParent(None)
		TextBox_Window.query.setParent(None)
		TextBox_Window.search_displayed = 0		

	def search_in_file(self):
		self.text = self.textbox.toPlainText()
		query = str(self.query.text())
		flags = re.I
		pattern = re.compile(query, flags)
		start = self.last_match.start() + 1 if self.last_match else 0

		self.last_match = pattern.search(self.text, start)
		if self.last_match:
			start = self.last_match.start()
			end = self.last_match.end()

			self.move_cursor(start, end)
			
	#Move cursor to found text and highlight it
	def move_cursor(self, start, end):
		cursor = self.textbox.textCursor()
		cursor.setPosition(start)
		cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end - start)
		self.textbox.setTextCursor(cursor)

#Custom QLineEdit for search query, removes search box when focus is lost
class SearchLineEdit(QtGui.QLineEdit, TextBox_Window):

	def __init__(self, parent = None):
		super(SearchLineEdit, self).__init__(parent)
		
   	def focusOutEvent(self, event):
		self.remove_search_box()
	
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
			self.file_open()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Down'):
			self.next_empty_line()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Up'):
			self.previous_empty_line()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+F'):
			self.setup_search_box()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+G'):
			self.remove_search_box()
		#TODO(Cody): Implement split buffer to edit two files
#		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+2'):
#			self.split_buffer()
				
if __name__ == '__main__':
   	#Every PyQt4 app must create an application object, sys.argv is arguments from cmd line
	app = QtGui.QApplication(sys.argv)
	w = MainWindow()
	w.resize(TextBox_Window.font_metrics.width(" ") * 89, TextBox_Window.font_metrics.lineSpacing() * 40)
	w.show()
	sys.exit(app.exec_())
