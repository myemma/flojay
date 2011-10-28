from flojay.state import ValueState
from flojay.exception import SyntaxError
import string

class BaseNumberState(ValueState):
    def invoke_end_handler(self):
        self.parser.invoke_handler_for_number_end()

    number_chars = set(string.digits)
    terminal_characters = set(']},' + string.whitespace)

    def parse_buf(self, buf):
        num = ''
        while(buf):
            if buf.peek() in self.terminal_characters:
                self.parser.invoke_handler_for_number_character(num)
                self.invoke_end_handler()
                self.leave_state()
                return

            c = buf.take()
            if c not in self.number_chars:
                raise SyntaxError
            num += c
        self.parser.invoke_handler_for_number_character(num)


class NumberState(BaseNumberState):

    def setUp(self):
        self.count = 0

    def enter_decimal_state(self):
        self.switch_state(DecimalState)

    def enter_exp_state(self):
        self.switch_state(ExpState)

    def parse_buf(self, buf):
        num = ''
        while(buf):
            if buf.peek() in self.terminal_characters:
                self.parser.invoke_handler_for_number_character(num)
                self.invoke_end_handler()
                self.leave_state()
                return

            c = buf.take()
            self.count += 1
            num += c

            if c == '.':
                self.parser.invoke_handler_for_number_character(num)
                self.enter_decimal_state()
                return
            elif c == 'e' or c == 'E':
                self.parser.invoke_handler_for_number_character(num)
                self.enter_exp_state()
                return
            elif c not in self.number_chars and not (c == '-' and self.count == 1):
                raise SyntaxError
            
        self.parser.invoke_handler_for_number_character(num)


class DecimalState(BaseNumberState): pass


class ExpState(NumberState):
    
    def setUp(self):
        self.count = 0

    def parse_buf(self, buf):
        num = ''
        while buf:
            if buf.peek() in self.terminal_characters:
                self.parser.invoke_handler_for_number_character(num)
                self.invoke_end_handler()
                self.leave_state()
                return

            c = buf.take()
            if (self.count == 0 and c in ['-','+']) or c in self.number_chars:
                self.count += 1
                num += c
            else:
                raise SyntaxError
        self.parser.invoke_handler_for_number_character(num)
