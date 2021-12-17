"""
RiscEmu (c) 2021 Anton Lydike

SPDX-License-Identifier: MIT
"""
import re
from typing import Dict, Tuple, Iterable, Callable

from helpers import Peekable
from .assembler import MemorySectionType, ParseContext, AssemblerDirectives
from .base_types import Program
from .colors import FMT_PARSE
from .exceptions import ParseException
from .tokenizer import Token, TokenType
from .types import SimpleInstruction


def parse_instruction(token: Token, args: Tuple[str], context: ParseContext):
    if context.section is None or context.section.type != MemorySectionType.Instructions:
        raise ParseException("{} {} encountered in invalid context: {}".format(token, args, context))
    ins = SimpleInstruction(token.value, args, context.context, context.section.current_address())
    context.section.data.append(ins)


def parse_label(token: Token, args: Tuple[str], context: ParseContext):
    name = token.value[:-1]
    if re.match(r'^\d+$', name):
        # relative label:
        context.context.numbered_labels[name].append(context.section.current_address())
    else:
        if name in context.context.labels:
            print(FMT_PARSE + 'Warn: Symbol {} defined twice!'.format(name))
        context.context.labels[name] = context.section.current_address()


PARSERS: Dict[TokenType, Callable[[Token, Tuple[str], ParseContext], None]] = {
    TokenType.PSEUDO_OP: AssemblerDirectives.handle_instruction,
    TokenType.LABEL: parse_label,
    TokenType.INSTRUCTION_NAME: parse_instruction
}


def parse_tokens(name: str, tokens_iter: Iterable[Token]) -> Program:
    context = ParseContext(name)

    for token, args in composite_tokenizer(Peekable[Token](tokens_iter)):
        if token.type not in PARSERS:
            raise ParseException("Unexpected token type: {}, {}".format(token, args))
        PARSERS[token.type](token, args, context)

    return context.finalize()


def composite_tokenizer(tokens_iter: Iterable[Token]) -> Iterable[Tuple[Token, Tuple[str]]]:
    tokens: Peekable[Token] = Peekable[Token](tokens_iter)

    while not tokens.is_empty():
        token = next(tokens)
        if token.type in (TokenType.PSEUDO_OP, TokenType.LABEL, TokenType.INSTRUCTION_NAME):
            yield token, tuple(take_arguments(tokens))


def take_arguments(tokens: Peekable[Token]) -> Iterable[str]:
    """
    Consumes (argument comma)* and yields argument.value until newline is reached
    If an argument is not followed by either a newline or a comma, a parse exception is raised
    The newline at the end is consumed
    :param tokens: A Peekable iterator over some Tokens
    """
    while True:
        if tokens.peek().type == TokenType.ARGUMENT:
            yield next(tokens).value
        if tokens.peek().type == TokenType.COMMA:
            next(tokens)
        elif tokens.peek().type == TokenType.NEWLINE:
            next(tokens)
            break
        raise ParseException("Expected newline, instead got {}".format(tokens.peek()))

