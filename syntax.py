import sys
import os 

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

def format(color, style=''):
	#Return a QTextCharFormat with the given attributes.
	
	_color = QColor()
	_color.setNamedColor(color)

	_format = QTextCharFormat()
	_format.setForeground(_color)
	if 'bold' in style:
		_format.setFontWeight(QFont.Bold)
	if 'italic' in style:
		_format.setFontItalic(True)

	return _format
		
class BoostSourceHighlighter(QSyntaxHighlighter):
	global syntax_mode
	file_extensions = ["py", "java", "cpp", "c", "htm", "html", "js",
	"css", "php", "h", "cs", "sh"]
	
			
	def __init__(self, document, filename, syntax_mode, syntax_theme):
		self.document = document
		QSyntaxHighlighter.__init__(self, self.document)
	
		try:
			filename_extension = filename.rsplit('.', 1)
			filename_extension = filename_extension[1]
		except:
			filename_extension = ""					
		
		for extension in BoostSourceHighlighter.file_extensions:
			if extension == filename_extension:
				syntax_mode = filename_extension
	
		# Syntax styles that can be shared by all languages
		# Theme support: temporarily sys.argv input
		try:
			if syntax_theme == "Monochrome" or str(sys.argv[1]) == "monochrome":
				STYLES = {
					'keyword': format('#38898C'),
					'operator': format('#419141'),
					'brace': format('#878787'),
					'defclass': format('#759F6F'),
					'string': format('#759F6F'),
					'string2': format('#759F6F'),
					'comment': format('#6b6b6b'),
					'self': format('#38898C'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Red" or str(sys.argv[1]) == "red":
				STYLES = {
					'keyword': format('#770000'),
					'operator': format('#7A7A7A'),
					'brace': format('#878787'),
					'defclass': format('#9C4343'),
					'string': format('#9C4343'),
					'string2': format('#9C4343'),
					'comment': format('#494949'),
					'self': format('#770000'),
					'numbers': format('#8A8A8A'),
				}
			elif syntax_theme == "Orange" or str(sys.argv[1]) == "orange":
				STYLES = {
					'keyword': format('#8F471E'),
					'operator': format('#7A7A7A'),
					'brace': format('#878787'),
					'defclass': format('#e87330'),
					'string': format('#e87330'),
					'string2': format('#e87330'),
					'comment': format('#494949'),
					'self': format('#8F471E'),
					'numbers': format('#8A8A8A'),
				}
			elif syntax_theme == "Yellow" or str(sys.argv[1]) == "yellow":
				STYLES = {
					'keyword': format('#777700'),
					'operator': format('#7A7A7A'),
					'brace': format('#878787'),
					'defclass': format('#A5A448'),
					'string': format('#848337'),
					'string2': format('#848337'),
					'comment': format('#494949'),
					'self': format('#777700'),
					'numbers': format('#8A8A8A'),
				}
			elif syntax_theme == "Blue" or str(sys.argv[1]) == "blue":
				STYLES = {
					'keyword': format('#003377'),
					'operator': format('#7A7A7A'),
					'brace': format('#878787'),
					'defclass': format('#375c84'),
					'string': format('#375c84'),
					'string2': format('#375c84'),
					'comment': format('#494949'),
					'self': format('#003377'),
					'numbers': format('#8A8A8A'),
				}
			elif syntax_theme == "Green" or str(sys.argv[1]) == "green":
				STYLES = {
					'keyword': format('#007765'),
					'operator': format('#7A7A7A'),
					'brace': format('#878787'),
					'defclass': format('#378437'),
					'string': format('#378437'),
					'string2': format('#378437'),
					'comment': format('#494949'),
					'self': format('#007765'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Flo\'s V8 Cafe" or str(sys.argv[1]) == "flosv8cafe":
				STYLES = {
					'keyword': format('#0D8580'),
					'operator': format('#7A7A7A'),
					'brace': format('#878787'),
					'defclass': format('#EF7196'),
					'string': format('#EF7196'),
					'string2': format('#EF7196'),
					'comment': format('#494949'),
					'self': format('#0D8580'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Stranger Things" or str(sys.argv[1]) == "strangerthings":
				STYLES = {
					'keyword': format('#222F57'),
					'operator': format('#7A7A7A'),
					'brace': format('#878787'),
					'defclass': format('#BF1515'),
					'string': format('#BF1515'),
					'string2': format('#BF1515'),
					'comment': format('#494949'),
					'self': format('#222F57'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Royal" or str(sys.argv[1]) == "royal":
				STYLES = {
					'keyword': format('#00626a'),
					'operator': format('#4D1675'),
					'brace': format('#878787'),
					'defclass': format('#e8b290'),
					'string': format('#e8b290'),
					'string2': format('#e8b290'),
					'comment': format('#494949'),
					'self': format('#00626a'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Scoops Ahoy" or str(sys.argv[1]) == "scoopsahoy":
				STYLES = {
					'keyword': format('#473B5F'),
					'operator': format('#943B41'),
					'brace': format('#878787'),
					'defclass': format('#943B41'),
					'string': format('#D2A89C'),
					'string2': format('#D2A89C'),
					'comment': format('#494949'),
					'self': format('#473B5F'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Old Locomotive" or str(sys.argv[1]) == "oldlocomotive":
				STYLES = {
					'keyword': format('#916438'),
					'operator': format('#878787'),
					'brace': format('#878787'),
					'defclass': format('#389138'),
					'string': format('#389138'),
					'string2': format('#389138'),
					'comment': format('#6b6b6b'),
					'self': format('#916438'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Green (Muted)" or str(sys.argv[1]) == "greenmuted":
				STYLES = {
					'keyword': format('#38898C'),
					'operator': format('#878787'),
					'brace': format('#878787'),
					'defclass': format('#759F6F'),
					'string': format('#759F6F'),
					'string2': format('#759F6F'),
					'comment': format('#6b6b6b'),
					'self': format('#38898C'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Winter" or str(sys.argv[1]) == "winter":
				STYLES = {
					'keyword': format('#875F5F'),
					'operator': format('#878787'),
					'brace': format('#878787'),
					'defclass': format('#5F5F87'),
					'string': format('#38898C'),
					'string2': format('#38898C'),
					'comment': format('#6b6b6b'),
					'self': format('#38898C'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "SpaCy" or str(sys.argv[1]) == "spacy":
				STYLES = {
					'keyword': format('#DB2C55'),
					'operator': format('#878787'),
					'brace': format('#878787'),
					'defclass': format('#FFB86C'),
					'string': format('#FFB86C'),
					'string2': format('#FFB86C'),
					'comment': format('#6b6b6b'),
					'self': format('#DEDEDE'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Alabaster" or str(sys.argv[1]) == "alabaster":
				STYLES = {
					'keyword': format('#007765'),
					'operator': format('#7A7A7A'),
					'brace': format('#000000'),
					'defclass': format('#378437'),
					'string': format('#378437'),
					'string2': format('#378437'),
					'comment': format('#378437'),
					'self': format('#000000'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "SpaceX" or str(sys.argv[1]) == "spacex":
				STYLES = {
					'keyword': format('#186298'),
					'operator': format('#878787'),
					'brace': format('#878787'),
					'defclass': format('#287FB1'),
					'string': format('#FF9210'),
					'string2': format('#FF9210'),
					'comment': format('#FF9210'),
					'self': format('#DEDEDE'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "Forest" or str(sys.argv[1]) == "forest":
				STYLES = {
					'keyword': format('#379439'),
					'operator': format('#BBC1A8'),
					'brace': format('#8C8C8C'),
					'defclass': format('#CC652D'),
					'string': format('#CC652D'),
					'string2': format('#CC652D'),
					'comment': format('#8C8C8C'),
					'self': format('#FFFFFF'),
					'numbers': format('#8A8A8A'),
			}
			elif syntax_theme == "":
				STYLES = {
					'keyword': format('#5E5E5E'),
					'operator': format('#494949'),
					'brace': format('#878787'),
					'defclass': format('#B5B5B5'),
					'string': format('#B5B5B5'),
					'string2': format('#B5B5B5'),
					'comment': format('#494949'),
					'self': format('#5E5E5E'),
					'numbers': format('#A6A28C'),
				}
		except:
			STYLES = {
				'keyword': format('#2273A5'),
				'operator': format('#DBD9D5'),
				'brace': format('#DBD9D5'),
				'defclass': format('#FFC629'),
				'string': format('#77D479'),
				'string2': format('#77D479'),
				'comment': format('#6e6b5e'),
				'self': format('#6e6b5e'),
				'numbers': format('#DBD9D5'),
			}
			
		if syntax_mode == "html":
			keywords = [
				'a', 'abbr', 'acronym', 'address', 'applet', 
				'area', 'article', 'aside', 'audio', 'b', 'base', 
				'basefont', 'bdi', 'bdo', 'bgsound', 'big', 'blink', 
				'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 
				'center', 'cite', 'code', 'col', 'colgroup', 'command', 
				'content', 'data', 'datalist', 'dd', 'del', 'details', 
				'dfn', 'dialog', 'dir', 'div', 'dl', 'dt', 'element', 
				'em', 'embed', 'fieldset', 'figcaption', 'figure', 'font', 
				'footer', 'form', 'frame', 'frameset', 'h1', 'head', 'header', 
				'hgroup', 'hr', 'html', 'i', 'iframe', 'image', 'img', 'input', 
				'ins', 'isindex', 'kbd', 'keygen', 'label', 'legend', 'li', 
				'link', 'listing', 'main', 'map', 'mark', 'marquee', 'menu', 
				'menuitem', 'meta', 'meter', 'multicol', 'nav', 'nextid', 'nobr', 
				'noembed', 'noframes', 'noscript', 'object', 'ol', 'optgroup', 
				'option', 'output', 'p', 'param', 'picture', 'plaintext', 'pre', 
				'progress', 'q', 'rb', 'rp', 'rt', 'rtc', 'ruby', 's', 'samp', 
				'script', 'section', 'select', 'shadow', 'slot', 'small', 'source', 
				'spacer', 'span', 'strike', 'strong', 'style', 'sub', 'summary', 
				'sup', 'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 
				'th', 'thead', 'time', 'title', 'tr', 'track', 'tt', 'u', 'ul', 
				'var', 'video', 'wbr', 'xmp', 
			]
			operators = [
				# Arithmetic
				'\+', '-', '\*', '/', '//', '\%', '\*\*',
			]
			braces = [
				'\{', '\}', '\(', '\)', '\[', '\]',
			]

		elif syntax_mode == "js":
			keywords = [
				'abstract', 'arguments', 'await*', 'boolean', 'break', 'byte', 'case', 
				'catch', 'char', 'class*', 'const', 'continue', 'debugger', 'default', 
				'delete', 'do', 'double', 'else', 'enum*', 'evalexport*', 'extends*', 
				'false', 'final', 'finally', 'float', 'for', 'function', 'goto', 'if', 
				'implements', 'import*', 'in', 'instanceof', 'int', 'interface', 'let*', 
				'long', 'native', 'new', 'null', 'package', 'private', 'protected', 'public', 
				'return', 'short', 'static', 'super*', 'switch', 'synchronized', 'this', 
				'throw', 'throws', 'transient', 'true', 'try', 'typeof', 'var', 'void', 
				'volatile', 'while', 'with', 'yield'	
			]
			
			operators = [
				# Arithmetic
				'\+', '-', '\*', '/', '//', '\%', '\*\*',
			]
			
			braces = [
				'\{', '\}', '\(', '\)', '\[', '\]',
			]

		elif syntax_mode == "cpp":
			keywords = [
				'__abstract', '__alignof', 'Operator', '__asm', '__assume', '__based', 
				'__box', '__cdecl', '__declspec', '__delegate', '__event', '__except', 
				'__fastcall', '__finally', '__forceinline', '__gc', '__hook', '__identifier', 
				'__if_exists', '__if_not_exists', '__inline', '__int16', '__int32', '__int64', 
				'__int8', '__interface', '__leave', '__m128', '__m128d', '__m128i', '__m64', 
				'__multiple_inheritance', '__nogc', '__noop', '__pin', '__property', '__ptr32', 
				'__ptr644', '__raise', '__restrict', '__sealed', '__single_inheritance4', '__sptr4', 
				'__stdcall', '__super', '__thiscall', '__try_cast', '__unaligned', '__unhook', 
				'__uptr', '__uuidof', '__value', '__vectorcall', '__virtual_inheritance', '__w64', 
				'__wchar_t', 'abstract', 'alignas', 'array', 'auto', 'bool', 'break', 'case', 
				'catch', 'char', 'char16_t', 'char32_t', 'class', 'const', 'const_cast', 'constexpr', 
				'continue', 'decltype', 'default', 'delegate', 'delete', 'deprecated', 'dllexport', 
				'dllimport', 'do', 'double', 'dynamic_cast', 'else', 'enum', 'enum', 'class', 'enum', 'include',
				'struct', 'event', 'explicit', 'extern', 'false', 'finally', 'float', 'for', 'for', 
				'each', 'in', 'friend', 'friend_as', 'gcnew', 'generic', 'goto', 'if', 'initonly', 
				'inline', 'int', 'interface', 'class', 'interface', 'struct', 'interior_ptr', 'literal', 
				'long', 'mutable', 'naked', 'namespace', 'new', 'new', 'noexcept', 'noinline', 'noreturn', 
				'nothrow', 'novtable', 'nullptr', 'operator', 'private', 'property', 'property', 'protected', 
				'public', 'ref', 'class', 'ref', 'struct', 'register', 'reinterpret_cast', 'return', 
				'safecast', 'sealed', 'selectany', 'short', 'signed', 'sizeof', 'static', 'static_assert', 
				'static_cast', 'struct', 'string', 'switch', 'template', 'this', 'thread', 'throw', 'true', 'try', 
				'typedef', 'typeid', 'typeid', 'typename', 'union', 'unsigned', 'using', 'declaration', 'using', 
				'directive', 'uuid', 'value', 'class', 'value', 'struct', 'virtual', 'void', 'volatile', 'while'	
			]
			
			operators = [
				# Arithmetic
				'\+', '-', '\*', '/', '//', '\%', '\*\*',
			]
			
			braces = [
				'\{', '\}', '\(', '\)', '\[', '\]',
			]

									
		# Python operators
		elif syntax_mode in BoostSourceHighlighter.file_extensions:
			# Python keywords
			keywords = [
				'and', 'assert', 'break', 'class', 'continue', 'def',
				'del', 'elif', 'else', 'except', 'exec', 'finally',
				'for', 'from', 'global', 'if', 'import', 'in',
				'is', 'lambda', 'not', 'or', 'pass', 'print',
				'raise', 'return', 'try', 'while', 'yield',
				'None', 'True', 'False',
			]
			operators = [
				'=',
				# Comparison
				'==', '!=', '<', '<=', '>', '>=',
				# Arithmetic
				'\+', '-', '\*', '/', '//', '\%', '\*\*',
				# In-place
				'\+=', '-=', '\*=', '/=', '\%=',
				# Bitwise
				'\^', '\|', '\&', '\~', '>>', '<<',
			]
	
			# Python braces
			braces = [
				'\{', '\}', '\(', '\)', '\[', '\]',
			]
			  
		else:
			keywords = []
			operators = []
			braces = []
			
		QSyntaxHighlighter.__init__(self, self.document)
						
		# Multi-line strings (expression, flag, style)
		# FIXME: The triple-quotes in these two lines will mess up the
		# syntax highlighting from this point onward
		self.tri_single = (QRegExp("'''"), 1, STYLES['comment'])
		self.tri_double = (QRegExp('"""'), 2, STYLES['comment'])

		highlight_rules = []

		# Keyword, operator, and brace rules
		highlight_rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
			for w in keywords]
		highlight_rules += [(r'%s' % o, 0, STYLES['operator'])
			for o in operators]
		highlight_rules += [(r'%s' % b, 0, STYLES['brace'])
			for b in braces]				
				
		# All other rules
		if str(syntax_mode) != "html" and str(syntax_mode) != "htm":
			highlight_rules += [
				# 'self'
				(r'\bself\b', 0, STYLES['self']),
		
				# 'def' followed by an identifier
				(r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
				# 'class' followed by an identifier
				(r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),
	
				# Function call after . and before (
			#	(r'\.(?:[^\.]*(?=([(])))', 0, STYLES['function']),
			#	(r'\.[\w]+(?=\()', 0, STYLES['function']),
	
				# Numeric literals
				(r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
				(r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
				(r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),

				# From '//' until a newline
				(r'//[^\n]*', 0, STYLES['comment']),
		
				#Comments between /* and */
				(r'\/\*(?:(?!\*)(?:.|[\r\n]+))*\*\/', 1, STYLES['comment']),
			]

		#Python comment
		if str(syntax_mode) == "py":
			highlight_rules += [
				# From '#' until a newline
				(r'#[^\n]*', 0, STYLES['comment']),			
			]

		elif str(syntax_mode) == "html" or str(syntax_mode) == "htm":
			highlight_rules += [
				(r'\<![ \r\n\t]*(--([^\-]|[\r\n]|-[^\-])*--[ \r\n\t]*)\>', 1, STYLES['comment']),
			]
						
		highlight_rules += [		
			# Double-quoted string, possibly containing escape sequences
			(r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
			# Single-quoted string, possibly containing escape sequences
			(r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
		]
										
		self.rules = [(QRegExp(pat), index, fmt)
		for (pat, index, fmt) in highlight_rules]		
						
	def highlightBlock(self, text):
		"""Apply syntax highlighting to the given block of text.
		"""
		# Do other syntax formatting
		try:
			for expression, nth, format in self.rules:
				index = expression.indexIn(text, 0)
	
				while index >= 0:
					# We actually want the index of the nth match
					index = expression.pos(nth)
					length = expression.cap(nth).length()
					self.setFormat(index, length, format)
					index = expression.indexIn(text, index + length)
	
			self.setCurrentBlockState(0)
	
			# Do multi-line strings
			in_multiline = self.match_multiline(text, *self.tri_single)
			if not in_multiline:
				in_multiline = self.match_multiline(text, *self.tri_double)
		except:
			pass


	def match_multiline(self, text, delimiter, in_state, style):
		"""Do highlighting of multi-line strings. ``delimiter`` should be a
		``QRegExp`` for triple-single-quotes or triple-double-quotes, and
		``in_state`` should be a unique integer to represent the corresponding
		state changes when inside those strings. Returns True if we're still
		inside a multi-line string when this function is finished.
		"""
		# If inside triple-single quotes, start at 0
		if self.previousBlockState() == in_state:
			start = 0
			add = 0
		# Otherwise, look for the delimiter on this line
		else:
			start = delimiter.indexIn(text)
			# Move past this match
			add = delimiter.matchedLength()

		# As long as there's a delimiter match on this line...
		while start >= 0:
			# Look for the ending delimiter
			end = delimiter.indexIn(text, start + add)
			# Ending delimiter on this line?
			if end >= add:
				length = end - start + add + delimiter.matchedLength()
				self.setCurrentBlockState(0)
			# No; multi-line string
			else:
				self.setCurrentBlockState(in_state)
				length = text.length() - start + add
			# Apply formatting
			self.setFormat(start, length, style)
			# Look for the next match
			start = delimiter.indexIn(text, start + length)

		# Return True if still inside a multi-line string, False otherwise
		if self.currentBlockState() == in_state:
			return True
		else:
			return False

