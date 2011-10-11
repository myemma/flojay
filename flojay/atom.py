# true, false and null

from flojay.state import ValueState
from flojay.exception import SyntaxError


class AtomState(ValueState):
    def setUp(self, atom):
        self.pointer = 0
        self.atom = atom

    def invoke_end_handler(self):
        self.parser.invoke_handler_for_atom_end()

    def parse_char(self, c):
        if c != self.atom[self.pointer]:
            raise SyntaxError
        else:
            self.parser.invoke_handler_for_atom_character(c)
        self.pointer += 1
