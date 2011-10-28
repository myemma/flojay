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
        self.buf += buf.take_n(4  - len(self.buf))
        if len(self.buf) == 4:
            self.parser.invoke_handler_for_string_character(unichr(int(self.buf, 16)))
            self.leave_state()


class InvalidEscapeCharacter(Exception):
    pass


class EscapeCharacterState(ParserState):
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
    terminals = set('"\\')

    def parse_buf(self, buf):
        while buf:
            c = buf.take_until(self.terminals)
            if c == "":
                c = buf.take()
                if c == '"':
                    self.parser.invoke_handler_for_string_end()
                    self.leave_state()
                    return
                elif c == '\\':
                    self.enter_state(EscapeCharacterState)
                    return
            else:
                self.parser.invoke_handler_for_string_character(c)
                


