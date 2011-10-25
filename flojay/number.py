from flojay.state import ValueState
from flojay.exception import SyntaxError
import string


class NumberState(ValueState):
    number_chars = string.digits

    def setUp(self):
        self.count = 0

    def invoke_end_handler(self):
        self.parser.invoke_handler_for_number_end()

    def enter_decimal_state(self):
        self.enter_state(DecimalState)

    def enter_exp_state(self):
        self.enter_state(ExpState)

    def parse_char(self, c):
        if c == '.':
            self.parser.invoke_handler_for_number_character(c)
            self.enter_decimal_state()
        elif c == 'e' or c == 'E':
            self.parser.invoke_handler_for_number_character(c)
            self.enter_exp_state()
        elif c in self.number_chars or (c == '-' and self.count == 0):
            self.parser.invoke_handler_for_number_character(c)
            self.count += 1
        else:
            raise SyntaxError


class DecimalState(NumberState):
    def parse_char(self, c):
        if c not in string.digits:
            raise SyntaxError
        self.parser.invoke_handler_for_number_character(c)


class ExpState(NumberState):
    def setUp(self):
        self.character_count = 0

    def parse_char(self, c):
        if (self.character_count == 0 and c in ['-', '+']) or \
                c in string.digits:
            self.parser.invoke_handler_for_number_character(c)
            self.character_count += 1
        else:
            raise SyntaxError
