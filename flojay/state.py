class ParserState(object):

    def __init__(self, parser, *args):
        self.parser = parser
        self.setUp(*args)

    def setUp(self, *args):
        pass

    def switch_state(self, state_class, *args):
        self.parser.leave_state()
        self.enter_state(state_class, *args)

    def enter_state(self, state_class, *args):
        state = state_class(self.parser, *args)
        self.parser.enter_state(state)

    def leave_state(self):
        self.parser.leave_state()
