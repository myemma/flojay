from flojay.state import ParserState
from flojay.exception import SyntaxError
import string


class NotImplementedException(Exception):
    pass


class UnicodeCodepointState(ParserState):

    hexdigits = set(string.hexdigits)

    def setUp(self):
        self.buf = ""

    def parse_buf(self, buf):
        self.buf += buf.take(4  - len(self.buf))
        if len(self.buf) == 4:
            self.parser.invoke_handler_for_string_character(unichr(int(self.buf, 16)))
            self.leave_state()


class InvalidEscapeCharacter(Exception):
    pass


class EscapeCharState(ParserState):
    escape_chars = {'t': "\t", 'n': "\n", 'b': "\b", 'f': "\f",
                     'r': "\r", '/': '/', '"': '"', '\\': '\\'}

    def parse_buf(self, buf):
        c = buf.take()
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

    def parse_buf(self, buf):
        chars = ''
        while buf:
            c = buf.take()
            if c == '\\':
                self.parser.invoke_handler_for_string_character(chars)
                self.enter_escape_char_state()
                return
            elif c == '"':
                self.parser.invoke_handler_for_string_character(chars)
                self.parser.invoke_handler_for_string_end()
                self.leave_state()
                return
            else:
                chars += c
        self.parser.invoke_handler_for_string_character(chars)
