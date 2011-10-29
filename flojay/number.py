from flojay.state import ParserState
from flojay.exception import SyntaxError
import string

number_chars = set(string.digits)
terminal_characters = set(']},' + string.whitespace)

def parse_base_number_state(parser, buf):
    num = buf.take_while(number_chars)
    if num == '':
        num = buf.peek()
        if num in terminal_characters:
            parser.invoke_handler_for_number_end()
            parser.leave_state()
        else:
            raise SyntaxError
    else:
        parser.invoke_handler_for_number_character(num)
        parser.invoke_handler_for_number_end()
        parser.leave_state()


def parse_number_sign_state(parser, buf):
    buf.take()
    parser.invoke_handler_for_number_character('-')
    parser.switch_state(parse_number_state)

def parse_number_state(parser, buf):
    num = buf.take_while(number_chars)
    if num == "":
        num = buf.peek()
        if num in terminal_characters:
            parser.invoke_handler_for_number_end()
            parser.leave_state()
        elif num == '.':
            buf.take()
            parser.invoke_handler_for_number_character(num)
            parser.switch_state(parse_base_number_state)
        elif num == 'e' or num == 'E':
            buf.take()
            parser.invoke_handler_for_number_character(num)
            parser.switch_state(parse_exp_sign_state)
        else:
            raise SyntaxError
    else:
        parser.invoke_handler_for_number_character(num)


def parse_exp_sign_state(parser, buf):
    c = buf.peek()
    if c in '-+':
        buf.take()
        parser.invoke_handler_for_number_character(c)
    parser.switch_state(parse_base_number_state)
