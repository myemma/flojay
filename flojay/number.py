from flojay.state import ParserState
from flojay.exception import SyntaxError
import string

class BaseNumberState(ParserState):

    number_chars = set(string.digits)
    terminal_characters = set(']},' + string.whitespace)

    def parse_buf(self, parser, buf):
        num = buf.take_while(self.number_chars)
        if num == '':
            num = buf.peek()
            if num in self.terminal_characters:
                parser.invoke_handler_for_number_end()
                parser.leave_state()
            else:
                raise SyntaxError
        else:
            parser.invoke_handler_for_number_character(num)
            parser.invoke_handler_for_number_end()
            parser.leave_state()


class NumberSignState(ParserState):
    def parse_buf(self, parser, buf):
        buf.take()
        parser.invoke_handler_for_number_character('-')
        parser.switch_state(NumberState)


class NumberState(BaseNumberState):

    def parse_buf(self, parser, buf):
        num = buf.take_while(self.number_chars)
        if num == "":
            num = buf.peek()
            if num in self.terminal_characters:
                parser.invoke_handler_for_number_end()
                parser.leave_state()
            elif num == '.':
                buf.take()
                parser.invoke_handler_for_number_character(num)
                parser.switch_state(BaseNumberState)
            elif num == 'e' or num == 'E':
                buf.take()
                parser.invoke_handler_for_number_character(num)
                parser.switch_state(ExpSignState)
            else:
                raise SyntaxError
        else:
            parser.invoke_handler_for_number_character(num)


class ExpSignState(ParserState):
    def parse_buf(self, parser, buf):
        c = buf.peek()
        if c in '-+':
            buf.take()
            parser.invoke_handler_for_number_character(c)
        parser.switch_state(BaseNumberState)
