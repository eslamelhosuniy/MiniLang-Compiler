from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()

    # One or two character tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()

    # Keywords (Customized!)
    DEC = auto()      # let / var
    DISPLAY = auto()  # print
    UNTIL = auto()    # loop until condition is true
    IF = auto()
    ELSE = auto()
    TRUE = auto()
    FALSE = auto()

    EOF = auto()

# Map of string keywords to their TokenType
KEYWORDS = {
    "dec": TokenType.DEC,
    "display": TokenType.DISPLAY,
    "until": TokenType.UNTIL,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}

@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __str__(self):
        return f"{self.type.name} {self.lexeme} {self.literal}"
