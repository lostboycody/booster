#WORKNAME: darkscrawl
#This file handles the behaviour of the text editor.
#2018 Cody Azevedo

import ntpath
import os
import platform
import re
import string
import sys
import threading
from functools import partial
from threading import Thread

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import syntax

class TextBox_Window(QObject):
	title_visible = True
	file_opened = False
	dir_browser_open = False
	dir_browser_opened = False
	file_1_is_modified = False
	file_2_is_modified = False
	has_been_split = False
	active_window = ""
	file_name = "null.txt"
	file_name_2 = "null.txt"
	file_path = ""
	file_path_2 = ""
	main_file_path = ""
	nav_mode = False 
	nav_mode_2 = False 
	preference_value = ""
	nav_tooltip = "This buffer is in navigation mode."
	ins_tooltip = "This buffer is in insert mode."
	nix_tooltip = "This file is encoded in the UNIX EOL format."
	dos_tooltip = "This file is encoded in the DOS (Windows) EOL format."
	file_extensions = [".py", ".java", ".cpp", ".c", ".htm", ".html", ".js",
	".css", ".php", ".h", ".cs", ".sh"]
	syntax_theme = ""
	temp_dir = os.getcwd()
	color_themes = ["Monochrome", "Red", "Orange", "Yellow", "Green", "Green (Muted)", "Blue", "Flo\'s V8 Cafe", "Stranger Things", "Royal", \
	"Scoops Ahoy", "Old Locomotive", "Winter", ]
	font_sizes = []
	current_dir_list = []
	
	for i in range(10, 21):
		font_sizes.append(i)
			
	def __init__(self, parent=None):
		super(TextBox_Window, self).__init__(parent)
			
	def create_widget(self, MainWindow):
		#Widget is base UI objects in PyQt4
		self.widget = QtGui.QWidget()
	
		self.widget.setMinimumSize(100, 100)
		self.widget.setAutoFillBackground(True)
		MainWindow.setCentralWidget(self.widget)
		MainWindow.setWindowTitle("Booster")
	
		#Set widget background color to dark gray for debug purposes
		palette = self.widget.palette()
		role = self.widget.backgroundRole()
		palette.setColor(role, QColor("#181c1f"))
		palette.setColor(QPalette.HighlightedText, QColor("red"))
		self.widget.setPalette(palette)
		
		TextBox_Window.font = QtGui.QFont()
		TextBox_Window.font.setPointSize(11)
		TextBox_Window.font.setFamily('Noto Mono')

		TextBox_Window.bar_font = QtGui.QFont()
		TextBox_Window.bar_font.setPointSize(11)
		TextBox_Window.bar_font.setFamily('Noto Mono')	
		
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
		try:
			if str(sys.argv[1]) == "forest":
				self.outer_widget_2.setStyleSheet("""
									QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
									QScrollArea { background-color: transparent; border: 0px solid black; }
									QWidget { background-color: transparent; border-left: 1px solid #BBC1A8; }
								""")
			else:
				self.outer_widget_2.setStyleSheet("""
									QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
									QScrollArea { background-color: transparent; border: 0px solid black; }
									QWidget { background-color: #29353E; border-left: 1px solid #2E3B44; }
								""")
		except:
			self.outer_widget_2.setStyleSheet("""
								QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
								QScrollArea { background-color: transparent; border: 0px solid black; }
								QWidget { background-color: transparent; border-left: 1px solid #2E3B44; }
							""")
						
		#Splitter, for dragging margin between split windows
		TextBox_Window.splitter = QSplitter(self.widget)
		self.splitter.setHandleWidth(1)
		self.splitter.setStyleSheet("""
							.QSplitter::handle { background-color: transparent; }
						""")
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
		self.browser_layout_widget.setFixedHeight(self.bar_font_metrics.height() + 4)

		TextBox_Window.browser_layout_widget2 = QScrollArea(self.widget)
		try:
			if str(sys.argv[1]) == "forest":
				self.browser_layout_widget2.setStyleSheet("""
									QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
									QScrollArea { background-color: transparent; border: 0px solid black; }
									QWidget { background-color: #BBC1A8; border: 0px solid black; }
								""")
			else:
				self.browser_layout_widget2.setStyleSheet("""
									QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
									QScrollArea { background-color: transparent; border: 0px solid black; }
									QWidget { background-color: #181c1f; border: 0px solid black; }
								""")
		except:
			self.browser_layout_widget2.setStyleSheet("""
								QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
								QScrollArea { background-color: transparent; border: 0px solid black; }
								QWidget { background-color: #181c1f; border: 0px solid black; }
								""")
		self.browser_layout_widget2.setLayout(self.browser_layout2)
		self.browser_layout_widget2.setFixedHeight(self.bar_font_metrics.height() + 4)

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
		
		#Displays search results in dir browser
		TextBox_Window.dir_browser_search = QTextEdit()
		self.dir_browser_search.setObjectName("Browser Search")
		
		#Search widget for searching in directory
		self.query_string = SearchLineEdit("")
		self.query_string.setObjectName("File Query")
		self.query_string.setMinimumWidth(self.bar_font_metrics.width(" "))
		self.query_string.setFixedHeight(self.bar_font_metrics.height() + 6)
		self.query_string.setFont(TextBox_Window.bar_font)
		self.query_string.textEdited.connect(self.update_dir_browser)
		self.query_string.returnPressed.connect(self.do_query)

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
		TextBox_Window.preferences_displayed = False
		
		self.update_bottom_label("Booster by lostboycody")

		self.textbox.setCursorWidth(self.font_metrics.width(" "))
		self.textbox2.setCursorWidth(self.font_metrics.width(" "))

		#Open the intro file, as read only
		self.file_open("firstfile.txt")
		
	#Custom QPlainTextEdit
   	def create_text_box(self):
   		TextBox_Window.textbox = BoostPlainTextEdit(self.widget)

		#On cursor position update, update the label
		self.textbox.cursorPositionChanged.connect(self.update_cursor_position)
		self.textbox.setObjectName("Textbox")
		self.textbox.setCenterOnScroll(False)
				
		TextBox_Window.active_window = self.textbox.objectName()

	#New instance for split buffer capabilities
   	def create_text_box2(self):
		TextBox_Window.textbox2 = BoostPlainTextEdit(self.widget)
		
		self.textbox2.cursorPositionChanged.connect(self.update_cursor_position)
		self.last_match = None

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
		TextBox_Window.file_label2 = BrowserBarLabel(self.main_text_label)
		TextBox_Window.line_label2 = BrowserBarLabel(self.main_text_label)
		TextBox_Window.filemode_label2 = BrowserBarLabel(self.main_text_label)
		TextBox_Window.editmode_label2 = BrowserBarLabel(self.main_text_label)
		
	def reset_browser_bar(self):
		if not TextBox_Window.dir_browser_open:
			if TextBox_Window.active_window == "Textbox2":
				self.main_text_label2.setParent(None)
				self.file_modified_label2.setParent(None)
				self.file_label2.setParent(None)
				self.filemode_label2.setParent(None)
				self.editmode_label2.setParent(None)
				self.line_label2.setParent(None)
				
				self.browser_layout2.addWidget(self.main_text_label2)
				self.browser_layout2.addWidget(self.file_modified_label2)
				self.browser_layout2.addWidget(self.file_label2)
				self.browser_layout2.addWidget(self.filemode_label2)
				self.browser_layout2.addWidget(self.editmode_label2)
				self.browser_layout2.addWidget(self.line_label2)
			else:
				self.main_text_label.setParent(None)
				self.file_modified_label.setParent(None)
				self.file_label.setParent(None)
				self.filemode_label.setParent(None)
				self.editmode_label.setParent(None)
				self.line_label.setParent(None)
							
				self.browser_layout.addWidget(self.main_text_label)
				self.browser_layout.addWidget(self.file_modified_label)
				self.browser_layout.addWidget(self.file_label)
				self.browser_layout.addWidget(self.filemode_label)
				self.browser_layout.addWidget(self.editmode_label)
				self.browser_layout.addWidget(self.line_label)
				
				self.main_text_label.setText("")
		
		if TextBox_Window.search_displayed:
			self.remove_search_box()
			TextBox_Window.search_displayed = False
		elif TextBox_Window.new_file_displayed:
			self.remove_new_file_box()
			TextBox_Window.new_file_displayed = False
 
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

		if TextBox_Window.file_name != "null.txt":
			if TextBox_Window.active_window == "Textbox2":
				self.line_label2.setText("L#{} C#{}".format(self.line, self.col))
				#Accomodate for right border
				if BoostPlainTextEdit.is_window_split:
					self.line_label2.setFixedWidth(self.bar_font_metrics.width(self.line_label2.text()) + 7)
				else:
					self.line_label2.setFixedWidth(self.bar_font_metrics.width(self.line_label2.text()) + 10)
			else:	
				self.line_label.setText("L#{} C#{}".format(self.line, self.col))
				if BoostPlainTextEdit.is_window_split:
					self.line_label.setFixedWidth(self.bar_font_metrics.width(self.line_label.text()) + 7)
				else:
					self.line_label.setFixedWidth(self.bar_font_metrics.width(self.line_label.text()) + 10)
					
		self.highlight_current_line()
		
	def file_open(self, file):
		TextBox_Window.file_opened = True
		
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
				self.file_label2.setFixedWidth(self.bar_font_metrics.width(self.file_label2.text()) + 5)
				self.line_label2.setFixedWidth(self.bar_font_metrics.width(self.line_label2.text()) + 10)
				self.filemode_label2.setFixedWidth(self.bar_font_metrics.width(self.filemode_label2.text()) + 10)
				self.editmode_label2.setFixedWidth(self.bar_font_metrics.width(self.editmode_label2.text()) + 10)
				self.textbox2.textChanged.connect(self.update_file_modified)
			else:
				TextBox_Window.file_path = str(os.path.join(os.getcwd(), file))
				TextBox_Window.file_name = self.get_file_name(file)
								
				self.textbox.setPlainText(self.open_text)
				self.file_label.setFixedWidth(self.bar_font_metrics.width(self.file_label.text()) + 5)
				self.line_label.setFixedWidth(self.bar_font_metrics.width(self.line_label.text()) + 10)
				self.filemode_label.setFixedWidth(self.bar_font_metrics.width(self.filemode_label.text()) + 10)
				self.editmode_label.setFixedWidth(self.bar_font_metrics.width(self.editmode_label.text()) + 10)
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

				if platform.system() == "Windows":
					self.filemode_label2.setText("dos")
				else:
					self.filemode_label2.setText("nix")

				self.document = self.textbox2.document()
				self.textbox2.setPlainText(self.open_text)
				self.file_label2.setFixedWidth(self.bar_font_metrics.width(self.file_label2.text()) + 5)
				self.line_label2.setFixedWidth(self.bar_font_metrics.width(self.line_label2.text()) + 10)
				self.filemode_label2.setFixedWidth(self.bar_font_metrics.width(self.filemode_label2.text()) + 10)
				self.editmode_label2.setFixedWidth(self.bar_font_metrics.width(self.editmode_label2.text()) + 10)
				self.textbox2.textChanged.connect(self.update_file_modified)
				self.textbox2.setFocus()
			else:
				TextBox_Window.file_path = str(os.path.join(os.getcwd(), str(self.new_file)))
				TextBox_Window.file_name = self.new_file

				if platform.system() == "Windows":
					self.filemode_label.setText("dos")
				else:
					self.filemode_label.setText("nix")

				self.textbox.setPlainText(self.open_text)
				self.file_label.setFixedWidth(self.bar_font_metrics.width(self.file_label.text()) + 5)
				self.line_label.setFixedWidth(self.bar_font_metrics.width(self.line_label.text()) + 10)
				self.filemode_label.setFixedWidth(self.bar_font_metrics.width(self.filemode_label.text()) + 10)
				self.editmode_label.setFixedWidth(self.bar_font_metrics.width(self.editmode_label.text()) + 10)
				self.textbox.textChanged.connect(self.update_file_modified)
				self.textbox.setFocus()
							
		if TextBox_Window.active_window == "Textbox2":
			self.main_text_label.setText("")
			self.file_label2.setText(self.file_name_2)
		   	self.file_label2.setFixedWidth(self.bar_font_metrics.width(self.file_name_2) + 10)
			self.block = self.textbox2.firstVisibleBlock()
			self.update_bottom_label("Opened {}".format(self.file_name_2))
			
			try:
				if "\r\n" in open(file, "rb").read():
					self.filemode_label2.setText("dos")
					self.filemode_label2.setFixedWidth(self.bar_font_metrics.width(self.filemode_label2.text()) + 10)
					self.filemode_label2.setToolTip(TextBox_Window.dos_tooltip)
				elif "\n" in open(file, "rb").read():
					self.filemode_label2.setText("nix")
					self.filemode_label2.setToolTip(TextBox_Window.nix_tooltip)
					self.filemode_label2.setFixedWidth(self.bar_font_metrics.width(self.filemode_label2.text()) + 10)
			except:
				pass
		else:
			self.file_modified_label.setText("")
			self.file_modified_label.setFixedWidth(0)
			self.file_label.setText(self.file_name)
		   	self.file_label.setFixedWidth(self.bar_font_metrics.width(self.file_name) + 10)
			self.block = self.textbox.firstVisibleBlock()
			self.update_bottom_label("Opened {}".format(self.file_name))
											
			try:
				if "\r\n" in open(file, "rb").read():
					self.filemode_label.setText("dos")
					self.filemode_label.setToolTip(TextBox_Window.dos_tooltip)
					self.filemode_label.setFixedWidth(self.bar_font_metrics.width(self.filemode_label.text()) + 10)
				elif "\n" in open(file, "rb").read():
					self.filemode_label.setText("nix")
					self.filemode_label.setToolTip(TextBox_Window.nix_tooltip)
					self.filemode_label.setFixedWidth(self.bar_font_metrics.width(self.filemode_label.text()) + 10)
			except:
				pass

		if BoostPlainTextEdit.is_window_split:
			self.file_modified_label2.setVisible(True)
			self.file_label2.setVisible(True)
			self.filemode_label2.setVisible(True)
			self.editmode_label2.setVisible(True)
			self.line_label2.setVisible(True)
					
		self.update_cursor_position()
		self.query_string.setParent(None)
		self.dir_browser_search.setParent(None)
		
		TextBox_Window.dir_browser_open = False

		self.apply_syntax_highlight(TextBox_Window.syntax_theme)
		
		#Replace top browser after file browser closes
		self.browser_layout.addWidget(self.file_modified_label)
		self.browser_layout.addWidget(self.file_label)
		self.browser_layout.addWidget(self.filemode_label)
		self.browser_layout.addWidget(self.editmode_label)
		self.browser_layout.addWidget(self.line_label)		
		self.file_modified_label.setVisible(True)
		self.file_label.setVisible(True)
		self.filemode_label.setVisible(True)
		self.editmode_label.setVisible(True)
		self.line_label.setVisible(True)
		
		#Don't modify this file
		if "firstfile.txt" in str(os.path.abspath(file)):
			self.file_modified_label.setVisible(False)
			self.file_label.setVisible(False)
			self.filemode_label.setVisible(False)
			self.editmode_label.setVisible(False)
			self.line_label.setVisible(False)

			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setReadOnly(True)
			else:
				self.textbox.setReadOnly(True)		

		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.main_file_path = TextBox_Window.file_path_2
			TextBox_Window.file_2_is_modified = False
			self.textbox2.setFocus()

			for widget in TextBox_Window.browser_layout_widget2.children():
				if isinstance(widget, BrowserBarLabel) or isinstance(widget, QLabel):
					widget.setProperty("is_active", True)
					widget.setStyle(widget.style())
		else:
			TextBox_Window.main_file_path = TextBox_Window.file_path
			TextBox_Window.file_1_is_modified = False
			self.textbox.setFocus()
	
			for widget in TextBox_Window.browser_layout_widget.children():
				if isinstance(widget, BrowserBarLabel) or isinstance(widget, QLabel):
					widget.setProperty("is_active", True)
					widget.setStyle(widget.style())
					
		QtCore.QTimer.singleShot(20, self.set_file_not_modified)
			
		self.browser_layout_widget.setFixedHeight(self.bar_font_metrics.height() + 4)
		self.browser_layout_widget2.setFixedHeight(self.bar_font_metrics.height() + 4)		

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
				
			if TextBox_Window.active_window == "Textbox2" and TextBox_Window.file_2_is_modified:
				self.file.write(str(self.save_text).encode('utf-8'))
				self.file.close()

				self.file_modified_label2.setText("")
				self.file_modified_label2.setFixedWidth(0)
				self.update_bottom_label("Wrote {}".format(TextBox_Window.file_name_2))
				TextBox_Window.file_2_is_modified = False
			elif TextBox_Window.active_window == "Textbox" and TextBox_Window.file_1_is_modified:
				self.file.write(str(self.save_text).encode('utf-8'))
				self.file.close()

				self.file_modified_label.setText("")
				self.file_modified_label.setFixedWidth(0)
				self.update_bottom_label("Wrote {}".format(TextBox_Window.file_name))
				TextBox_Window.file_1_is_modified = False
									
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
				
		#Safekeeping, *just in case* the file hasn't been opened / doesn't exist yet
		else:
			self.update_bottom_label("This file doesn't exist on disk.")
			
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
			
	def setup_new_file(self):
		if TextBox_Window.new_file_displayed == False:
			self.remove_bottom_label()
			self.dir_browser_search.setParent(None)

			TextBox_Window.new_file_name = SearchLineEdit("")
			self.new_file_name.setFixedHeight(self.bar_font_metrics.height() + 6)
			self.new_file_name.setFont(TextBox_Window.bar_font)
			self.new_file_name.setStyleSheet("""
								.SearchLineEdit { background-color: #181c1f; color: #e8e4cf; padding-top: 3px; border: 0px solid black; font-size: 14px; }
							""")
			TextBox_Window.get_new_file = QtGui.QLabel("New filename:", parent = self.main_text_label)
			self.get_new_file.setFixedHeight(self.bar_font_metrics.height() + 6)
			self.get_new_file.setFont(TextBox_Window.bar_font)
			self.get_new_file.setStyleSheet("""
								.QLabel { background-color: #181c1f; color: #6684e1; padding-top: 3px; border: 0px solid black; font-size: 14px; }
							""")
							
			if TextBox_Window.active_window == "Textbox2" and BoostPlainTextEdit.is_window_split:
				self.browser_layout2.addWidget(self.get_new_file)
				self.browser_layout2.addWidget(self.new_file_name)
				self.main_text_label2.setParent(None)
			else:
				self.browser_layout.addWidget(self.get_new_file)
				self.browser_layout.addWidget(self.new_file_name)
				self.main_text_label.setParent(None)
			
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
		
	def set_preference(self, preference):
		if preference in TextBox_Window.color_themes:
			self.apply_syntax_highlight(preference)
		elif preference in TextBox_Window.font_sizes:
			TextBox_Window.font.setPointSize(int(preference))
			self.font_metrics = QFontMetrics(TextBox_Window.font)
			self.textbox.setCursorWidth(self.font_metrics.width(" "))
			self.textbox2.setCursorWidth(self.font_metrics.width(" "))
			self.textbox.setFont(TextBox_Window.font)
			self.textbox2.setFont(TextBox_Window.font)

		self.close_dialog_button_box()
		self.set_textbox_focus()
   					
	#Set focus to the textbox that last had focus.
	def set_textbox_focus(self):
		if TextBox_Window.active_window == "Textbox2":
			self.textbox2.setFocus()
		else:
			self.textbox.setFocus()

	#Set the bottom label text, reset after 5 seconds
	def update_bottom_label(self, bottomtext):
		if TextBox_Window.active_window == "Textbox2":
			self.main_text_label2.setText(bottomtext)
		else:
			self.main_text_label.setText(bottomtext)
		t = threading.Timer(5.0, self.remove_bottom_label)
		t.start()
		
	def remove_bottom_label(self):
		if not TextBox_Window.dir_browser_open and self.main_text_label.text() != "Buffer 1 has unsaved changes. Exit anyway? (Yes/No):" \
		and self.main_text_label2.text() != "Buffer 2 has unsaved changes. Exit anyway? (yes/no):" :
			self.main_text_label.setText("")
			self.main_text_label2.setText("")
			
	#Apply syntax highlighting only if the file is a source file.
	def apply_syntax_highlight(self, theme):
		TextBox_Window.syntax_theme = theme
							
		TextBox_Window.highlighter2 = syntax.BoostSourceHighlighter(self.textbox2.document(), \
		 TextBox_Window.file_name_2, self.preference_value, theme)

		TextBox_Window.highlighter = syntax.BoostSourceHighlighter(self.textbox.document(), \
		 TextBox_Window.file_name, self.preference_value, theme)
					
		QtCore.QTimer.singleShot(5, self.set_file_not_modified)
		self.close_dialog_button_box()
		self.set_textbox_focus()
					
	def highlight_current_line(self):
		if TextBox_Window.active_window == "Textbox2":
			self.extraSelections = []
			self.lineColor = QColor("#0e1112")
			self.selection = QTextEdit.ExtraSelection()
			self.selection.format.setBackground(self.lineColor)
			self.selection.format.setProperty(QTextFormat.FullWidthSelection, QVariant(True))
			self.selection.cursor = self.textbox2.textCursor()
			self.selection.cursor.clearSelection()
			self.extraSelections.append(self.selection)

			self.textbox2.setExtraSelections(self.extraSelections)
		elif TextBox_Window.active_window == "Textbox":
			self.extraSelections = []
			self.lineColor = QColor("#0e1112")
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
			self.query.setFixedHeight(self.bar_font_metrics.height() + 6)
			self.query.setFont(TextBox_Window.bar_font)
			TextBox_Window.search_text = QtGui.QLabel("Search:", parent = self.main_text_label)
			self.search_text.setFixedHeight(self.bar_font_metrics.height() + 6)
			self.search_text.setFont(TextBox_Window.bar_font)
			self.search_text.setStyleSheet("""
								background-color: #181c1f; color: #1fad83; padding-top: 2px; border: 0px solid black; font-size: 14px;
							""")
							
			if TextBox_Window.active_window == "Textbox2":
				self.browser_layout2.addWidget(self.search_text)
				self.browser_layout2.addWidget(self.query)
				self.main_text_label2.setParent(None)
			else:
				self.browser_layout.addWidget(self.search_text)
				self.browser_layout.addWidget(self.query)
				self.main_text_label.setParent(None)
		
		TextBox_Window.search_displayed = True
	
		self.query.setFocus()
		#TODO(cody): Implement emacs-esque search function that only finds the first result on keypress. 
