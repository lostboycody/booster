import sys 

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
# Theme support: temporarily sys.argv input
try:
	if str(sys.argv[1]) == "red":
		STYLES = {
			'keyword': format('#770000'),
			'operator': format('#7A7A7A'),
			'brace': format('#454545'),
			'defclass': format('#c5a18b'),
			'string': format('#c5a18b'),
			'string2': format('#c5a18b'),
			'comment': format('#7A7A7A'),
			'self': format('#770000'),
			'numbers': format('#8A8A8A'),
		}
	elif str(sys.argv[1]) == "orange":
		STYLES = {
			'keyword': format('#8F471E'),
			'operator': format('#7A7A7A'),
			'brace': format('#454545'),
			'defclass': format('#e87330'),
			'string': format('#e87330'),
			'string2': format('#e87330'),
			'comment': format('#7A7A7A'),
			'self': format('#8F471E'),
			'numbers': format('#8A8A8A'),
		}
	elif str(sys.argv[1]) == "yellow":
		STYLES = {
			'keyword': format('#777700'),
			'operator': format('#7A7A7A'),
			'brace': format('#454545'),
			'defclass': format('#A5A448'),
			'string': format('#848337'),
			'string2': format('#848337'),
			'comment': format('#7A7A7A'),
			'self': format('#777700'),
			'numbers': format('#8A8A8A'),
		}
	elif str(sys.argv[1]) == "blue":
		STYLES = {
			'keyword': format('#003377'),
			'operator': format('#7A7A7A'),
			'brace': format('#454545'),
			'defclass': format('#375c84'),
			'string': format('#375c84'),
			'string2': format('#375c84'),
			'comment': format('#7A7A7A'),
			'self': format('#003377'),
			'numbers': format('#8A8A8A'),
		}
	elif str(sys.argv[1]) == "green":
		STYLES = {
		'keyword': format('#007765'),
		'operator': format('#7A7A7A'),
		'brace': format('#454545'),
		'defclass': format('#378437'),
		'string': format('#378437'),
		'string2': format('#378437'),
		'comment': format('#7A7A7A'),
		'self': format('#007765'),
		'numbers': format('#8A8A8A'),
	}
	elif str(sys.argv[1]) == "flosv8cafe":
		STYLES = {
		'keyword': format('#0D8580'),
		'operator': format('#7A7A7A'),
		'brace': format('#454545'),
		'defclass': format('#EF7196'),
		'string': format('#EF7196'),
		'string2': format('#EF7196'),
		'comment': format('#7A7A7A'),
		'self': format('#0D8580'),
		'numbers': format('#8A8A8A'),
	}
	elif str(sys.argv[1]) == "strangerthings":
		STYLES = {
		'keyword': format('#222F57'),
		'operator': format('#7A7A7A'),
		'brace': format('#454545'),
		'defclass': format('#BF1515'),
		'string': format('#BF1515'),
		'string2': format('#BF1515'),
		'comment': format('#7A7A7A'),
		'self': format('#222F57'),
		'numbers': format('#8A8A8A'),
	}
	elif str(sys.argv[1]) == "royal":
		STYLES = {
		'keyword': format('#00626a'),
		'operator': format('#7A7A7A'),
		'brace': format('#454545'),
		'defclass': format('#e8b290'),
		'string': format('#e8b290'),
		'string2': format('#e8b290'),
		'comment': format('#7A7A7A'),
		'self': format('#00626a'),
		'numbers': format('#8A8A8A'),
	}
except:
	STYLES = {
		'keyword': format('#6B6B6B'),
		'operator': format('#7A7A7A'),
		'brace': format('#454545'),
		'defclass': format('#8e8e8e'),
		'string': format('#8e8e8e'),
		'string2': format('#8e8e8e'),
		'comment': format('#7A7A7A'),
		'self': format('#6B6B6B'),
		'numbers': format('#8A8A8A'),
	}	

class DarkHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
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
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in DarkHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in DarkHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in DarkHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),
			# From '//' until a newline
            (r'//[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
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
