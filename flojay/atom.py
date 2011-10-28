# true, false and null

from flojay.state import ValueState
from flojay.exception import SyntaxError


class AtomState(ValueState):
    def setUp(self, atom):
        self.pointer = 0
        self.atom = atom
        self.partial = ''

    def parse_buf(self, buf):
        self.partial += buf.take_n(len(self.atom) - len(self.partial))
        if self.partial == self.atom:
            self.parser.invoke_handler_for_atom_character(self.partial)
            self.exit_state()
        if self.partial != self.atom[0:len(self.partial)]:
            raise SyntaxError

    def invoke_end_handler(self):
        self.parser.invoke_handler_for_atom_end()

    def parse_whitespace(self, c):
        self.parse_terminal_character(c)

    def parse_char(self, c):
        if c != self.atom[self.pointer]:
            raise SyntaxError
        else:
            self.parser.invoke_handler_for_atom_character(c)
        self.pointer += 1