#		self.query.textChanged.connect(self.search_in_file)
		self.query.returnPressed.connect(self.search_in_file)
	
	def remove_search_box(self):
		TextBox_Window.search_text.setParent(None)
		TextBox_Window.query.setParent(None)
		TextBox_Window.search_displayed = False
		
		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.textbox2.setFocus()
		else:
			TextBox_Window.textbox.setFocus()

		self.browser_layout_widget.setFixedHeight(self.bar_font_metrics.height() + 4)
		self.browser_layout_widget2.setFixedHeight(self.bar_font_metrics.height() + 4)
		self.dir_browser_search.setParent(None)
		self.query_string.setParent(None)
		
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
			self.textbox2.setCenterOnScroll(True)
		else:
			self.text = self.textbox.toPlainText()
			self.textbox.setCenterOnScroll(True)
					
		query = str(self.query.text())
		flags = re.I
		pattern = re.compile(query, flags)
		start = self.last_match.start() + 1 if self.last_match else 0
	
		self.last_match = pattern.search(self.text, start)
		if self.last_match:
			start = self.last_match.start()
			end = self.last_match.end()
			self.query.setStyleSheet("""
								.SearchLineEdit { background-color: #181c1f; color: #e8e4cf; border: 0px solid black; }
								""")
			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setStyleSheet("""
				   			BoostPlainTextEdit { background-color: #181c1f; selection-color: black; selection-background-color: #FA8072; color: #42cc3f; }
							BoostPlainTextEdit[readOnly=true] { color: #cc3f3f; }
							.QScrollBar { height: 0px; width: 0px; }
							""")
			else:
				self.textbox.setStyleSheet("""
				   			BoostPlainTextEdit { background-color: #181c1f; selection-color: black; selection-background-color: #FA8072; color: #42cc3f; }
							BoostPlainTextEdit[readOnly=true] { color: #cc3f3f; }
							.QScrollBar { height: 0px; width: 0px; }
							""")				
		else:
			end = 0
			self.query.setStyleSheet("""
								.SearchLineEdit { background-color: #d73737; color: #23292c; border: 0px solid black; }
								""")
	
		self.move_cursor(start, end)
	
		if TextBox_Window.active_window == "Textbox2":
			self.textbox2.setCenterOnScroll(False)
		else:
			self.textbox.setCenterOnScroll(False)
			
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

	#Custom directory browser, text-based for speed
	def open_dir_browser(self):
		if not TextBox_Window.dir_browser_open:
			self.temp_dir = os.getcwd()
		TextBox_Window.dir_browser_open = True
		TextBox_Window.current_dir_list = []
		
		self.browser_layout_widget.setFixedHeight(self.bar_font_metrics.height() + 4)
		self.dir_browser_search.setFixedHeight(self.bar_font_metrics.height() + 4)
				
		#Display the browser directory and remove the bottom label
		self.main_text_label.setProperty("is_active", True)

		self.current_dir = os.chdir(os.getcwd())
		self.len_of_path = os.getcwd().split(os.sep)
				
		if len(self.len_of_path) >= 3:
			self.current_dir_separated = "Open file: ~" + os.sep.join(os.getcwd().split(os.sep)[(len(self.len_of_path) / 2) + 1:])
		else:
			self.current_dir_separated = "Open file: ~" + os.sep.join(os.getcwd().split(os.sep)[:])

	   	self.main_text_label.setText(str(self.current_dir_separated))
		
		for f in os.listdir("."):
			path = os.path.join(os.getcwd(), f)
			
			#Foreach directory, append it to list of working directory
			if os.path.isdir(path):
				if platform.system() == "Windows":
					TextBox_Window.current_dir_list.append(f + "\\")
				else:
					TextBox_Window.current_dir_list.append(f + "/")
			#Foreach file, append it to list of working directory
			else:
				TextBox_Window.current_dir_list.append(f)
				self.file_path = str(os.path.join(os.getcwd(), TextBox_Window.current_dir_list[0]))
								
		self.query_string.setFixedWidth(self.bar_font_metrics.width(str(self.query_string.text())) \
		 + (self.bar_font_metrics.width(" ") / 2))

		TextBox_Window.current_dir_list[0] = TextBox_Window.current_dir_list[0].replace(TextBox_Window.current_dir_list[0], \
		 "{" + TextBox_Window.current_dir_list[0] + "}")
		self.dir_string = '[%s]' % ' | '.join(map(str, TextBox_Window.current_dir_list))
		self.dir_browser_search.setText(self.dir_string)
		self.dir_browser_search.setStyleSheet("""
									font-family: Noto Mono; background-color: #181c1f; color: #e8e4cf; border: 0px solid black; text-align: left; padding-top: 0px;
									""")
									
		self.dir_browser_search.setMinimumHeight(self.dir_browser_search.document().size().height())	
									
		self.browser_layout_widget.setFixedHeight(self.dir_browser_search.frameGeometry().height())
		self.dir_browser_search.setFixedHeight(self.dir_browser_search.frameGeometry().height())
						
		self.file_label.setParent(None)
		self.file_modified_label.setParent(None)
		self.filemode_label.setParent(None)
		self.editmode_label.setParent(None)
		self.line_label.setParent(None)
			
		self.browser_layout.addWidget(self.query_string)
		self.browser_layout.addWidget(self.dir_browser_search)
		self.dir_browser_search.setMinimumHeight(self.dir_browser_search.frameGeometry().height())
		self.dir_browser_search.setFont(TextBox_Window.bar_font)
		self.dir_browser_search.setReadOnly(True)
		
		self.update_dir_browser()
		self.query_string.setFocus()
		
	#Update contents of files in current dir
	def update_dir_browser(self):
		self.query_string.setFixedWidth(self.bar_font_metrics.width(str(self.query_string.text())) \
	     + (self.bar_font_metrics.width(" ") / 2))
		self.browser_layout_widget.setFixedHeight(self.bar_font_metrics.height() + 4)
		self.browser_layout_widget2.setFixedHeight(self.bar_font_metrics.height() + 4)
		self.dir_browser_search.setFixedHeight(self.bar_font_metrics.height() + 4)

		TextBox_Window.temp_current_dir_list = []

		for item in self.current_dir_list:
			if str(self.query_string.text()) in str(item).lower():
				self.temp_current_dir_list.append(item)
				
		if len(self.temp_current_dir_list) > 0 and len(TextBox_Window.current_dir_list) > 0 and \
		 self.temp_current_dir_list[0] != TextBox_Window.current_dir_list[0]:
			if len(self.temp_current_dir_list) > 1:
				self.temp_current_dir_list[0] = self.temp_current_dir_list[0].replace(self.temp_current_dir_list[0], \
				 "{" + self.temp_current_dir_list[0] + "}")
		self.dir_string = '[%s]' % ' | '.join(map(str, self.temp_current_dir_list))

		if self.query_string.text() == "..":
			self.dir_string = "[Previous directory]"

		self.dir_browser_search.setText(self.dir_string)
		self.dir_browser_search.setMinimumHeight(self.dir_browser_search.document().size().height())		
		
		if self.dir_browser_search.frameGeometry().height() > self.bar_font_metrics.height() + 4:
			self.browser_layout_widget.setFixedHeight(self.dir_browser_search.frameGeometry().height())
			self.browser_layout_widget2.setFixedHeight(self.dir_browser_search.frameGeometry().height())
			self.browser_layout_widget2.setMinimumHeight(self.bar_font_metrics.height() + 4)
