
#WORKNAME: darkscrawl
#This file handles the behaviour of the text editor.
#2018 Cody Azevedo

import sys
import os
import threading
import re
import string
import ntpath
import platform
import syntax
from threading import Thread
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4 import QtGui
from PyQt4.QtGui import *
from functools import partial

	
class TextBox_Window(QObject):	
	title_visible = True
	file_opened = False
	dir_browser_open = False
	dir_browser_opened = False
	file_is_modified = False
	active_window = ""
	file_name = ""
	file_name_2 = ""
	file_path = ""
	file_path_2 = ""
	main_file_path = ""
	nav_mode = False 
	nav_mode_2 = False 
	nav_tooltip = "This buffer is in navigation mode."
	ins_tooltip = "This buffer is in insert mode."
	nix_tooltip = "This file is encoded in the UNIX EOL format."
	dos_tooltip = "This file is encoded in the DOS (Windows) EOL format."	
			
	def __init__(self, parent=None):
		super(TextBox_Window, self).__init__(parent)
	
	def create_widget(self, MainWindow):
		#Widget is base UI objects in PyQt4
		self.widget = QtGui.QWidget()
	
		self.widget.setMinimumSize(100, 100)
		self.widget.setAutoFillBackground(True)
		MainWindow.setCentralWidget(self.widget)
		MainWindow.setWindowTitle("darkscrawl")
	
		#Set widget background color to dark gray for debug purposes
		palette = self.widget.palette()
		role = self.widget.backgroundRole()
		palette.setColor(role, QColor("#121212"))
		palette.setColor(QPalette.HighlightedText, QColor("red"))
		self.widget.setPalette(palette)
									
		TextBox_Window.font = QtGui.QFont()
		TextBox_Window.font.setPointSize(11)
		TextBox_Window.font.setFamily("Consolas")
	
		self.create_text_box()
		self.create_text_box2()
			
		self.create_browser_bar()
		self.create_browser_bar2()
			
		self.file_modified_label2.setHidden(not self.file_modified_label2.isHidden())				
		self.file_label2.setHidden(not self.file_label2.isHidden())	
		self.filemode_label2.setHidden(not self.filemode_label2.isHidden())
		self.editmode_label2.setHidden(not self.editmode_label2.isHidden())
		self.line_label2.setHidden(not self.line_label2.isHidden())
	
		self.file_modified_label.setFixedWidth(0)				
		self.file_label.setFixedWidth(0)
		self.filemode_label.setFixedWidth(0)
		self.editmode_label.setFixedWidth(0)
		self.line_label.setFixedWidth(0)	
				
		#Setup GridLayout, allows textbox window stretching
		TextBox_Window.grid_layout = QtGui.QGridLayout(self.widget)
		self.grid_layout.setMargin(0)
		self.grid_layout.setSpacing(0)
		self.grid_layout.setColumnStretch(0, 2)
	
		#Outer container widgets for each window
		TextBox_Window.outer_widget_1 = QScrollArea(self.widget)
		self.outer_widget_1.setStyleSheet("""
							QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
							QScrollArea { background-color: transparent; border: 0px solid black; }
							QWidget { background-color: transparent; }
						""")
		TextBox_Window.outer_widget_2 = QScrollArea(self.widget)
		self.outer_widget_2.setStyleSheet("""
							QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
							QScrollArea { background-color: transparent; border: 0px solid black; }
							QWidget { background-color: transparent; border-left: 1px solid #0c0c0c; }
						""")
			
		#Splitter, for dragging margin between split windows
		TextBox_Window.splitter = QSplitter(self.widget)
		self.splitter.setHandleWidth(1)
		self.splitter.addWidget(self.outer_widget_1)

		#Setup top browser line
		TextBox_Window.browser_layout = QtGui.QHBoxLayout()
		self.browser_layout.setMargin(0)
		self.browser_layout.setSpacing(0)
		
		TextBox_Window.browser_layout2 = QtGui.QHBoxLayout()
		self.browser_layout2.setMargin(0) 
		self.browser_layout2.setSpacing(0)
		
		TextBox_Window.browser_layout_widget = QScrollArea()
		self.browser_layout_widget.setStyleSheet("""
							QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
							QScrollArea { background-color: transparent; border: 0px solid black; }
							QWidget { background-color: transparent; border: 0px solid black; }
						""")
		self.browser_layout_widget.setLayout(self.browser_layout)
		self.browser_layout_widget.setFixedHeight(self.font_metrics.height() + 4)

		TextBox_Window.browser_layout_widget2 = QScrollArea(self.widget)
		self.browser_layout_widget2.setStyleSheet("""
							QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
							QScrollArea { background-color: transparent; border: 0px solid black; }
							QWidget { background-color: transparent; border: 0px solid black; }
						""")
		self.browser_layout_widget2.setLayout(self.browser_layout2)
		self.browser_layout_widget2.setFixedHeight(self.font_metrics.height() + 4)

		self.grid_layout.addWidget(self.browser_layout_widget, 0, 0)

		#Setup StackedLayout, for dir file browser
		self.stacked_layout = QtGui.QStackedLayout(self.outer_widget_1)
	   	self.stacked_layout.setMargin(0)
		self.stacked_layout.setSpacing(0)
		self.stacked_layout.addWidget(self.textbox)

		self.grid_layout.addWidget(self.splitter, 1, 0)

		self.scroll_area = QScrollArea()
		self.dialog_button_box = QDialogButtonBox(Qt.Vertical)
		self.stacked_layout.addWidget(self.dialog_button_box)
		self.stacked_layout.setAlignment(Qt.AlignLeft)
		self.scroll_area.setWidget(self.dialog_button_box)
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setStyleSheet("""
							QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
							QScrollArea { background-color: transparent; border: 0px solid black; }
							QWidget { background-color: transparent; border: 0px solid black; }
						""")
		self.stacked_layout.addWidget(self.scroll_area)

		#Setup HBoxLayout for browser layout section
		self.browser_layout.addWidget(self.main_text_label)
		self.browser_layout.addWidget(self.file_modified_label)
		self.browser_layout.addWidget(self.file_label)
		self.browser_layout.addWidget(self.filemode_label)
		self.browser_layout.addWidget(self.editmode_label)
		self.browser_layout.addWidget(self.line_label)
		
		#Search widget for dir browser
		TextBox_Window.dir_browser_search = SearchLineEdit()

		#Setup HBoxLayout for second window
		self.browser_layout2.addWidget(self.main_text_label2)
		self.browser_layout2.addWidget(self.file_modified_label2)
		self.browser_layout2.addWidget(self.file_label2)
		self.browser_layout2.addWidget(self.filemode_label2)
		self.browser_layout2.addWidget(self.editmode_label2)
		self.browser_layout2.addWidget(self.line_label2)
		
		self.widget.setLayout(self.grid_layout)

		TextBox_Window.search_displayed = False
		TextBox_Window.new_file_displayed = False
		
		self.update_bottom_label("darkscrawl 1.0 by lostboycody")

		self.textbox.setCursorWidth(self.font_metrics.width(" "))
		self.textbox2.setCursorWidth(self.font_metrics.width(" "))

		#Open the intro file, as read only
		self.file = open("firstfile.txt", 'rb')
		with self.file:
		   	text = self.file.read()
		   	self.textbox.setPlainText(text)
		   	self.file_length = len(text)
			
		self.update_cursor_position()
		self.textbox.setReadOnly(True)
		
	#Custom QPlainTextEdit
   	def create_text_box(self):
   		TextBox_Window.textbox = DarkPlainTextEdit(self.widget)

		#On cursor position update, update the label
		self.textbox.cursorPositionChanged.connect(self.update_cursor_position)
		self.textbox.setObjectName("Textbox")
		self.textbox.setCenterOnScroll(False)
				
		TextBox_Window.active_window = self.textbox.objectName()

	#New instance for split buffer capabilities
   	def create_text_box2(self):
		TextBox_Window.textbox2 = DarkPlainTextEdit(self.widget)
		
		self.textbox2.cursorPositionChanged.connect(self.update_cursor_position)
		self.last_match = None
		self.highlighter2 = syntax.DarkHighlighter(self.textbox2.document())

		self.fmt = QTextCharFormat()
		self.fmt.setForeground(QBrush(QColor("#454545")))
		self.textbox2.mergeCurrentCharFormat(self.fmt)

		self.textbox2.setObjectName("Textbox2")
		self.textbox2.setCenterOnScroll(False)
		
	def create_browser_bar(self):
		#Top label, used for file info, search, file browser etc.
		TextBox_Window.main_text_label = BrowserBarLabel(self.widget)
		self.main_text_label.setAlignment(QtCore.Qt.AlignLeft)

		#Display file modified
		TextBox_Window.file_modified_label = BrowserBarLabel(self.widget)
		self.file_modified_label.setObjectName("FileModifiedLabel")
		#Display file name
		TextBox_Window.file_label = BrowserBarLabel(self.main_text_label)
		#Monitor line, char count
		TextBox_Window.line_label = BrowserBarLabel(self.main_text_label)
		#Monitor EOL type
		TextBox_Window.filemode_label = BrowserBarLabel(self.main_text_label)
		#Monitor editing mode
		TextBox_Window.editmode_label = BrowserBarLabel(self.main_text_label)

	def create_browser_bar2(self):
		TextBox_Window.main_text_label2 = BrowserBarLabel(self.main_text_label)
		self.main_text_label2.setAlignment(QtCore.Qt.AlignLeft)

		TextBox_Window.file_modified_label2 = BrowserBarLabel(self.widget)
		TextBox_Window.file_modified_label2.setObjectName("FileModifiedLabel2")
		self.file_modified_label2.setStyleSheet("""
						BrowserBarLabel { background-color: #0A0A0A; color: brown; padding-top: 4px; margin: 0; height: 10px; font-size: 14px; font-weight: 700; }
					""")
		TextBox_Window.file_label2 = BrowserBarLabel(self.main_text_label)
		TextBox_Window.line_label2 = BrowserBarLabel(self.main_text_label)
		TextBox_Window.filemode_label2 = BrowserBarLabel(self.main_text_label)
		TextBox_Window.editmode_label2 = BrowserBarLabel(self.main_text_label)

	#Set cursor position text, update actual cursor position in document
	#Updates actual cursor position when cursor is moved with a click or regular scrolling
	def update_cursor_position(self):
		if TextBox_Window.active_window == "Textbox2":
			self.cursor = self.textbox2.textCursor()
		else:
			self.cursor = self.textbox.textCursor()

		self.line = self.cursor.blockNumber() + 1
	   	self.col = self.cursor.columnNumber()

		if TextBox_Window.active_window == "Textbox2":
			self.document = self.textbox2.document()
		else:
			self.document = self.textbox.document()
	
		self.block = self.document.findBlockByLineNumber(self.line - 1)
		
		if TextBox_Window.active_window == "Textbox2":
			self.line_label2.setText("L{} C{}".format(self.line, self.col))
			#Accomodate for right border
			if DarkPlainTextEdit.is_window_split:
				self.line_label2.setFixedWidth(self.font_metrics.width(self.line_label2.text()) + 12)
			else:
				self.line_label2.setFixedWidth(self.font_metrics.width(self.line_label2.text()) + 10)
		else:	
			self.line_label.setText("L{} C{}".format(self.line, self.col))
			if DarkPlainTextEdit.is_window_split:
				self.line_label.setFixedWidth(self.font_metrics.width(self.line_label.text()) + 12)
			else:
				self.line_label.setFixedWidth(self.font_metrics.width(self.line_label.text()) + 10)		

	def file_open(self, file):
		TextBox_Window.file_opened = True

		#Don't modify this file
		if "firstfile.txt" in str(os.path.abspath(file)):
			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setReadOnly(True)
			else:
				self.textbox.setReadOnly(True)
		else:
			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setReadOnly(False)
				self.textbox2.setStyle(self.textbox2.style())
				self.editmode_label2.setText("ins")
				self.editmode_label2.setToolTip(TextBox_Window.ins_tooltip)
			else:
				self.textbox.setReadOnly(False)
				self.textbox.setStyle(self.textbox.style())
				self.editmode_label.setText("ins")
				self.editmode_label.setToolTip(TextBox_Window.ins_tooltip)
		
		#If the file exists, open it and write to textbox
		if os.path.isfile(file):
			self.file = open(file, 'rb')
			with self.file:
				TextBox_Window.open_text = self.file.read()
				self.file_length = len(self.open_text)
				
			if TextBox_Window.active_window == "Textbox2":
				TextBox_Window.file_path_2 = str(os.path.join(os.getcwd(), file))
				TextBox_Window.file_name_2 = self.get_file_name(file)

				self.document = self.textbox2.document()
				self.textbox2.setPlainText(self.open_text)
				self.file_label2.setFixedWidth(self.font_metrics.width(self.file_label2.text()) + 5)
				self.line_label2.setFixedWidth(self.font_metrics.width(self.line_label2.text()) + 10)
				self.filemode_label2.setFixedWidth(self.font_metrics.width(self.filemode_label2.text()) + 10)
				self.editmode_label2.setFixedWidth(self.font_metrics.width(self.editmode_label2.text()) + 10)
				self.textbox2.textChanged.connect(self.update_file_modified)
			else:
				TextBox_Window.file_path = str(os.path.join(os.getcwd(), file))
				TextBox_Window.file_name = self.get_file_name(file)
				
				self.textbox.setPlainText(self.open_text)
				self.file_label.setFixedWidth(self.font_metrics.width(self.file_label.text()) + 5)
				self.line_label.setFixedWidth(self.font_metrics.width(self.line_label.text()) + 10)
				self.filemode_label.setFixedWidth(self.font_metrics.width(self.filemode_label.text()) + 10)
				self.editmode_label.setFixedWidth(self.font_metrics.width(self.editmode_label.text()) + 10)
				self.textbox.textChanged.connect(self.update_file_modified)
				
		#If the file doesn't exist, create new file and write blank text to textbox
		elif not os.path.isfile(file):
			self.new_file = self.new_file_name.text()
			file = open(self.new_file, 'ab')

			TextBox_Window.open_text = ""
			self.file_length = len(self.open_text)

			if TextBox_Window.active_window == "Textbox2":
				TextBox_Window.file_path_2 = str(os.path.join(os.getcwd(), str(self.new_file)))
				TextBox_Window.file_name_2 = self.new_file

				self.document = self.textbox2.document()
				self.textbox2.setPlainText(self.open_text)
				self.file_label2.setFixedWidth(self.font_metrics.width(self.file_label2.text()) + 5)
				self.line_label2.setFixedWidth(self.font_metrics.width(self.line_label2.text()) + 10)
				self.filemode_label2.setFixedWidth(self.font_metrics.width(self.filemode_label2.text()) + 10)
				self.editmode_label2.setFixedWidth(self.font_metrics.width(self.editmode_label2.text()) + 10)
				self.textbox2.textChanged.connect(self.update_file_modified)
			else:
				TextBox_Window.file_path = str(os.path.join(os.getcwd(), str(self.new_file)))
				TextBox_Window.file_name = self.new_file
								
				self.textbox.setPlainText(self.open_text)
				self.file_label.setFixedWidth(self.font_metrics.width(self.file_label.text()) + 5)
				self.line_label.setFixedWidth(self.font_metrics.width(self.line_label.text()) + 10)
				self.filemode_label.setFixedWidth(self.font_metrics.width(self.filemode_label.text()) + 10)
				self.editmode_label.setFixedWidth(self.font_metrics.width(self.editmode_label.text()) + 10)
				self.textbox.textChanged.connect(self.update_file_modified)
		
		if TextBox_Window.active_window == "Textbox2":
			self.main_text_label.setText("")
			self.file_modified_label2.setText("")
			self.file_modified_label2.setFixedWidth(0)
			self.file_label2.setText(self.file_name_2)
		   	self.file_label2.setFixedWidth(self.font_metrics.width(self.file_name_2) + 10)
			self.block = self.textbox2.firstVisibleBlock()
			self.update_bottom_label("Opened {}".format(self.file_name_2))

			try:
				if "\r\n" in open(file, "rb").read():
					self.filemode_label2.setText("dos")
					self.filemode_label2.setFixedWidth(self.font_metrics.width(self.filemode_label2.text()) + 10)
					self.filemode_label2.setToolTip(TextBox_Window.dos_tooltip)
				elif "\n" in open(file, "rb").read():
					self.filemode_label2.setText("nix")
					self.filemode_label2.setToolTip(TextBox_Window.nix_tooltip)
					self.filemode_label2.setFixedWidth(self.font_metrics.width(self.filemode_label2.text()) + 10)
			except:
				self.filemode_label2.setText("   ")
		else:
			self.file_modified_label.setText("")
			self.file_modified_label.setFixedWidth(0)
			self.file_label.setText(self.file_name)
		   	self.file_label.setFixedWidth(self.font_metrics.width(self.file_name) + 10)
			self.block = self.textbox.firstVisibleBlock()
			self.update_bottom_label("Opened {}".format(self.file_name))
			
			try:
				if "\r\n" in open(file, "rb").read():
					self.filemode_label.setText("dos")
					self.filemode_label.setToolTip(TextBox_Window.dos_tooltip)
					self.filemode_label.setFixedWidth(self.font_metrics.width(self.filemode_label.text()) + 10)
				elif "\n" in open(file, "rb").read():
					self.filemode_label.setText("nix")
					self.filemode_label.setToolTip(TextBox_Window.nix_tooltip)
					self.filemode_label.setFixedWidth(self.font_metrics.width(self.filemode_label.text()) + 10)
			except:
				self.filemode_label.setText("   ")

		if DarkPlainTextEdit.is_window_split:
			self.file_modified_label2.setVisible(True)
			self.file_label2.setVisible(True)
			self.filemode_label2.setVisible(True)
			self.editmode_label2.setVisible(True)
			self.line_label2.setVisible(True)
					
		self.update_cursor_position()
		self.dir_browser_search.setParent(None)

		TextBox_Window.dir_browser_open = False
		TextBox_Window.file_is_modified = False
		
		#Replace top browser after file browser closes
		self.browser_layout.addWidget(self.file_modified_label)
		self.browser_layout.addWidget(self.file_label)
		self.browser_layout.addWidget(self.filemode_label)
		self.browser_layout.addWidget(self.editmode_label)
		self.browser_layout.addWidget(self.line_label)

		TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width(), 0, 0, 0)

		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.main_file_path = TextBox_Window.file_path_2
			self.stacked_layout.setCurrentIndex(0)
			self.textbox2.setFocus()

			for widget in TextBox_Window.browser_layout_widget2.children():
				if isinstance(widget, BrowserBarLabel) or isinstance(widget, QLabel):
					widget.setProperty("is_active", True)
					widget.setStyle(widget.style())
		else:
			TextBox_Window.main_file_path = TextBox_Window.file_path
			self.stacked_layout.setCurrentIndex(0)
			self.textbox.setFocus()
			
			for widget in TextBox_Window.browser_layout_widget.children():
				if isinstance(widget, BrowserBarLabel) or isinstance(widget, QLabel):
					widget.setProperty("is_active", True)
					widget.setStyle(widget.style())

   	def file_save(self):
		if TextBox_Window.active_window == "Textbox2":
			self.save_text = self.textbox2.toPlainText()
		else:
			self.save_text = self.textbox.toPlainText()

		#Keep the file format if it exists
		try:
			if "\r\n" in open(self.file_path, "rb").read():
				self.save_text = self.convert_line_endings(str(self.save_text), 2)
			elif "\n" in open(self.file_path, "rb").read():
				self.save_text = self.convert_line_endings(str(self.save_text), 0)
			else:
				self.save_text = self.convert_line_endings(str(self.save_text), 0)
				
		#Otherwise make new file depending on OS
		except:
			if platform.system() == "Windows":
				self.save_text = self.convert_line_endings(str(self.save_text), 2)
			else:
				self.save_text = self.convert_line_endings(str(self.save_text), 0)
		
		#If the file has been opened, it exists
		if TextBox_Window.file_opened:
			self.file = open(TextBox_Window.main_file_path, 'wb+')

			#If the file has been modified, save it
			if TextBox_Window.file_is_modified:
				self.file.write(str(self.save_text).encode('utf-8'))
				self.file.close()
				
				if TextBox_Window.active_window == "Textbox2":
					self.file_modified_label2.setText("")
					self.file_modified_label2.setFixedWidth(0)
					self.update_bottom_label("Wrote {}".format(TextBox_Window.file_name_2))
				else:
					self.file_modified_label.setText("")
					self.file_modified_label.setFixedWidth(0)
					self.update_bottom_label("Wrote {}".format(TextBox_Window.file_name))
									
			#Write again to be safe.
			else:
				self.update_bottom_label("No changes need to be saved")
				self.file.write(str(self.save_text).encode('utf-8'))
				self.file.close()
			
				if TextBox_Window.active_window == "Textbox2":
					self.file_modified_label2.setText("")
					self.file_modified_label2.setFixedWidth(0)
				else:
					self.file_modified_label.setText("")
					self.file_modified_label.setFixedWidth(0)

			TextBox_Window.file_is_modified = False
				
		#Safekeeping, *just in case* the file hasn't been opened / doesn't exist yet
		else:
			self.update_bottom_label("This file doesn't exist on disk")
			
	#Keep OS-specific EOL format. (Add option to change later?)
	def convert_line_endings(self, temp, mode):
		#modes:  0 - Unix, 1 - Mac, 2 - DOS
		if mode == 0:
			temp = string.replace(temp, '\r\n', '\n')
			temp = string.replace(temp, '\r', '\n')
		elif mode == 1:
			temp = string.replace(temp, '\r\n', '\r')
			temp = string.replace(temp, '\n', '\r')
		elif mode == 2:
			import re
			temp = re.sub("\r(?!\n)|(?<!\r)\n", "\r\n", temp)
		return temp
			
	#TODO(Cody): Create new file interface when button pressed.
	def setup_new_file(self):
		if TextBox_Window.new_file_displayed == False:
			self.remove_bottom_label()
			self.dir_browser_search.setParent(None)		

			TextBox_Window.new_file_name = SearchLineEdit("")
			self.new_file_name.setFixedHeight(self.font_metrics.height() + 6)
			self.new_file_name.setFont(TextBox_Window.font)
			self.new_file_name.setStyleSheet("""
								.SearchLineEdit { background-color: #050505; color: #BFBFBF; padding-top: 4px; border: 0px solid black; font-size: 14px; font-weight: 700; }
							""")
			TextBox_Window.get_new_file = QtGui.QLabel(" New filename:", parent = self.main_text_label)
			self.get_new_file.setFixedHeight(self.font_metrics.height() + 6)
			self.get_new_file.setFont(TextBox_Window.font)
			self.get_new_file.setStyleSheet("""
								.QLabel { background-color: #050505; color: #BFBFBF; padding-top: 4px; border: 0px solid black; font-size: 14px; font-weight: 700; }
							""")
							
			if TextBox_Window.active_window == "Textbox2" and DarkPlainTextEdit.is_window_split:
				self.browser_layout2.addWidget(self.get_new_file)
				self.browser_layout2.addWidget(self.new_file_name)
			else:
				self.browser_layout.addWidget(self.get_new_file)
				self.browser_layout.addWidget(self.new_file_name)
			
			TextBox_Window.new_file_displayed = True

		self.new_file_path = os.path.join(os.getcwd(), str(self.new_file_name.text()))

		self.new_file_name.setFocus()
		self.new_file_name.returnPressed.connect(partial(self.file_open, self.new_file_path))
			
	#Return the file name itself, rather than the abspath
	#Compatible with Linux + Windows (MacOS?)
	def get_file_name(self, file_path):
		if platform.system() == "Windows":
			head, tail = ntpath.split(file_path)
			return tail
		else:
			head, tail = os.path.split(file_path)
			return tail

	#Method for passing full path generated by button presses in dir browser
	def open_file_path(self):
		self.file_path = str(os.path.join(os.getcwd(), f))
		self.new_file_open(self.file_path)
		
	#Set the bottom label text, reset after 5 seconds
	def update_bottom_label(self, bottomtext):
		if TextBox_Window.active_window == "Textbox2":
			self.main_text_label2.setText(bottomtext)
		else:
			self.main_text_label.setText(bottomtext)
		t = threading.Timer(5.0, self.remove_bottom_label)
		t.start()
		
	def remove_bottom_label(self):
		if not TextBox_Window.dir_browser_open:
			self.main_text_label.setText("")
			self.main_text_label2.setText("")

	def highlight_current_line(self):
		self.extraSelections = []
		if not self.textbox.isReadOnly():
			self.lineColor = QColor(Qt.black)
			self.selection = QTextEdit.ExtraSelection()
			self.selection.format.setBackground(self.lineColor)
			self.selection.format.setProperty(QTextFormat.FullWidthSelection, QVariant(True))
			self.selection.cursor = self.textbox.textCursor()
			self.selection.cursor.clearSelection()
			self.extraSelections.append(self.selection)

		self.textbox.setExtraSelections(self.extraSelections)

	#If not already displayed, create the search widget and add them to layout
	def setup_search_box(self):
		#Prevent duplication from multiple consecutive searches
		if TextBox_Window.search_displayed == False:
			TextBox_Window.query = SearchLineEdit("")
			self.query.setFixedHeight(self.font_metrics.height() + 6)
			self.query.setFont(TextBox_Window.font)
			TextBox_Window.search_text = QtGui.QLabel(" Search:", parent = self.main_text_label)
			self.search_text.setFixedHeight(self.font_metrics.height() + 6)
			self.search_text.setFont(TextBox_Window.font)
			self.search_text.setStyleSheet("""
								background-color: #050505; color: #BFBFBF; padding-top: 4px; border: 0px solid black; font-size: 14px; font-weight: 700;
							""")
							
			if TextBox_Window.active_window == "Textbox2":
				self.browser_layout2.addWidget(self.search_text)
				self.browser_layout2.addWidget(self.query)
			else:
				self.browser_layout.addWidget(self.search_text)
				self.browser_layout.addWidget(self.query)
		
		TextBox_Window.search_displayed = True
	
		self.query.setFocus()
		self.query.returnPressed.connect(self.search_in_file)
	
	def remove_search_box(self):
		TextBox_Window.search_text.setParent(None)
		TextBox_Window.query.setParent(None)
		TextBox_Window.search_displayed = False
		
		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.textbox2.setFocus()
		else:
			TextBox_Window.textbox.setFocus()
			
	def remove_new_file_box(self):
		TextBox_Window.new_file_name.setParent(None)
		TextBox_Window.get_new_file.setParent(None)
		if TextBox_Window.dir_browser_open:
			self.browser_layout.addWidget(self.dir_browser_search)
			self.dir_browser_search.setFocus()
		if TextBox_Window.active_window == "Textbox2" and not TextBox_Window.dir_browser_open:
			self.textbox2.setFocus()
		elif TextBox_Window.active_window == "Textbox" and not TextBox_Window.dir_browser_open:
			self.textbox.setFocus()
		TextBox_Window.new_file_displayed = False
	
	def search_in_file(self):
		if TextBox_Window.active_window == "Textbox2":
			self.text = self.textbox2.toPlainText()
		else:
			self.text = self.textbox.toPlainText()
					
		query = str(self.query.text())
		flags = re.I
		pattern = re.compile(query, flags)
		start = self.last_match.start() + 1 if self.last_match else 0
	
		self.last_match = pattern.search(self.text, start)
		if self.last_match:
			start = self.last_match.start()
			end = self.last_match.end()
			self.query.setStyleSheet("""
								.SearchLineEdit { background-color: #050505; color: #BFBFBF; border: 0px solid black; font-size: 14px; font-weight: bold; }
								""")
		else:
			end = 0
			self.query.setStyleSheet("""
								.SearchLineEdit { background-color: #1E0000; color: #BFBFBF; border: 0px solid black; font-size: 14px; font-weight: bold; }
								""")
	
		self.move_cursor(start, end)
			
	#Move cursor to found text and highlight it
	def move_cursor(self, start, end):
		if TextBox_Window.active_window == "Textbox2":
			cursor = self.textbox2.textCursor()
		else:
			cursor = self.textbox.textCursor()

		cursor.setPosition(start)
		cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end - start)

		if TextBox_Window.active_window == "Textbox2":
			self.textbox2.setTextCursor(cursor)
		else:
			self.textbox.setTextCursor(cursor)

	#Custom directory browser, more efficient than dialogbox
	def open_dir_browser(self):
		
		if not TextBox_Window.dir_browser_open:
			self.temp_dir = os.getcwd()
		TextBox_Window.dir_browser_open = True
		self.dir_browser_search.setText("")

		#Display the browser directory and remove the bottom label
		self.main_text_label.setProperty("is_active", True)

	   	self.current_dir = os.chdir(os.getcwd())
		self.dialog_button_box.clear()
		self.dir_label = str(os.getcwd()) + "\\"
	   	self.main_text_label.setText(self.dir_label)
	
		#Previous directory button
  		self.previous_dir_button = QPushButton("../")
		self.previous_dir_button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
	   	self.previous_dir_button.setStyleSheet("""
	   	  						.QPushButton { border: none; background-color: #121212; color: #009435; text-align: left; padding: 5px; font-family: Consolas; font-size: 14px; font-weight: bold; }
		   						.QPushButton:focus { outline: 0px; border: 2px solid #007765; }
	   	   					""")
		
		self.previous_dir_button.setAutoDefault(True)
		self.previous_dir_button.pressed.connect(self.open_previous_dir)
		self.dialog_button_box.addButton(self.previous_dir_button, QDialogButtonBox.ActionRole)

		for f in os.listdir("."):
			path = os.path.join(os.getcwd(), f)
			#For each directory in directory, add button that points to new directory
			if os.path.isdir(path):
				self.button = QPushButton(str(f))
				self.button.setObjectName(str(f))
				self.button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
	   	   		self.button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #121212; color: #009435; text-align: left; padding: 5px; font-family: Consolas; font-size: 14px; font-weight: bold; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #007765; }
	   	   						""")
				self.button.setAutoDefault(True)
				self.file_path = str(os.path.join(os.getcwd(), f))
				#Workaround for connecting file_open while passing parameter to it
				self.button.pressed.connect(partial(self.open_dir, f))
		   		self.dialog_button_box.addButton(self.button, QDialogButtonBox.ActionRole)

			#For each file in directory, add button that points to that file
			else:
	   	   		self.button = QPushButton(str(f))
				self.button.setObjectName(str(f))
				self.button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
	   	   		self.button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #121212; color: #AFAFAF; text-align: left; padding: 5px; font-family: Consolas; font-size: 14px; font-weight: bold; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #007765; }
	   	   						""")
				self.button.setAutoDefault(True)
				self.file_path = str(os.path.join(os.getcwd(), f))
				#Workaround for connecting file_open while passing parameter to it
				self.button.pressed.connect(partial(self.file_open, self.file_path))
		   		self.dialog_button_box.addButton(self.button, QDialogButtonBox.ActionRole)
				
		#Place new file button at the end of every directory, to create
		#a new file in that directory
		self.new_file_button = QPushButton("+ New file")
	   	self.new_file_button.setStyleSheet("""
		   	  						.QPushButton { border: none; background-color: #121212; color: white; text-align: left; padding: 5px; font-family: Consolas; font-size: 14px; font-weight: bold; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #007765; }
	   	   						""")
		self.new_file_button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
		self.new_file_button.setAutoDefault(True)
		self.new_file_button.pressed.connect(self.setup_new_file)
		self.dialog_button_box.addButton(self.new_file_button, QDialogButtonBox.ActionRole)

		self.stacked_layout.setCurrentIndex(1)

		self.file_label.setParent(None)
		self.file_modified_label.setParent(None)
		self.filemode_label.setParent(None)
		self.editmode_label.setParent(None)
		self.line_label.setParent(None)
		
		self.browser_layout.addWidget(self.dir_browser_search)
		self.dir_browser_search.setFixedHeight(self.font_metrics.height() + 6)
		self.dir_browser_search.setFont(TextBox_Window.font)
		self.dir_browser_search.textChanged.connect(self.update_dir_browser)
		self.dir_browser_search.returnPressed.connect(self.dialog_button_box.setFocus)
		self.dir_browser_search.setFocus()
				
	#Without opening file
	def close_dir_browser(self):
		if TextBox_Window.dir_browser_open == True:
			os.chdir(self.temp_dir)
			self.stacked_layout.setCurrentIndex(0)
			self.browser_layout.addWidget(self.file_modified_label)
			self.browser_layout.addWidget(self.file_label)
			self.browser_layout.addWidget(self.filemode_label)
			self.browser_layout.addWidget(self.editmode_label)
			self.browser_layout.addWidget(self.line_label)
	
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width(), 0, 0, 0)

			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setFocus()
			else:
				self.textbox.setFocus()
			
			self.main_text_label.setText("")
			self.dir_browser_search.setText("")
			self.dir_browser_search.setParent(None)
			TextBox_Window.dir_browser_open = False
			TextBox_Window.new_file_displayed = False
	
	#Open the next directory of the dir browser
	def open_dir(self, directory):
		TextBox_Window.dir_browser_open = True
		os.chdir(os.path.join(os.getcwd(), directory))
		self.dialog_button_box.clear()
		self.open_dir_browser()

	#Open the previous directory of the dir_browser
	def open_previous_dir(self):
		TextBox_Window.dir_browser_open = True
		self.change_to_previous_dir = os.chdir("..")
		self.dialog_button_box.clear()
		self.open_dir_browser()
		
	#Remove irrelevant dir buttons on keypress
	def update_dir_browser(self):
		for widget in self.dialog_button_box.children():
			if isinstance(widget, QPushButton):
				if not re.search(str(self.dir_browser_search.text()), widget.objectName(), re.IGNORECASE):
					self.dialog_button_box.removeButton(widget)
					widget.setParent(self.dialog_button_box)
				elif re.search(str(self.dir_browser_search.text()), widget.objectName(), re.IGNORECASE):
					self.dialog_button_box.addButton(widget, QDialogButtonBox.ActionRole)
				else:
					pass

	def update_file_modified(self):
		TextBox_Window.file_is_modified = True

		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.file_modified_label2.setText("~")
			TextBox_Window.file_modified_label2.setFixedWidth(self.font_metrics.width(" ") + 5)
			TextBox_Window.file_modified_label2.setToolTip("This buffer has been modified.")
		else:
			TextBox_Window.file_modified_label.setText("~")
			TextBox_Window.file_modified_label.setFixedWidth(self.font_metrics.width(" ") + 5)
			TextBox_Window.file_modified_label.setToolTip("This buffer has been modified.")


