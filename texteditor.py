#Custom text editor. For fun and getting used to Python again.
#2018 Cody Azevedo

import sys
import os
import threading
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtGui import *

class TextBox_Window(object):

	file_opened = False

	def setup_app(self):
		self.create_widget()
	
	def create_widget(self, MainWindow):
		#Widget is base UI objects in PyQt4
		self.widget = QtGui.QWidget()

		#Set fixed size for now, until we can set resizable QTextEdit
		self.WIDTH = 900
		self.HEIGHT = 715
		self.widget.setFixedSize(self.WIDTH, self.HEIGHT)
		self.widget.setAutoFillBackground(True)
		MainWindow.setCentralWidget(self.widget)
		MainWindow.setWindowTitle("TypeWritr v. 0.0.1")

		#Set widget background color to dark gray for debug purposes
		palette = self.widget.palette()
		role = self.widget.backgroundRole()
		palette.setColor(role, QColor(17, 17, 17))
		self.widget.setPalette(palette)

		self.create_text_box()
		
		#Bottom command label, for use in seeing what the editor is doing
		self.bottom_label = QtGui.QLabel("", self)
		self.bottom_label.setGeometry(QtCore.QRect(0, self.HEIGHT-15, 900, 15))
		self.bottom_label.setFont(self.font)
		self.bottom_label.setStyleSheet("""
							.QLabel {
							background-color: rgb(17, 17, 17);
							color: rgb(253, 244, 193);
							}
						""")
		self.update_bottom_label("TypeWritr v. 0.0.1 by lostboycody")
		
   	def create_text_box(self):
		#TODO(Cody): Make editor window + editor resizable
   		self.textbox = QPlainTextEdit(self.widget)
   		self.textbox.resize(900, 700)
		self.textbox.setLineWrapMode(0)
   		self.textbox.setStyleSheet("""
   				.QPlainTextEdit {
           		background-color: rgb(40, 44, 50);
           		color: rgb(253, 244, 193);
           		}
       		""")
   		self.textbox.setFrameStyle(QFrame.NoFrame)
   		self.textbox.setCursorWidth(7)

   		self.font = QtGui.QFont()
   		self.font.setPointSize(11)
   		self.font.setFamily("Consolas")
   		self.textbox.setFont(self.font)

   	def file_save(self):
		text = self.textbox.toPlainText()
		
		if TextBox_Window.file_opened:
			file = open(self.open_name, 'w')
			file.write(text)
			file.close()
		else:
			self.save_name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
			file = open(self.save_name, 'w')
			file.write(text)
			file.close()

		self.update_bottom_label("Saved {}".format(self.open_name))
			
	def file_open(self):
		TextBox_Window.file_opened = True

		self.open_name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
		if os.path.isfile(self.open_name):
			file = open(self.open_name, 'r')
			with file:
				text = file.read()
				self.textbox.setPlainText(text)
		else:
			self.file_save()

		self.update_bottom_label("Opened {}".format(self.open_name))

	#Set the bottom label text, reset after 5 seconds
	def update_bottom_label(self, bottomtext):
		self.bottom_label.setText(bottomtext)
		t = threading.Timer(5.0, self.remove_bottom_label)
		t.start()

	def remove_bottom_label(self):
		self.bottom_label.setText("")

		
class MainWindow(QMainWindow, TextBox_Window):
	
	def __init__(self, parent = None):
		super(MainWindow, self).__init__(parent)
		self.create_widget(self)
			
	def keyPressEvent(self, event):
		k = event.key()
		m = int(event.modifiers())

		#TODO(Cody): Handle Ctrl+X+S etc.
		#self.connect(QtGui.QShortcut(QtGui.QKeySequence('Crtl+X, Ctrl+S'), self), QtCore.SIGNAL('activated()'), self.file_save())
		
		if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+S'):
			self.file_save()
		elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+O'):
			self.file_open()
		else:
		  	event.ignore()
	
if __name__ == '__main__':
   	#Every PyQt4 app must create an application object, sys.argv is arguments from cmd line
	app = QtGui.QApplication(sys.argv)
	w = MainWindow()
	w.show()
	sys.exit(app.exec_())