#			self.browser_layout_widget2.setMaximumHeight(self.bar_font_metrics.height() + 4)
			self.dir_browser_search.setFixedHeight(self.dir_browser_search.frameGeometry().height())
			self.browser_layout.setAlignment(self.main_text_label, Qt.AlignTop)
			self.browser_layout.setAlignment(self.query_string, Qt.AlignTop)
			self.browser_layout.setAlignment(self.dir_browser_search, Qt.AlignTop)
			self.browser_layout2.setAlignment(Qt.AlignTop)
		else:
			self.browser_layout_widget.setFixedHeight(self.bar_font_metrics.height() + 4)
			self.browser_layout_widget2.setMinimumHeight(self.bar_font_metrics.height() + 4)
			self.browser_layout_widget2.setMaximumHeight(self.bar_font_metrics.height() + 4)
			self.dir_browser_search.setFixedHeight(self.bar_font_metrics.height() + 4)									
			self.browser_layout.setAlignment(self.main_text_label, Qt.AlignTop)
			self.browser_layout.setAlignment(self.query_string, Qt.AlignTop)
			self.browser_layout.setAlignment(self.dir_browser_search, Qt.AlignTop)
			self.browser_layout2.setAlignment(Qt.AlignTop)
		
		self.query_string.setFocus()

	#Dir_browser returnPressed results
	def do_query(self):
		if self.query_string.text() == "..":
			self.dir_string = "[Previous directory]"
			self.open_previous_dir()
		elif str(self.query_string.text()) != ".." and self.dir_string != "[Previous directory]":
			try:
				self.file_path = str(os.path.join(os.getcwd(), self.temp_current_dir_list[0].replace("{", "")))
				self.file_path = self.file_path.replace("}", "")
				if os.path.isfile(self.file_path):
					self.file_open(self.file_path)
				elif os.path.isdir(self.file_path):
					self.open_dir(self.file_path)
			except:
				pass
				
		self.query_string.setText("")
		
	#Without opening file
	def close_dir_browser(self):
		if TextBox_Window.dir_browser_open == True:
			os.chdir(self.temp_dir)
			self.browser_layout.addWidget(self.file_modified_label)
			self.browser_layout.addWidget(self.file_label)
			self.browser_layout.addWidget(self.filemode_label)
			self.browser_layout.addWidget(self.editmode_label)
			self.browser_layout.addWidget(self.line_label)
	
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width(), 0, 0, 0)
	
			self.set_textbox_focus()
	
			self.main_text_label.setText("")
			self.dir_browser_search.setText("")
			self.query_string.setText("")
			self.query_string.setParent(None)
			self.dir_browser_search.setParent(None)
			TextBox_Window.dir_browser_open = False
			TextBox_Window.new_file_displayed = False
	
		if BoostPlainTextEdit.is_window_split:
			TextBox_Window.browser_layout_widget.setFixedWidth(TextBox_Window.outer_widget_1.width() + 1)
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width() + 2, 0, 0, 0)
		else:
			TextBox_Window.browser_layout_widget.setFixedWidth(TextBox_Window.outer_widget_1.width() + 1)
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width() + 2, 0, 0, 0)
		
		self.browser_layout_widget.setFixedHeight(self.bar_font_metrics.height() + 4)
		self.browser_layout_widget2.setFixedHeight(self.bar_font_metrics.height() + 4)
		
	#Open the next directory of the dir browser
	def open_dir(self, directory):
		TextBox_Window.dir_browser_open = True
		os.chdir(os.path.join(os.getcwd(), directory))
		self.open_dir_browser()
		self.query_string.setText("")
		self.update_dir_browser()
	
	#Open the previous directory of the dir_browser
	def open_previous_dir(self):
		TextBox_Window.dir_browser_open = True
		if str(self.query_string.text()) == "..":
			self.change_to_previous_dir = os.chdir("..")
			self.open_dir_browser()
			self.query_string.setText("")
			self.update_dir_browser()
			
	#For closing preferences and stuff
	def close_dialog_button_box(self):
		if TextBox_Window.preferences_displayed:
			os.chdir(self.temp_dir)
			self.browser_layout.addWidget(self.file_modified_label)
			self.browser_layout.addWidget(self.file_label)
			self.browser_layout.addWidget(self.filemode_label)
			self.browser_layout.addWidget(self.editmode_label)
			self.browser_layout.addWidget(self.line_label)
   
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width(), 0, 0, 0)
   
			self.set_textbox_focus()
   
		if BoostPlainTextEdit.is_window_split:
			TextBox_Window.browser_layout_widget.setFixedWidth(TextBox_Window.outer_widget_1.width() + 1)
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width() + 2, 0, 0, 0)
		else:
			TextBox_Window.browser_layout_widget.setFixedWidth(TextBox_Window.outer_widget_1.width() + 1)
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width() + 2, 0, 0, 0)
		
		self.reset_browser_bar()
		self.stacked_layout.setCurrentIndex(0)
		TextBox_Window.preferences_displayed = False

	def update_file_modified(self):
		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.file_2_is_modified = True
			TextBox_Window.file_modified_label2.setText("~")
			TextBox_Window.file_modified_label2.setFixedWidth(self.bar_font_metrics.width(" ") + 10)
			TextBox_Window.file_modified_label2.setToolTip("This buffer has been modified.")
		else:
			TextBox_Window.file_1_is_modified = True
			TextBox_Window.file_modified_label.setText("~")
			TextBox_Window.file_modified_label.setFixedWidth(self.bar_font_metrics.width(" ") + 10)
			TextBox_Window.file_modified_label.setToolTip("This buffer has been modified.")
			
	def set_file_not_modified(self):
		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.file_2_is_modified = False
			TextBox_Window.file_modified_label2.setText("")
			TextBox_Window.file_modified_label2.setFixedWidth(0)
		else:
			TextBox_Window.file_1_is_modified = False
			TextBox_Window.file_modified_label.setText("")
			TextBox_Window.file_modified_label.setFixedWidth(0)
			
	def open_preference_menu(self):
		#Display the browser directory and remove the bottom label
		self.main_text_label.setProperty("is_active", True)
		
		self.dialog_button_box = QDialogButtonBox(Qt.Vertical)
		self.stacked_layout.addWidget(self.dialog_button_box)
		self.stacked_layout.setAlignment(Qt.AlignLeft)
		self.scroll_area.setWidget(self.dialog_button_box)		
		
		for widget in self.dialog_button_box.children():
			if isinstance(widget, QPushButton):
				widget.deleteLater()
				widget = None
		self.dialog_button_box.clear()
		
	   	self.main_text_label.setText("Preferences")
	
		#Previous directory button
  		self.syntax_color_button = QPushButton("Syntax Color")
		self.syntax_color_button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
		self.syntax_color_button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #181c1f; color: #DBD9D5; text-align: left; padding: 5px; font-family: Noto Mono; font-size: 14px; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
			   						.QPushButton:hover { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
	   	   						""")
		
		self.syntax_color_button.setAutoDefault(True)
		self.syntax_color_button.pressed.connect(self.open_syntax_colors)
		self.dialog_button_box.addButton(self.syntax_color_button, QDialogButtonBox.ActionRole)

  		self.font_size_button = QPushButton("Font Size")
		self.font_size_button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
		self.font_size_button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #181c1f; color: #DBD9D5; text-align: left; padding: 5px; font-family: Noto Mono; font-size: 14px; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
			   						.QPushButton:hover { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
	   	   						""")
		
		self.font_size_button.setAutoDefault(True)
		self.font_size_button.pressed.connect(self.open_font_sizes)
		self.dialog_button_box.addButton(self.font_size_button, QDialogButtonBox.ActionRole)

		self.stacked_layout.setCurrentIndex(1)
	
		self.file_label.setParent(None)
		self.file_modified_label.setParent(None)
		self.filemode_label.setParent(None)
		self.editmode_label.setParent(None)
		self.line_label.setParent(None)
		
		TextBox_Window.preferences_displayed = True
		
	def open_syntax_colors(self):
		for widget in self.dialog_button_box.children():
			if isinstance(widget, QPushButton):
				widget.deleteLater()
				widget = None
		self.dialog_button_box.clear()
		
	   	self.main_text_label.setText("Choose syntax color theme")
	
		#Previous directory button
  		self.syntax_color_button = QPushButton("Syntax Color")
		self.syntax_color_button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
		self.syntax_color_button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #181c1f; color: #DBD9D5; text-align: left; padding: 5px; font-family: Noto Mono; font-size: 14px; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
			   						.QPushButton:hover { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
	   	   						""")
		
		for color in TextBox_Window.color_themes:
			self.button = QPushButton(str(color))
			self.button.setObjectName(str(color))
			self.button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
	   	   	self.button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #181c1f; color: #DBD9D5; text-align: left; padding: 5px; font-family: Noto Mono; font-size: 14px; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
			   						.QPushButton:hover { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
	   	   						""")
			self.button.setAutoDefault(True)
			self.button.pressed.connect(partial(self.set_preference, color))
		   	self.dialog_button_box.addButton(self.button, QDialogButtonBox.ActionRole)

	def open_font_sizes(self):			
		for widget in self.dialog_button_box.children():
			if isinstance(widget, QPushButton):
				widget.deleteLater()
				widget = None
		self.dialog_button_box.clear()
		
	   	self.main_text_label.setText("Select font size")
	
  		self.font_size_button = QPushButton("Font Size")
		self.font_size_button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
		self.font_size_button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #181c1f; color: #DBD9D5; text-align: left; padding: 5px; font-family: Noto Mono; font-size: 14px; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
			   						.QPushButton:hover { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
	   	   						""")
		
		for size in TextBox_Window.font_sizes:
			self.button = QPushButton(str(size))
			self.button.setObjectName(str(size))
			self.button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
	   	   	self.button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #181c1f; color: #DBD9D5; text-align: left; padding: 5px; font-family: Noto Mono; font-size: 14px; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
			   						.QPushButton:hover { outline: 0px; border: 2px solid #2273A5; padding: 3px; }
	   	   						""")
			self.button.setAutoDefault(True)
			self.button.pressed.connect(partial(self.set_preference, size))
		   	self.dialog_button_box.addButton(self.button, QDialogButtonBox.ActionRole)

		