class DarkPlainTextEdit(QtGui.QPlainTextEdit, TextBox_Window):

	is_window_split = False
	
	def __init__(self, parent = None):
		super(DarkPlainTextEdit, self).__init__(parent)

		self.editor = QPlainTextEdit()
		self.setMinimumSize(10, 10)
		self.setLineWrapMode(0)
		self.setStyleSheet("""
	   				DarkPlainTextEdit { background-color: #121212; selection-color: #BFBFBF; selection-background-color: #020014; color: #378437; }
					DarkPlainTextEdit[readOnly=true] { color: #843837; }
					.QScrollBar { height: 0px; width: 0px; }
   	    		""")
		self.setReadOnly(False)

   		self.setFrameStyle(QFrame.NoFrame)
		self.ensureCursorVisible()

		self.font = QtGui.QFont()
 		self.font.setPointSize(11)
  		self.font.setFamily("Consolas")
   		self.setFont(self.font)

		#Set color format back to gray, so cursor stays green
		self.fmt = QTextCharFormat()
		self.fmt.setForeground(QBrush(QColor("#454545")))
		self.mergeCurrentCharFormat(self.fmt)
								
		#Set default tab width to 4 spaces
		TextBox_Window.font_metrics = QFontMetrics(self.font)
		self.setTabStopWidth(4 * self.font_metrics.width(' '))

		self.last_match = None
	
		self.highlighter = syntax.DarkHighlighter(self.document())
	
	#Handle custom keyevents that occur in the editor	
	def keyPressEvent(self, event):
   		k = event.key()
		m = int(event.modifiers())
		modifiers = QtGui.QApplication.keyboardModifiers()
						
		#Split window
		if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+X'):
			if not DarkPlainTextEdit.is_window_split:
				self.split_buffer()
				
		#Insert navigation
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Down') \
			or QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+K'):
			self.next_empty_line()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Up') \
			or QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+I'):
			self.previous_empty_line()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+J'):
			self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Left, Qt.ControlModifier)
			QCoreApplication.postEvent(self, self.nav_event)
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+L'):
			self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Right, Qt.ControlModifier)
			QCoreApplication.postEvent(self, self.nav_event)
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+E'):
			self.end_of_line()
							
		#Navigation navigation
		elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier and k == QtCore.Qt.Key_Down \
			or modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier and k == QtCore.Qt.Key_K:
			self.highlight_next_block()
		elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier and k == QtCore.Qt.Key_Up \
			or modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier and k == QtCore.Qt.Key_I:
			self.highlight_previous_block()
		elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier and k == QtCore.Qt.Key_E:
			self.highlight_to_end_of_line()
		elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier:
			self.highlight_mode = True
					
		#Switch editing mode / active window
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+M'):
			self.switch_editing_mode()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Q'):
			if not self.textbox.hasFocus():
				self.textbox.setFocus()
			else:
				self.textbox2.setFocus()
				
		if k == QtCore.Qt.Key_Return:		
			QtCore.QTimer.singleShot(10, self.auto_indent)
			
		#Emulate navigation mode arrow keys using I,J,K,L
		if TextBox_Window.active_window == "Textbox" and TextBox_Window.nav_mode:
			if k == QtCore.Qt.Key_I:
				self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Up, Qt.NoModifier)
				QCoreApplication.postEvent(self, self.nav_event)
			elif k == QtCore.Qt.Key_J:
				self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Left, Qt.NoModifier)
				QCoreApplication.postEvent(self, self.nav_event)
			elif k == QtCore.Qt.Key_K:
				self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
				QCoreApplication.postEvent(self, self.nav_event)
			elif k == QtCore.Qt.Key_L:
				self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Right, Qt.NoModifier)
				QCoreApplication.postEvent(self, self.nav_event)
				
		elif TextBox_Window.active_window == "Textbox2" and TextBox_Window.nav_mode_2:
			if k == QtCore.Qt.Key_I:
				self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Up, Qt.NoModifier)
				QCoreApplication.postEvent(self, self.nav_event)
			elif k == QtCore.Qt.Key_J:
				self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Left, Qt.NoModifier)
				QCoreApplication.postEvent(self, self.nav_event)
			elif k == QtCore.Qt.Key_K:
				self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
				QCoreApplication.postEvent(self, self.nav_event)
			elif k == QtCore.Qt.Key_L:
				self.nav_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Right, Qt.NoModifier)
				QCoreApplication.postEvent(self, self.nav_event)
			
		#Handle any other event normally
		QtGui.QPlainTextEdit.keyPressEvent(self, event)
			
	#Disable right-click in text edit
	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.RightButton:
			pass
		
	def focusInEvent(self, event):
		TextBox_Window.active_window = self.objectName()	
		super(DarkPlainTextEdit, self).focusInEvent(event)
		
		self.set_active_browser_bar()
					
	def focusOutEvent(self, event):
		TextBox_Window.active_window = self.objectName()	
		super(DarkPlainTextEdit, self).focusOutEvent(event)
		
		self.set_inactive_browser_bar()
		QApplication.restoreOverrideCursor()
											
	def set_active_browser_bar(self):
		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.main_file_path = TextBox_Window.file_path_2

			for widget in TextBox_Window.browser_layout_widget2.children():
				if isinstance(widget, BrowserBarLabel) or isinstance(widget, QLabel):
					widget.setProperty("is_active", True)
					widget.setStyle(widget.style())
					if widget.objectName() == "FileModifiedLabel2":
						widget.setStyleSheet("""
											background-color: #AFAFAF; color: brown; padding-top: 4px; margin: 0; height: 10px; font-size: 14px; font-weight: 700;\
										""")
		else:
			TextBox_Window.main_file_path = TextBox_Window.file_path
			
			for widget in TextBox_Window.browser_layout_widget.children():
				if isinstance(widget, BrowserBarLabel):
					widget.setProperty("is_active", True)
					widget.setStyle(widget.style())
					if widget.objectName() == "FileModifiedLabel":
						widget.setStyleSheet("""
											background-color: #AFAFAF; color: brown; padding-top: 4px; margin: 0; height: 10px; font-size: 14px; font-weight: 700;\
										""")
	def set_inactive_browser_bar(self):
		if not TextBox_Window.dir_browser_open:
			if TextBox_Window.active_window == "Textbox2":
				TextBox_Window.main_file_path = TextBox_Window.file_path_2

				for widget in TextBox_Window.browser_layout_widget2.children():
					if isinstance(widget, BrowserBarLabel) \
						and not TextBox_Window.search_displayed \
						and not TextBox_Window.new_file_displayed:
						widget.setProperty("is_active", False)
						widget.setStyle(widget.style())
						if widget.objectName() == "FileModifiedLabel2":
							widget.setStyleSheet("""
											background-color: #0A0A0A; color: brown; padding-top: 4px; margin: 0; height: 10px; font-size: 14px; font-weight: 700;\
										""")
			else:
				TextBox_Window.main_file_path = TextBox_Window.file_path
			
				for widget in TextBox_Window.browser_layout_widget.children():
					if isinstance(widget, BrowserBarLabel) \
						and not TextBox_Window.search_displayed \
						and not TextBox_Window.new_file_displayed:
						widget.setProperty("is_active", False)
						widget.setStyle(widget.style())
						if widget.objectName() == "FileModifiedLabel":
							widget.setStyleSheet("""
											background-color: #0A0A0A; color: brown; padding-top: 4px; margin: 0; height: 10px; font-size: 14px; font-weight: 700;\
										""")											
											
	def resizeEvent(self, event):
		TextBox_Window.browser_layout_widget.setFixedWidth(TextBox_Window.outer_widget_1.width() + 3)
		TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width(), 0, 0, 0)
					
	#Split the window to enable editing two files
	def split_buffer(self):
		DarkPlainTextEdit.is_window_split = True
		
		self.grid_layout.addWidget(self.browser_layout_widget2, 0, 0)
		self.container_widget = QScrollArea()
		self.container_widget.setStyleSheet("""
							QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
							QScrollArea { background-color: transparent; border: 0px solid black; }
							QWidget { background-color: transparent; border-left: 1px solid #0A0A0A; }
						""")
		
		self.splitter.addWidget(self.outer_widget_2)
		DarkPlainTextEdit.stacked_layout2 = QtGui.QStackedLayout(self.outer_widget_2)
		self.stacked_layout2.setMargin(0)
		self.stacked_layout2.setSpacing(0)
		
		self.stacked_layout2.addWidget(self.textbox2)
		self.textbox2.setPlainText("This is a second buffer.\nFor notes you don't want to save, write them here.")
		self.textbox2.setFocus()
		DarkPlainTextEdit.is_window_split = True
		
	#Detect indentation of previous line and insert tabs accordingly
	def auto_indent(self):
		self.document_text = self.document()
		self.cursor = self.textCursor()
		self.line = self.cursor.blockNumber() + 1
		self.col = self.cursor.columnNumber()
		
		self.block = self.document_text.findBlockByLineNumber(self.line - 2)

		#Insert tab for each tab at the start of previous line
		tab = "\t"
		tab_array = []
		string_beginning = len(str(self.block.text())) - len(str(self.block.text()).lstrip(tab))
		for i in range(string_beginning):
			tab_array.append(tab)
			
		#Insert extra tab if ":" or "{" at EOL
		line_text = str(self.block.text())
		line_length = len(str(self.block.text()))
		if line_length > 0:
			if line_text[line_length - 1] == ":" or line_text[line_length - 1] == "{":
				tab_array.append(tab)
		
		tab_string = "".join(tab_array)
		self.cursor.insertText(tab_string)
		
	#Ctrl + Down scrolling: moves cursor to next block of code
	def next_empty_line(self):			
		self.cursor = self.textCursor()
		self.line = self.cursor.blockNumber() + 1
		self.document_text = self.document()
		self.block = self.document_text.findBlockByLineNumber(self.line - 1)
	
		self.first_block = self.firstVisibleBlock()
		
		while self.block.isValid():
			if re.search('[^\s*$]', self.block.next().text()):
				self.block = self.block.next()
			else:
				if self.block.next().position() >= self.cursor.position() and self.block.next().position() != 0:
					self.block = self.block.next()
					self.cursor = self.textCursor()
					self.cursor.setPosition(self.block.position())
					self.setTextCursor(self.cursor)
 				break

	#Ctrl + Up scrolling: moves cursor to previous block of code
	def previous_empty_line(self):
		self.cursor = self.textCursor()
		self.line = self.cursor.blockNumber() + 1
		self.document_text = self.document()
		self.block = self.document_text.findBlockByLineNumber(self.line - 1)

		self.first_block = self.firstVisibleBlock()
		
		while self.block.isValid():
			if re.search('[^\s*$]', self.block.previous().text()):
				self.block = self.block.previous()
			else:
				if self.block.previous().position() > 0:
   					self.block = self.block.previous()	
					self.cursor = self.textCursor()
					self.cursor.setPosition(self.block.position())
					self.setTextCursor(self.cursor)
				break

	#Ctrl+Shift+Down scrolling highlights next block
	def highlight_next_block(self):
		self.cursor = self.textCursor()
		self.line = self.cursor.blockNumber() + 1
		self.document_text = self.document()
		self.block = self.document_text.findBlockByLineNumber(self.line - 1)
	
		self.first_block = self.firstVisibleBlock()
		
		while self.block.isValid():
			if re.search('[^\s*$]', self.block.next().text()):
				self.block = self.block.next()
			else:
				if self.block.next().position() >= self.cursor.position() and self.block.next().position() != 0:
					self.block = self.block.next()
					self.cursor.setPosition(self.block.position(), self.cursor.KeepAnchor)
					self.setTextCursor(self.cursor)
 				break

	#Ctrl+Shift+Up scrolling highlights previous block
	def highlight_previous_block(self):	
		self.cursor = self.textCursor()
		self.line = self.cursor.blockNumber() + 1
		self.document_text = self.document()
		self.block = self.document_text.findBlockByLineNumber(self.line - 1)

		self.first_block = self.firstVisibleBlock()
		
		while self.block.isValid():
			if re.search('[^\s*$]', self.block.previous().text()): #and self.block.previous().previous().text() != "":
				self.block = self.block.previous()
			else:
				if self.block.previous().position() > 0:
   					self.block = self.block.previous()
					self.cursor = self.textCursor()
					self.cursor.setPosition(self.block.position(), self.cursor.KeepAnchor)
					self.setTextCursor(self.cursor)
				break

	#Move cursor to end of line
	def end_of_line(self):
		self.cursor = self.textCursor()
		self.line = self.cursor.blockNumber() + 1
		self.block = self.document_text.findBlockByLineNumber(self.line - 1)

		self.cursor.movePosition(self.cursor.EndOfLine, self.cursor.MoveAnchor, len(str(self.block.text())))
		self.setTextCursor(self.cursor)
		
	#Move cursor to start of line
	def highlight_to_end_of_line(self):
		self.cursor = self.textCursor()
		self.line = self.cursor.blockNumber() + 1
		self.block = self.document_text.findBlockByLineNumber(self.line - 1)

		self.cursor.movePosition(self.cursor.EndOfLine, self.cursor.KeepAnchor, len(str(self.block.text())))
		self.setTextCursor(self.cursor)
	
	def switch_editing_mode(self):
		if TextBox_Window.active_window == "Textbox2":		
			if TextBox_Window.textbox2.isReadOnly():
				self.textbox2.setReadOnly(False)
				self.textbox2.setStyle(TextBox_Window.textbox2.style())
				self.editmode_label2.setText("ins")
				self.editmode_label2.setToolTip(TextBox_Window.ins_tooltip)
			else:
				self.textbox2.setReadOnly(True)
				self.textbox2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
				self.textbox2.setStyle(TextBox_Window.textbox2.style())
				self.editmode_label2.setText("nav")
				self.editmode_label2.setToolTip(TextBox_Window.nav_tooltip)
	
			TextBox_Window.nav_mode_2 = not TextBox_Window.nav_mode_2
		else:
			if TextBox_Window.textbox.isReadOnly():
				self.textbox.setReadOnly(False)
				self.textbox.setStyle(TextBox_Window.textbox.style())
				self.editmode_label.setText("ins")
				self.editmode_label.setToolTip(TextBox_Window.ins_tooltip)
			else:
				self.textbox.setReadOnly(True)
				self.textbox.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
				self.textbox.setStyle(TextBox_Window.textbox.style())
				self.editmode_label.setText("nav")
				self.editmode_label.setToolTip(TextBox_Window.nav_tooltip)
		
			TextBox_Window.nav_mode = not TextBox_Window.nav_mode			

