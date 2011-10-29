from flojay.state import ParserState
from flojay.exception import SyntaxError
import string


class UnicodeCodepointState(ParserState):

    hexdigits = set(string.hexdigits)

    def setUp(self):
        self.buf = ""

    def parse_buf(self, parser, buf):
        self.buf += buf.take_n(4  - len(self.buf))
        if len(self.buf) == 4:
            parser.invoke_handler_for_string_character(unichr(int(self.buf, 16)))
            parser.leave_state()


class InvalidEscapeCharacter(Exception):
    pass


escape_chars = {'t': "\t", 'n': "\n", 'b': "\b", 'f': "\f",
                'r': "\r", '/': '/', '"': '"', '\\': '\\'}


def parse_escape_chars_state(parser, buf):
    c = buf.take()
    if c in escape_chars:
        escape_char = escape_chars[c]
        parser.invoke_handler_for_string_character(escape_char)
        parser.leave_state()
    elif c == 'u':
        parser.switch_state(UnicodeCodepointState().parse_buf)
    else:
        raise InvalidEscapeCharacter


terminals = set('"\\')

def parse_string_state(parser, buf):
    c = buf.take_until(terminals)
    if c == "":
        c = buf.take()
        if c == '"':
            parser.invoke_handler_for_string_end()
            parser.leave_state()
        elif c == '\\':
            parser.enter_state(parse_escape_chars_state)
    else:
        parser.invoke_handler_for_string_character(c)
