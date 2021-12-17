from unittest import TestCase

from riscemu.tokenizer import tokenize, print_tokens, Token, TokenType, NEWLINE, COMMA


def ins(name: str) -> Token:
    return Token(TokenType.INSTRUCTION_NAME, name)


def arg(name: str) -> Token:
    return Token(TokenType.ARGUMENT, name)


def op(name: str) -> Token:
    return Token(TokenType.PSEUDO_OP, name)


def lbl(name: str) -> Token:
    return Token(TokenType.LABEL, name)


class Test(TestCase):

    def test_instructions(self):
        program = [
            'li     a0, 144',
            'divi   a0, a0, 12',
            'xori   a1, a0, 12'
        ]
        tokens = [
            ins('li'), arg('a0'), COMMA, arg('144'), NEWLINE,
            ins('divi'), arg('a0'), COMMA, arg('a0'), COMMA, arg('12'), NEWLINE,
            ins('xori'), arg('a1'), COMMA, arg('a0'), COMMA, arg('12'), NEWLINE,
        ]
        self.assertEqual(list(tokenize(program)), tokens)

    def test_comments(self):
        parsed_res = [
            ins('li'), arg('a0'), COMMA, arg('144'), NEWLINE
        ]
        for c in ('#', '//', ';'):
            lines = [
                c + ' this is a comment',
                'li a0, 144'
            ]
            self.assertEqual(list(tokenize(lines)), parsed_res)

    def test_pseudo_ins(self):
        parsed_res = [
            Token(TokenType.PSEUDO_OP, '.section'), Token(TokenType.ARGUMENT, '.text'), NEWLINE,
            Token(TokenType.PSEUDO_OP, '.type'), Token(TokenType.ARGUMENT, 'init'), COMMA,
            Token(TokenType.ARGUMENT, '@function'), NEWLINE
        ]
        input_program = [
            '.section .text',
            '.type init, @function'
        ]
        self.assertEqual(list(tokenize(input_program)), parsed_res)

    def test_full_program(self):
        program = """
# a hashtag comment

; semicolon comment followed by an empty line
.section .text
// double slash comment
    addi sp, sp, -32
    sw   s0, 0(ra)
section:
    sub  s0, s0, s0
"""
        tokens = [
            op('.section'), arg('.text'), NEWLINE,
            ins('addi'), arg('sp'), COMMA, arg('sp'), COMMA, arg('-32'), NEWLINE,
            ins('sw'), arg('s0'), COMMA, arg('ra'), arg('0'), NEWLINE,
            lbl('section:'), NEWLINE,
            ins('sub'), arg('s0'), COMMA, arg('s0'), COMMA, arg('s0'), NEWLINE
        ]

        self.assertEqual(list(tokenize(program.splitlines())), tokens)

