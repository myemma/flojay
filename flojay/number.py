from flojay.state import ValueState
from flojay.exception import SyntaxError
import string

class BaseNumberState(ValueState):

    number_chars = set(string.digits)
    terminal_characters = set(']},' + string.whitespace)

    def invoke_end_handler(self):
        self.parser.invoke_handler_for_number_end()

    def parse_buf(self, buf):
        num = buf.take_while(self.number_chars)
        if num == '':
            num = buf.peek()
            if num in self.terminal_characters:
                self.invoke_end_handler()
                self.leave_state()
            else:
                raise SyntaxError
        else:
            self.parser.invoke_handler_for_number_character(num)
            self.invoke_end_handler()
            self.leave_state()


class NumberSignState(ValueState):
    def parse_buf(self, buf):
        buf.take()
        self.parser.invoke_handler_for_number_character('-')
        self.switch_state(NumberState)


class NumberState(BaseNumberState):
    def enter_decimal_state(self):
        self.switch_state(BaseNumberState)

    def enter_exp_state(self):
        self.switch_state(BaseNumberState)

    def enter_exp_sign_state(self):
        self.switch_state(ExpSignState)

    def parse_buf(self, buf):
        num = buf.take_while(self.number_chars)
        if num == "":
            num = buf.peek()
            if num in self.terminal_characters:
                self.invoke_end_handler()
                self.leave_state()
            elif num == '.':
                buf.take()
                self.parser.invoke_handler_for_number_character(num)
                self.enter_decimal_state()
            elif num == 'e' or num == 'E':
                buf.take()
                self.parser.invoke_handler_for_number_character(num)
                self.enter_exp_sign_state()
            else:
                raise SyntaxError
        else:
            self.parser.invoke_handler_for_number_character(num)


class ExpSignState(ValueState):
    def parse_buf(self, buf):
        c = buf.peek()
        if c in '-+':
            buf.take()
            self.parser.invoke_handler_for_number_character(c)
        self.switch_state(BaseNumberState)
