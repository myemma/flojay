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

    def switch_state(self, state_class, *args):
        self.leave_state()
        self.enter_state(state_class, *args)

    def enter_state(self, state_class, *args):
        state = state_class(self.parser, *args)
        self.parser.enter_state(state)

    def leave_state(self):
        self.parser.leave_state()

    def reparse_char(self, c):
        self.parser.parse_char(c)


class ValueState(ParserState):

    def parse_terminal_character(self, c):
        self.leave_state()
        self.invoke_end_handler()
        self.parser.parse_char(c)