class BoostPlainTextEdit(QtGui.QPlainTextEdit, TextBox_Window):

	is_window_split = False
	
	def __init__(self, parent = None):
		super(BoostPlainTextEdit, self).__init__(parent)

		self.editor = QPlainTextEdit()
		self.setMinimumSize(10, 10)
		self.setLineWrapMode(0)
		self.setReadOnly(False)

   		self.setFrameStyle(QFrame.NoFrame)
		self.ensureCursorVisible()
				
		self.setFont(TextBox_Window.font)
			
		self.setContextMenuPolicy(Qt.PreventContextMenu)
		self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		
		try:
			if str(sys.argv[1]) == "forest":
				self.setStyleSheet("""
				   			BoostPlainTextEdit { background-color: #222B1E; selection-color: #BFBFBF; selection-background-color: #0C0075; color: lightgreen; }
							BoostPlainTextEdit[readOnly=true] { color: #cc3f3f; }
							.QScrollBar { height: 0px; width: 0px; }
		   	    		""")
				self.fmt = QTextCharFormat()
				self.fmt.setForeground(QBrush(QColor("#BBC1A8")))
				self.mergeCurrentCharFormat(self.fmt)
			elif str(sys.argv[1]) == "spacex":
				self.setStyleSheet("""
				   			BoostPlainTextEdit { background-color: #192433; selection-color: #BFBFBF; selection-background-color: #0C0075; color: lightgreen; }
							BoostPlainTextEdit[readOnly=true] { color: #cc3f3f; }
							.QScrollBar { height: 0px; width: 0px; }
		   	    		""")
				self.fmt = QTextCharFormat()
				self.fmt.setForeground(QBrush(QColor("#878787")))
				self.mergeCurrentCharFormat(self.fmt)
			elif str(sys.argv[1]) == "alabaster":
				self.setStyleSheet("""
				   			BoostPlainTextEdit { background-color: #EDEAE0; selection-color: #BFBFBF; selection-background-color: #0C0075; color: #378437; }
							BoostPlainTextEdit[readOnly=true] { color: #cc3f3f; }
							.QScrollBar { height: 0px; width: 0px; }
		   	    		""")
				self.fmt = QTextCharFormat()
				self.fmt.setForeground(QBrush(QColor("black")))
				self.mergeCurrentCharFormat(self.fmt)
			else:
				self.setStyleSheet("""
				   			BoostPlainTextEdit { background-color: #181c1f; selection-color: white; selection-background-color: #162730; color: #42cc3f; }
							BoostPlainTextEdit[readOnly=true] { color: #cc3f3f; }
							.QScrollBar { height: 0px; width: 0px; }
			       		""")
				self.fmt = QTextCharFormat()
				self.fmt.setForeground(QBrush(QColor("#d1d1d1")))
				self.mergeCurrentCharFormat(self.fmt)

		except:
			self.setStyleSheet("""
			   			BoostPlainTextEdit { background-color: #181c1f; selection-color: white; selection-background-color: #162730; color: #42cc3f; }
						BoostPlainTextEdit[readOnly=true] { color: #cc3f3f; }
						.QScrollBar { height: 0px; width: 0px; }
			      		""")
			self.fmt = QTextCharFormat()
			self.fmt.setForeground(QBrush(QColor("#d1d1d1")))
			self.mergeCurrentCharFormat(self.fmt)
												
		#Set default tab width to 4 spaces
		TextBox_Window.font_metrics = QFontMetrics(TextBox_Window.font)
		self.setTabStopWidth(4 * self.font_metrics.width(' '))
		
		TextBox_Window.bar_font_metrics = QFontMetrics(TextBox_Window.bar_font)

		self.last_match = None
				
	#Handle custom keyevents that occur in the editor	
	def keyPressEvent(self, event):
   		k = event.key()
		m = int(event.modifiers())
		modifiers = QtGui.QApplication.keyboardModifiers()
						
		#Split window
		if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+X'):
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
			if BoostPlainTextEdit.is_window_split:
				if self.textbox.hasFocus():
					self.textbox2.setFocus()
				elif self.textbox2.hasFocus():
					self.textbox.setFocus()
				
		if k == QtCore.Qt.Key_Return:		
			QtCore.QTimer.singleShot(10, self.auto_indent)
		elif k == QtCore.Qt.Key_Tab:
			self.indent_selected_text()
			
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
							
	def focusInEvent(self, event):
		TextBox_Window.active_window = self.objectName()
		super(BoostPlainTextEdit, self).focusInEvent(event)

		#Reset color scheme after search_in_file changes highlight color
		if TextBox_Window.active_window == "Textbox2":
			self.textbox2.setStyleSheet("""
			   			BoostPlainTextEdit { background-color: #181c1f; selection-color: white; selection-background-color: #162730; color: #42cc3f; }
						BoostPlainTextEdit[readOnly=true] { color: #cc3f3f; }
						.QScrollBar { height: 0px; width: 0px; }
			      		""")
		else:
			self.textbox.setStyleSheet("""
			   			BoostPlainTextEdit { background-color: #181c1f; selection-color: white; selection-background-color: #162730; color: #42cc3f; }
						BoostPlainTextEdit[readOnly=true] { color: #cc3f3f; }
						.QScrollBar { height: 0px; width: 0px; }
			      		""")
		
		self.set_active_browser_bar()
		self.reset_browser_bar()
					
	def focusOutEvent(self, event):
		TextBox_Window.active_window = self.objectName()	
		super(BoostPlainTextEdit, self).focusOutEvent(event)
		
		self.set_inactive_browser_bar()
		QApplication.restoreOverrideCursor()
		