#Custom QLineEdit for search query, removes search box when focus is lost
class SearchLineEdit(QtGui.QLineEdit, TextBox_Window):

	def __init__(self, parent = None):
		super(SearchLineEdit, self).__init__(parent)
		self.search_line_edit = QLineEdit()
		self.setStyleSheet("""
							SearchLineEdit { background-color: #050505; color: #BFBFBF; border: 0px solid black; font-size: 14px; font-weight: bold; }
						""")
		
   	def focusOutEvent(self, event):
		if TextBox_Window.search_displayed == True:
			TextBox_Window.search_displayed == False
			self.remove_search_box()
		elif TextBox_Window.new_file_displayed == True:
			TextBox_Window.new_file_displayed == False
			self.remove_new_file_box()
			
#Custom QLabel for top bar
class BrowserBarLabel(QtGui.QLabel, TextBox_Window):

	def __init__(self, parent = None):
		super(BrowserBarLabel, self).__init__(parent)
		
		self.browser_label = QLabel()
		self.setFixedHeight(self.font_metrics.height() + 4)
		self.setFont(TextBox_Window.font)
		self.setAlignment(QtCore.Qt.AlignRight)
		self.setStyleSheet("""
						BrowserBarLabel { background-color: #0A0A0A; color: #AFAFAF; padding-top: 4px; margin: 0; height: 10px; font-size: 14px; font-weight: 700; border-right: 3px solid #121212; }
						BrowserBarLabel[is_active=true] { background-color: #AFAFAF; color: black; padding-top: 4px; margin: 0; height: 10px; font-size: 14px; font-weight: 700; border-right: 3px solid #121212;}
					""")
	
	
