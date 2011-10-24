from flojay.state import ParserState
from flojay.exception import SyntaxError
import string


class NotImplementedException(Exception):
    pass


class UnicodeCodepointState(ParserState):
    def setUp(self):
        self.buf = ""

    def parse_terminal_character(self, c):
        raise SyntaxError

    def parse_whitespace_character(self, c):
        raise SyntaxError

    def parse_char(self, c):
        if not c in string.hexdigits:
            raise SyntaxError
        self.buf += c
        print self.buf
        if len(self.buf) == 4:
            print self.buf, int(self.buf), unichr(int(self.buf, 16))
            self.parser.invoke_handler_for_string_character(unichr(int(self.buf, 16)))
            self.leave_state()


class InvalidEscapeCharacter(Exception):
    pass


class EscapeCharState(ParserState):
    escape_chars = {'t': "\t", 'n': "\n", 'b': "\b", 'f': "\f",
                     'r': "\r", '/': '/', '"': '"', '\\': '\\'}

    def parse_char(self, c):
        print "esc: %s" % (c,)
        if c in self.escape_chars:
            escape_char = self.escape_chars[c]
            self.parser.invoke_handler_for_string_character(escape_char)
            self.leave_state()
        elif c == 'u':
            self.switch_state(UnicodeCodepointState)
        else:
            raise InvalidEscapeCharacter



class StringState(ParserState):
    def enter_escape_char_state(self):
        self.enter_state(EscapeCharState)

    def parse_terminal_character(self, c):
        self.parse_char(c)

    def parse_whitespace(self, c):
        self.parse_char(c)

    def parse_char(self, c):
        print c
        if c == "\\":
            self.enter_escape_char_state()
        elif c == '"':
            self.parser.invoke_handler_for_string_end()
            self.leave_state()
        else:
            self.parser.invoke_handler_for_string_character(c)
