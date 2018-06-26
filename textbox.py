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
	active_window = ""
	file_name = ""
	file_name_2 = ""
	file_path = ""
	file_path_2 = ""
	main_file_path = ""
	editing_mode = ""
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
			
		self.font = QtGui.QFont()
		self.font.setPointSize(11)
		self.font.setFamily("Consolas")

		self.create_text_box()
		self.create_text_box2()
		
		self.create_browser_bar()
		self.create_browser_bar2()

		self.file_label2.setHidden(not self.file_label2.isHidden())				
		self.filemode_label2.setHidden(not self.filemode_label2.isHidden())
		self.editmode_label2.setHidden(not self.editmode_label2.isHidden())
		self.line_label2.setHidden(not self.line_label2.isHidden())
			
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
							QWidget { background-color: transparent; border-left: 1px solid #0A0A0A; }
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
		self.browser_layout_widget.setFixedHeight(self.font_metrics.height() + 6)

		TextBox_Window.browser_layout_widget2 = QScrollArea(self.widget)
		self.browser_layout_widget2.setStyleSheet("""
							QScrollBar { height: 0px; width: 0px; background-color: transparent; border: 0px solid black; }
							QScrollArea { background-color: transparent; border: 0px solid black; }
							QWidget { background-color: transparent; border: 0px solid black; }
						""")
		self.browser_layout_widget2.setLayout(self.browser_layout2)
		self.browser_layout_widget2.setFixedHeight(self.font_metrics.height() + 6)

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
		self.browser_layout.addWidget(self.file_label)
		self.browser_layout.addWidget(self.filemode_label)
		self.browser_layout.addWidget(self.editmode_label)
		self.browser_layout.addWidget(self.line_label)

		self.browser_layout2.addWidget(self.main_text_label2)
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
			
		self.file_label.setText("_")
		self.update_cursor_position()
		self.textbox.setReadOnly(True)
		
	#Custom QPlainTextEdit
   	def create_text_box(self):
   		TextBox_Window.textbox = DarkPlainTextEdit(self.widget)

		#On cursor position update, update the label
		self.textbox.cursorPositionChanged.connect(self.update_cursor_position)
		self.textbox.setObjectName("Textbox")
		self.textbox.setCenterOnScroll(True)
		
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
		self.textbox2.setCenterOnScroll(True)
		
	def create_browser_bar(self):
		#Top label, used for file info, search, file browser etc.
		TextBox_Window.main_text_label = QtGui.QLabel("", self)
		self.main_text_label.setFixedHeight(self.font_metrics.height() + 6)
		self.main_text_label.setFont(self.font)
		self.main_text_label.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; font-size: 14px; }
						""")

		#Display file name
		self.file_label = QtGui.QLabel("", parent = self.main_text_label)
		self.file_label.setFixedHeight(self.font_metrics.height() + 6)
		self.file_label.setFont(self.font)
		self.file_label.setAlignment(QtCore.Qt.AlignRight)
		self.file_label.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; margin: 0; height: 10px; font-size: 14px; font-weight: 700; }
						""")
						
		#Line widget, for keeping line, char count
		self.line_label = QtGui.QLabel("", parent = self.main_text_label)
		self.line_label.setFixedHeight(self.font_metrics.height() + 6)
		self.line_label.setFixedWidth(90)
		self.line_label.setFont(self.font)
		self.line_label.setAlignment(QtCore.Qt.AlignRight)
		self.line_label.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; font-size: 14px; border-right: 2px solid #121212; }
						""")

		TextBox_Window.filemode_label = QtGui.QLabel("", parent = self.main_text_label)
		self.filemode_label.setFixedHeight(self.font_metrics.height() + 6)
		self.filemode_label.setFixedWidth(60)
		self.filemode_label.setFont(self.font)
		self.filemode_label.setAlignment(QtCore.Qt.AlignRight)
		self.filemode_label.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: brown; padding-top: 4px; font-size: 14px; font-weight: 700; }
						""")
						
		TextBox_Window.editmode_label = QtGui.QLabel("", parent = self.main_text_label)
		self.editmode_label.setFixedHeight(self.font_metrics.height() + 6)
		self.editmode_label.setFixedWidth(60)
		self.editmode_label.setFont(self.font)
		self.editmode_label.setAlignment(QtCore.Qt.AlignRight)
		self.editmode_label.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; font-size: 14px; font-weight: 700; }
						""")

	def create_browser_bar2(self):
		TextBox_Window.main_text_label2 = QtGui.QLabel(self.widget)
		self.main_text_label2.setFixedHeight(self.font_metrics.height() + 6)
		self.main_text_label2.setFont(self.font)
		self.main_text_label2.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; font-size: 14px;}
						""")

		self.file_label2 = QtGui.QLabel("", parent = self.main_text_label)
		self.file_label2.setFixedHeight(self.font_metrics.height() + 6)
		self.file_label2.setFont(self.font)
		self.file_label2.setAlignment(QtCore.Qt.AlignRight)
		self.file_label2.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; margin: 0; height: 10px; font-size: 14px; font-weight: 700; }
						""")

		self.line_label2 = QtGui.QLabel("", parent = self.main_text_label)
		self.line_label2.setFixedHeight(self.font_metrics.height() + 6)
		self.line_label2.setFixedWidth(90)
		self.line_label2.setFont(self.font)
		self.line_label2.setAlignment(QtCore.Qt.AlignRight)
		self.line_label2.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; font-size: 14px; }
						""")

		TextBox_Window.filemode_label2 = QtGui.QLabel("", parent = self.main_text_label2)
		self.filemode_label2.setFixedHeight(self.font_metrics.height() + 6)
		self.filemode_label2.setFixedWidth(60)
		self.filemode_label2.setFont(self.font)
		self.filemode_label2.setAlignment(QtCore.Qt.AlignRight)
		self.filemode_label2.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: brown; padding-top: 4px; font-size: 14px; font-weight: 700; }
						""")

		TextBox_Window.editmode_label2 = QtGui.QLabel("", parent = self.main_text_label)
		self.editmode_label2.setFixedHeight(self.font_metrics.height() + 6)
		self.editmode_label2.setFixedWidth(60)
		self.editmode_label2.setFont(self.font)
		self.editmode_label2.setAlignment(QtCore.Qt.AlignRight)
		self.editmode_label2.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; font-size: 14px; font-weight: 700; }
						""")

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
			self.line_label2.setText("L{}|C{}".format(self.line, self.col))
		else:	
			self.line_label.setText("L{}|C{}".format(self.line, self.col))

	def file_open(self, file):
		TextBox_Window.file_opened = True

		#Don't modify this file
		if "firstfile.txt" in str(os.path.abspath(file)):
			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setReadOnly(True)
				self.editmode_label2.setText("[nav]")
			else:
				self.textbox.setReadOnly(True)
				self.editmode_label.setText("[nav]")
		else:
			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setReadOnly(False)
				self.textbox2.setStyle(self.textbox2.style())
				self.editmode_label2.setText("[ins]")
			else:
				self.textbox.setReadOnly(False)
				self.textbox.setStyle(self.textbox.style())
				self.editmode_label.setText("[ins]")
		
		#If the file exists, open it and write to textbox
		if os.path.isfile(file):
			self.file = open(file, 'rb')
			with self.file:
				self.open_text = self.file.read()
				self.file_length = len(self.open_text)
				
			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setPlainText(self.open_text)
				TextBox_Window.file_path_2 = str(os.path.join(os.getcwd(), file))
				TextBox_Window.file_name_2 = self.get_file_name(file)
			else:
				self.textbox.setPlainText(self.open_text)
				TextBox_Window.file_path = str(os.path.join(os.getcwd(), file))
				TextBox_Window.file_name = self.get_file_name(file)

		#If the file doesn't exist, create new file and write blank text to textbox
		if not os.path.isfile(file):
			self.open_text = ""
			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setPlainText(self.open_text)
			else:
				self.textbox.setPlainText(self.open_text)
			self.file_length = len(self.open_text)

		self.file_name = self.get_file_name(file)
		self.file_path = os.path.join(os.getcwd(), self.file_name)		
		self.update_bottom_label("Opened {}".format(self.file_path))

		if TextBox_Window.active_window == "Textbox2":
			self.file_label2.setText(self.file_name)
		   	self.file_label2.setFixedWidth(self.font_metrics.width(self.file_name) + 20)
			self.stacked_layout.setCurrentIndex(0)
			self.block = self.textbox2.firstVisibleBlock()
			self.textbox2.setFocus()

			try:
				if "\r\n" in open(self.file_path, "rb").read():
					self.filemode_label2.setText("*dos")
					self.filemode_label2.setToolTip(TextBox_Window.dos_tooltip)
				elif "\n" in open(self.file_path, "rb").read():
					self.filemode_label2.setText("*nix")
					self.filemode_label2.setToolTip(TextBox_Window.nix_tooltip)
			except:
				self.filemode_label2.setText("")
		else:
			self.file_label.setText(self.file_name)
		   	self.file_label.setFixedWidth(self.font_metrics.width(self.file_name) + 20)
			self.stacked_layout.setCurrentIndex(0)
			self.block = self.textbox.firstVisibleBlock()
			self.textbox.setFocus()
			
			try:
				if "\r\n" in open(self.file_path, "rb").read():
					self.filemode_label.setText("*dos")
					self.filemode_label.setToolTip(TextBox_Window.dos_tooltip)
				elif "\n" in open(self.file_path, "rb").read():
					self.filemode_label.setText("*nix")
					self.filemode_label.setToolTip(TextBox_Window.nix_tooltip)
			except:
				self.filemode_label.setText("")

		if DarkPlainTextEdit.is_window_split:
			self.file_label2.setVisible(True)
			self.filemode_label2.setVisible(True)
			self.editmode_label2.setVisible(True)
			self.line_label2.setVisible(True)
		
		self.update_cursor_position()

		TextBox_Window.dir_browser_open = False
		
		#Replace top browser after file browser closes
		self.main_text_label.setStyleSheet("""
							.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; font-size: 14px; }
						""")
		self.browser_layout.addWidget(self.file_label)
		self.browser_layout.addWidget(self.filemode_label)
		self.browser_layout.addWidget(self.editmode_label)
		self.browser_layout.addWidget(self.line_label)

		TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width(), 0, 0, 0)

		if TextBox_Window.active_window == "Textbox2":
			self.textbox2.setFocus()
		else:
			self.textbox.setFocus()
							
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
		#Otherwise make new file depending on OS
		except:
			if os.name == "nt":
				self.save_text = self.convert_line_endings(str(self.save_text), 2)
			else:
				self.save_text = self.convert_line_endings(str(self.save_text), 0)				
		
		#If the file has been opened, save it automatically
		if TextBox_Window.file_opened:
			self.file = open(TextBox_Window.main_file_path, 'wb+')

			#If the file has been modified, save it
			if self.open_text != self.save_text:
				self.file.write(str(self.save_text).encode('utf-8'))
				self.file.close()
				self.update_bottom_label("Wrote {}".format(TextBox_Window.main_file_path))
				self.open_text = self.save_text
			#Writing again. Inefficient but safe.
			elif self.open_text == self.save_text:
				self.update_bottom_label("No changes need to be saved")
				self.file.write(str(self.save_text).encode('utf-8'))
				self.file.close()
				
		#Safekeeping, *just in case* the file hasn't been opened / doesn't exist yet
		else:
			self.save_name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
			self.file = open(self.save_name, 'wb+')
			
			if TextBox_Window.active_window == "Textbox2":
				if TextBox_Window.filemode_label2 == "*nix":
					self.convert_line_endings(self.save_text, 0)
				elif TextBox_Window.filemode_label2 == "*dos":
					self.convert_line_endings(self.save_text, 2)
			else:			
				if TextBox_Window.filemode_label == "*nix":
					self.convert_line_endings(self.save_text, 0)
				elif TextBox_Window.filemode_label == "*dos":
					self.convert_line_endings(self.save_text, 2)
				
			self.file.write(str(self.save_text).encode('utf-8'))
			self.file.close()
			self.update_bottom_label("Wrote {}".format(self.save_name))
			
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

			TextBox_Window.new_file_name = SearchLineEdit("")
			self.new_file_name.setFixedHeight(self.font_metrics.height() + 6)
			self.new_file_name.setFont(self.font)
			self.new_file_name.setStyleSheet("""
								.SearchLineEdit { background-color: #050505; color: #BFBFBF; padding-top: 4px; border: 0px solid black; font-size: 14px; }
							""")
			TextBox_Window.get_new_file = QtGui.QLabel(" New filename:", parent = self.main_text_label)
			self.get_new_file.setFixedHeight(self.font_metrics.height() + 6)
			self.get_new_file.setFont(self.font)
			self.get_new_file.setStyleSheet("""
								.QLabel { background-color: #050505; color: #BFBFBF; padding-top: 4px; border: 0px solid black; font-size: 14px; }
							""")
							
			if TextBox_Window.active_window == "Textbox2":
				self.browser_layout2.addWidget(self.get_new_file)
				self.browser_layout2.addWidget(self.new_file_name)
			else:
				self.browser_layout.addWidget(self.get_new_file)
				self.browser_layout.addWidget(self.new_file_name)
			
			TextBox_Window.new_file_displayed = True

		self.new_file_name.setFocus()
		self.new_file_name.returnPressed.connect(self.open_new_file)

	def open_new_file(self):
		self.new_file_path = os.path.join(os.getcwd(), str(self.new_file_name.text()))
		TextBox_Window.main_file_path = self.new_file_path
		
		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.file_path_2 = self.new_file_path
		else:
			TextBox_Window.file_path = self.new_file_path
			
		self.open_text = ""
		self.file_open(self.new_file_path)
			
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
			self.selection = QTextEdit.ExtraSelection()
			self.lineColor = QColor(Qt.black)

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
			self.query.setFont(self.font)
			self.query.setStyleSheet("""
								.SearchLineEdit { background-color: #050505; color: #BFBFBF; border: 0px solid black; font-size: 14px; }
							""")
			TextBox_Window.search_text = QtGui.QLabel(" Search:", parent = self.main_text_label)
			self.search_text.setFixedHeight(self.font_metrics.height() + 6)
			self.search_text.setFont(self.font)
			self.search_text.setStyleSheet("""
								.QLabel { background-color: #050505; color: #BFBFBF; padding-top: 4px; border: 0px solid black; font-size: 14px }
							""")
							
			if TextBox_Window.active_window == "Textbox2":
				self.browser_layout2.addWidget(self.search_text)
				self.browser_layout2.addWidget(self.query)
			else:
				self.browser_layout.addWidget(self.search_text)
				self.browser_layout.addWidget(self.query)
		
		TextBox_Window.search_displayed = True

		self.query.setFocus()
		self.query.textChanged.connect(self.search_in_file)
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
								.SearchLineEdit { background-color: #050505; color: #BFBFBF; border: 0px solid black; font-size: 14px; }
								""")
		else:
			end = 0
			self.query.setStyleSheet("""
								.SearchLineEdit { background-color: #1E0000; color: #BFBFBF; border: 0px solid black; font-size: 14px; }
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
		TextBox_Window.dir_browser_open = True;

		#Display the browser directory and remove the bottom label
		self.main_text_label.setStyleSheet("""
							.QLabel { background-color: #AFAFAF; color: black; padding-top: 4px; font-size: 14px; font-weight: bold; text-align: left;}
						""")
		self.file_label.setParent(None)
		self.line_label.setParent(None)

	   	self.current_dir = os.chdir(os.getcwd())
		self.dialog_button_box.clear()
	   	self.main_text_label.setText(str(os.getcwd()))

		#Previous directory button
  		self.previous_dir_button = QPushButton("../")
		self.previous_dir_button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
	   	self.previous_dir_button.setStyleSheet("""
	   	  						.QPushButton { border: none; background-color: #121212; color: #009435; text-align: left; padding: 5px; font-family: Consolas; font-size: 14px; }
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
				self.button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
	   	   		self.button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #121212; color: #009435; text-align: left; padding: 5px; font-family: Consolas; font-size: 14px; }
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
				self.button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
	   	   		self.button.setStyleSheet("""
	   	   							.QPushButton { border: none; background-color: #121212; color: #AFAFAF; text-align: left; padding: 5px; font-family: Consolas; font-size: 14px; }
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
		   	  						.QPushButton { border: none; background-color: #121212; color: white; text-align: left; padding: 5px; font-family: Consolas; font-size: 14px; }
		   							.QPushButton:focus { outline: 0px; border: 2px solid #007765; }
	   	   						""")
		self.new_file_button.setMinimumSize(QSize(self.outer_widget_1.width(), 30))
		self.new_file_button.setAutoDefault(True)
		self.new_file_button.pressed.connect(self.setup_new_file)
		self.dialog_button_box.addButton(self.new_file_button, QDialogButtonBox.ActionRole)

		self.stacked_layout.setCurrentIndex(1)
		self.dialog_button_box.setFocus()

		self.file_label.setParent(None)
		self.filemode_label.setParent(None)
		self.editmode_label.setParent(None)
		self.line_label.setParent(None)
				
	#Without opening file
	def close_dir_browser(self):
		if TextBox_Window.dir_browser_open == True:
			os.chdir(self.temp_dir)
			self.stacked_layout.setCurrentIndex(0)
			self.main_text_label.setStyleSheet("""
								.QLabel { background-color: #0A0A0A; color: #BFBFBF; padding-top: 4px; font-size: 14px; }
							""")
			self.main_text_label.setText("")
			self.browser_layout.addWidget(self.file_label)
			self.browser_layout.addWidget(self.filemode_label)
			self.browser_layout.addWidget(self.line_label)
	
			TextBox_Window.browser_layout2.setContentsMargins(TextBox_Window.browser_layout_widget.width(), 0, 0, 0)

			if TextBox_Window.active_window == "Textbox2":
				self.textbox2.setFocus()
			else:
				self.textbox.setFocus()
				
			TextBox_Window.dir_browser_open = False
	
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

class DarkPlainTextEdit(QtGui.QPlainTextEdit, TextBox_Window):

	is_window_split = False
	
	def __init__(self, parent = None):
		super(DarkPlainTextEdit, self).__init__(parent)

		self.editor = QPlainTextEdit()
		self.setMinimumSize(10, 10)
		self.setLineWrapMode(0)
		self.setStyleSheet("""
	   				DarkPlainTextEdit { background-color: #121212; selection-color: white; selection-background-color: black; color: #378437; }
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

		self.editor.setFocusPolicy(QtCore.Qt.StrongFocus)
		self.editor.installEventFilter(self)
		
	#Release instead of press event for RETURN insert syncing
	def keyReleaseEvent(self, event):
		k = event.key()

		if k == QtCore.Qt.Key_Return:
			self.auto_indent()
			
		QtGui.QPlainTextEdit.keyReleaseEvent(self, event)

	#Handle custom keyevents that occur in the editor	
	def keyPressEvent(self, event):
   		k = event.key()
		m = int(event.modifiers())
		modifiers = QtGui.QApplication.keyboardModifiers()

		if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+X'):
			if not DarkPlainTextEdit.is_window_split:
				self.split_buffer()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Down'):
			self.next_empty_line()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+Up'):
			self.previous_empty_line()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+E'):
			self.end_of_line()
		elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier and k == QtCore.Qt.Key_Down:
			self.highlight_next_block()
		elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier and k == QtCore.Qt.Key_Up:
			self.highlight_previous_block()
		elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier and k == QtCore.Qt.Key_E:
			self.highlight_to_end_of_line()
		elif modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier:
			self.highlight_mode = True
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+M'):
			self.switch_editing_mode()
								
		QtGui.QPlainTextEdit.keyPressEvent(self, event)
		
	def focusInEvent(self, event):
		TextBox_Window.active_window = self.objectName()	
		super(DarkPlainTextEdit, self).focusInEvent(event)

		if TextBox_Window.active_window == "Textbox2":
			TextBox_Window.main_file_path = TextBox_Window.file_path_2
		else:
			TextBox_Window.main_file_path = TextBox_Window.file_path
					
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
		self.cursor = self.textCursor()
		self.line = self.cursor.blockNumber() + 1
		self.col = self.cursor.columnNumber()
		
		self.document_text = self.document()
		self.block = self.document_text.findBlockByLineNumber(self.line - 2)

		tab = "\t"
		tab_array = []
		string_beginning = len(str(self.block.text())) - len(str(self.block.text()).lstrip(tab))
		for i in range(string_beginning):
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
			if re.search('[^\s*$]', self.block.text()) and self.block.next().next().text() != self.first_block.text():
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
			if re.search('[^\s*$]', self.block.text()) and self.block.previous().previous().text() != "":
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
			if re.search('[^\s*$]', self.block.text()) and self.block.next().next().text() != self.first_block.text():
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
			if re.search('[^\s*$]', self.block.text()) and self.block.previous().previous().text() != "":
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
				self.editmode_label2.setText("[ins]")
				self.editmode_label2.setToolTip(TextBox_Window.ins_tooltip)
			else:
				self.textbox2.setReadOnly(True)
				self.textbox2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
				self.textbox2.setStyle(TextBox_Window.textbox2.style())
				self.editmode_label2.setText("[nav]")
				self.editmode_label2.setToolTip(TextBox_Window.nav_tooltip)
		else:
			if TextBox_Window.textbox.isReadOnly():
				self.textbox.setReadOnly(False)
				self.textbox.setStyle(TextBox_Window.textbox.style())
				self.editmode_label.setText("[ins]")
				self.editmode_label.setToolTip(TextBox_Window.ins_tooltip)
			else:
				self.textbox.setReadOnly(True)
				self.textbox.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
				self.textbox.setStyle(TextBox_Window.textbox.style())
				self.editmode_label.setText("[nav]")
				self.editmode_label.setToolTip(TextBox_Window.nav_tooltip)				

#Custom QLineEdit for search query, removes search box when focus is lost
class SearchLineEdit(QtGui.QLineEdit, TextBox_Window):

	def __init__(self, parent = None):
		super(SearchLineEdit, self).__init__(parent)
		
   	def focusOutEvent(self, event):
		if TextBox_Window.search_displayed == True:
			self.remove_search_box()
		elif TextBox_Window.new_file_displayed == True:
			self.remove_new_file_box()
			
