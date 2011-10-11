class ParserState(object):
    def __init__(self, parser, *args):
        self.parser = parser
        self.setUp(*args)

    def setUp(self, *args):
        pass

    def handle_begin(self):
        pass

    def handle_end(self):
        pass

    def parse_whitespace_character(self, c):
        self.parser.invoke_handler_for_whitespace_character(c)

    def enter_state(self, state_class, *args):
        state = state_class(self.parser, *args)
        self.parser.enter_state(state)

    def leave_state(self):
        self.parser.leave_state()


class ValueState(ParserState):

    def parse_terminal_character(self, c):
        self.leave_state()
        self.invoke_end_handler()
        self.parser.parse_char(c)

    def parse_whitespace_character(self, c):
        self.parse_teriminal_character(c)