#	def paintEvent(self, event):
#		qp = QtGui.QPainter(self.viewport())
#		qp.setViewport(self.viewport())
#		qp.drawText((self.font_metrics.width(" ") * 2) * self.textbox.textCursor().positionInBlock(), (self.font_metrics.xHeight() * 2) * self.textbox.textCursor().blockNumber(), "Hello")
#		QPlainTextEdit.paintEvent(self, event)
       													
	def set_active_browser_bar(self):
		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.main_file_path = TextBox_Window.file_path_2

			for widget in TextBox_Window.browser_layout_widget2.children():
				if isinstance(widget, BrowserBarLabel) or isinstance(widget, QLabel):
					widget.setProperty("is_active", True)
					widget.setStyle(widget.style())
					if widget.objectName() == "FileModifiedLabel2":
						try:
							if str(sys.argv[1]) == "forest":
								widget.setStyleSheet("""
													background-color: #BBC1A8; color: #800000; padding-top: 3px; margin: 0; height: 12px;
												""")
							elif str(sys.argv[1]) == "spacex":
								widget.setStyleSheet("""
													background-color: #878787; color: #800000; padding-top: 3px; margin: 0; height: 12px;
												""")
							else:
								widget.setStyleSheet("""
													background-color: #2E3B44; color: red; padding-top: 3px; margin: 0; height: 12px;
												""")
						except:
							widget.setStyleSheet("""
												background-color: #2E3B44; color: red; padding-top: 3px; margin: 0; height: 12px;
											""")
		else:
			TextBox_Window.main_file_path = TextBox_Window.file_path
			
			for widget in TextBox_Window.browser_layout_widget.children():
				if isinstance(widget, BrowserBarLabel):
					widget.setProperty("is_active", True)
					widget.setStyle(widget.style())
					if widget.objectName() == "FileModifiedLabel":
						try:
							if str(sys.argv[1]) == "forest":							
								widget.setStyleSheet("""
													background-color: #BBC1A8; color: #800000; padding-top: 3px; margin: 0; height: 12px; 
												""")
							else:
								widget.setStyleSheet("""
													background-color: #2E3B44; color: red; padding-top: 3px; margin: 0; height: 12px;
												""")
						except:
							widget.setStyleSheet("""
												background-color: #2E3B44; color: red; padding-top: 3px; margin: 0; height: 12px;
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
							try:
								if str(sys.argv[1]) == "forest":
									widget.setStyleSheet("""
													background-color: #878787; color: brown; padding-top: 3px; margin: 0; height: 12px;
												""")
								else:
									widget.setStyleSheet("""
													background-color: #2E3B44; color: red; padding-top: 3px; margin: 0; height: 12px;
												""")
							except:
								widget.setStyleSheet("""
												background-color: #2E3B44; color: red; padding-top: 3px; margin: 0; height: 12px;
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
							try:
								if str(sys.argv[1]) == "forest":
									widget.setStyleSheet("""
													background-color: #878787; color: brown; padding-top: 3px; margin: 0; height: 12px;
												""")
								else:
									widget.setStyleSheet("""
													background-color: #2E3B44; color: red; padding-top: 3px; margin: 0; height: 12px;
												""")

							except:
								widget.setStyleSheet("""
												background-color: #2E3B44; color: red; padding-top: 3px; margin: 0; height: 12px;
											""")
											
	def resizeEvent(self, event):
		if BoostPlainTextEdit.is_window_split:
			TextBox_Window.browser_layout_widget.setFixedWidth(TextBox_Window.outer_widget_1.width() + 1)
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width() + 2, 0, 0, 0)
		else:
			TextBox_Window.browser_layout_widget.setFixedWidth(TextBox_Window.outer_widget_1.width() + 1)
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width() + 2, 0, 0, 0)			
					
	#Split the window to enable editing two files
	def split_buffer(self):
		if not TextBox_Window.has_been_split:
			self.grid_layout.addWidget(self.browser_layout_widget2, 0, 0)
			self.container_widget = QScrollArea()
			self.container_widget.setStyleSheet("""
								QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
								QScrollArea { background-color: transparent; border: 0px solid black; }
								QWidget { background-color: transparent; }
							""")
			try:
				if str(sys.argv[1]) == "forest":
					self.line_label.setStyleSheet("""
										BrowserBarLabel { background-color: #878787; color: black; padding-top: 3px; margin: 0; height: 12px; }
										BrowserBarLabel[is_active=true] { background-color: #BBC1A8; color: black; padding-top: 3px; margin: 0; height: 12px;  }
									""")
					self.line_label2.setStyleSheet("""
										BrowserBarLabel { background-color: #878787; color: black; padding-top: 3px; margin: 0; height: 12px; border-right: 0px solid black; }
										BrowserBarLabel[is_active=true] { background-color: #BBC1A8; color: black; padding-top: 3px; margin: 0; height: 12px; border-right: 0px solid black; }
									""")
				else:
					self.line_label.setStyleSheet("""
										BrowserBarLabel { background-color: #DBD9D5; color: #878787; padding-top: 3px; margin: 0; height: 12px;  }
										BrowserBarLabel[is_active=true] { background-color: #2E3B44; color: black; padding-top: 3px; margin: 0; height: 12px; }
									""")
					self.line_label2.setStyleSheet("""
										BrowserBarLabel { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; border-right: 0px solid black; }
										BrowserBarLabel[is_active=true] { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; border-right: 0px solid black; }
									""")
	
			except:
				self.line_label.setStyleSheet("""
									BrowserBarLabel { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; ; }
									BrowserBarLabel[is_active=true] { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; }
								""")
				self.line_label2.setStyleSheet("""
									BrowserBarLabel { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; }
									BrowserBarLabel[is_active=true] { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; }
								""")
	
			self.splitter.addWidget(self.outer_widget_2)
			BoostPlainTextEdit.stacked_layout2 = QtGui.QStackedLayout(self.outer_widget_2)
			self.stacked_layout2.setMargin(0)
			self.stacked_layout2.setSpacing(0)
			
			self.stacked_layout2.addWidget(self.textbox2)
			self.textbox2.setPlainText("This is an empty buffer.\nFor notes or text you don't want to save, write them here.")
			self.textbox2.setFocus()
		
			TextBox_Window.has_been_split = True
			
		if BoostPlainTextEdit.is_window_split:
			if TextBox_Window.active_window == "Textbox2":
				self.outer_widget_1.setVisible(False)
				self.textbox2.setFocus()
				BoostPlainTextEdit.is_window_split = False
			elif TextBox_Window.active_window == "Textbox":
				self.outer_widget_2.setVisible(False)
				self.textbox.setFocus()
				BoostPlainTextEdit.is_window_split = False

			TextBox_Window.browser_layout_widget.setFixedWidth(TextBox_Window.outer_widget_1.width() + 1)
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width() + 2, 0, 0, 0)
			
		elif not BoostPlainTextEdit.is_window_split:
			if TextBox_Window.active_window == "Textbox2":
				self.outer_widget_1.setVisible(True)
				self.textbox2.setFocus()
				BoostPlainTextEdit.is_window_split = True
			elif TextBox_Window.active_window == "Textbox":
				self.outer_widget_2.setVisible(True)
				self.textbox.setFocus()
				BoostPlainTextEdit.is_window_split = True
														
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
			if line_text[line_length - 1] == ":":
				tab_array.append(tab)
				tab_string = "".join(tab_array)
				self.cursor.insertText(tab_string)
			elif line_text[line_length - 1] == "{":
				tab_array.append(tab)
				tab_string = "".join(tab_array)
				self.cursor.insertText(tab_string)
				
				try:
					tab_array.pop(1)
				except:
					tab_array = []
				tab_string = "".join(tab_array)
				self.cursor.insertText('\n')
				self.cursor.insertText(tab_string + '}')
				
				self.cursor.movePosition(self.cursor.Up, self.cursor.MoveAnchor, 1)
				self.cursor.movePosition(self.cursor.EndOfLine, self.cursor.MoveAnchor, 1)
				self.setTextCursor(self.cursor)
			else:
				tab_string = "".join(tab_array)
				self.cursor.insertText(tab_string)
								
		if TextBox_Window.active_window == "Textbox2":
			self.next_block = self.textbox2.document().findBlockByLineNumber(self.line)	
			TextBox_Window.highlighter2.rehighlightBlock(self.next_block)
		else:
			self.next_block = self.textbox.document().findBlockByLineNumber(self.line)	
			TextBox_Window.highlighter.rehighlightBlock(self.next_block)
		
	#Indent selected text if user pressed TAB while multiple lines are selected.
	def indent_selected_text(self):
		if TextBox_Window.active_window == "Textbox2":
			self.cursor = self.textbox2.textCursor()
		else:
			self.cursor = self.textbox.textCursor()
			
		self.selected_text = unicode(self.cursor.selectedText())
		special = u"\u2029"

		for line in self.selected_text.splitlines():
			if special in self.selected_text:
				if platform.system() == "Windows":
					self.cursor.insertText('\t' + line + '\r\n')
				else:
					self.cursor.insertText('\t' + line + '\n')
					
		if special in self.selected_text:
			QtCore.QTimer.singleShot(1, self.cursor.deletePreviousChar)

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
		self.document_text = self.document()
		self.block = self.document_text.findBlockByLineNumber(self.line - 1)

		self.cursor.movePosition(self.cursor.EndOfLine, self.cursor.MoveAnchor, len(str(self.block.text())))
		self.setTextCursor(self.cursor)
		
	#Move cursor to start of line
	def highlight_to_end_of_line(self):
		self.cursor = self.textCursor()
		self.line = self.cursor.blockNumber() + 1
		self.document_text = self.document()
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
							SearchLineEdit { font-family: Noto Mono; background-color: #181c1f; color: #e8e4cf; border: 0px solid black; text-align: left; padding-top: 0px; }
						""")
		
   	def focusOutEvent(self, event):
		if self.objectName() != "Browser Search" and self.objectName() != "File Query":
			self.setParent(None)
		
		if TextBox_Window.search_displayed == True:
			TextBox_Window.search_displayed = False
			TextBox_Window.search_text.setParent(None)
		elif TextBox_Window.new_file_displayed == True:
			TextBox_Window.new_file_displayed = False
			self.remove_new_file_box()
		elif TextBox_Window.preferences_displayed == True:
			TextBox_Window.preferences_displayed = False
			TextBox_Window.get_preference.setParent(None)
		
		self.set_textbox_focus()
		
	def keyPressEvent(self, event):
		k = event.key()
		
		if k == QtCore.Qt.Key_Right:
			TextBox_Window.temp_current_dir_list[0] = TextBox_Window.temp_current_dir_list[0].replace("{", "")
			TextBox_Window.temp_current_dir_list[0] = TextBox_Window.temp_current_dir_list[0].replace("}", "")
			TextBox_Window.temp_current_dir_list = TextBox_Window.temp_current_dir_list[1:] + TextBox_Window.temp_current_dir_list[:1]

		if k == QtCore.Qt.Key_Left:
			TextBox_Window.temp_current_dir_list[0] = TextBox_Window.temp_current_dir_list[0].replace("{", "")
			TextBox_Window.temp_current_dir_list[0] = TextBox_Window.temp_current_dir_list[0].replace("}", "")
			TextBox_Window.temp_current_dir_list = TextBox_Window.temp_current_dir_list[-1:] + TextBox_Window.temp_current_dir_list[:-1]

		if len(TextBox_Window.temp_current_dir_list) > 0 and len(TextBox_Window.current_dir_list) > 0 and \
		 TextBox_Window.temp_current_dir_list[0] != TextBox_Window.current_dir_list[0]:
			if len(TextBox_Window.temp_current_dir_list) > 1:
				TextBox_Window.temp_current_dir_list[0] = TextBox_Window.temp_current_dir_list[0].replace(TextBox_Window.temp_current_dir_list[0], \
				 "{" + TextBox_Window.temp_current_dir_list[0] + "}")

		TextBox_Window.dir_string = '[%s]' % ' | '.join(map(str, TextBox_Window.temp_current_dir_list))
		TextBox_Window.dir_browser_search.setText(TextBox_Window.dir_string)
				
		#Handle any other event normally 
		QtGui.QLineEdit.keyPressEvent(self, event)
			
#Custom QLabel for top bar
class BrowserBarLabel(QtGui.QLabel, TextBox_Window):

	def __init__(self, parent = None):
		super(BrowserBarLabel, self).__init__(parent)
		
		self.browser_label = QLabel()
		self.setFixedHeight(self.bar_font_metrics.height() + 4)
		self.setFont(TextBox_Window.bar_font)
		self.setAlignment(QtCore.Qt.AlignRight)

		try:
			if str(sys.argv[1]) == "forest":
				self.setStyleSheet("""
					BrowserBarLabel { background-color: #878787; color: black; padding-top: 3px; margin: 0; height: 12px; font-size: 14px; border-right: 3px solid #222B1E; }
					BrowserBarLabel[is_active=true] { background-color: #BBC1A8; color: black; padding-top: 3px; margin: 0; height: 12px; font-size: 14px; border-right: 3px solid #222B1E; }
					""")
			elif str(sys.argv[1]) == "spacex":
				self.setStyleSheet("""
					BrowserBarLabel { background-color: #878787; color: black; padding-top: 3px; margin: 0; height: 12px; font-size: 14px; border-right: 3px solid #192433; }
					BrowserBarLabel[is_active=true] { background-color: #878787; color: black; padding-top: 3px; margin: 0; height: 12px; font-size: 14px; border-right: 3px solid #192433; }
					""")
			else:
				self.setStyleSheet("""
					BrowserBarLabel { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; border-right: 2px solid #181c1f; }
					BrowserBarLabel[is_active=true] { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; border-right: 2px solid #181c1f;}
					""")
		except:
			self.setStyleSheet("""
				BrowserBarLabel { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; border-right: 2px solid #181c1f; }
				BrowserBarLabel[is_active=true] { background-color: #2E3B44; color: #DBD9D5; padding-top: 3px; margin: 0; height: 12px; border-right: 2px solid #181c1f; }
				""")

#TODO(cody): Implement this to autocomplete based on word suggestions that
#            already exist in the document by pressing ctrl+tab
class BoostAutoCompleter(object):
	
	def __init__(self, words):
		self.words = sorted(words)
		
	def complete(self, text, state):
		#On first trigger, build all possible matches
		if state == 0:
			#Cache matches for entries that start with entered text
			if text:
				self.matches = [s for s in self.words if s and s.starswith(text)]
			#No match, all matches possible
			else:
				self.matches = self.words[:]
				
			try:
				return self.matches[state]
			except IndexError:
				return None
