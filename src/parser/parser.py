from src.lexer.token import Token, TokenType
from src.parser.ast_nodes import *
from src.core.errors import ErrorHandler

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[Stmt]:
        statements = []
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        return statements

    # --- Statements ---
    
    def declaration(self) -> Stmt | None:
        try:
            if self.match(TokenType.DEC):
                return self.dec_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def dec_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return DecStmt(name, initializer)

    def statement(self) -> Stmt:
        if self.match(TokenType.DISPLAY):
            return self.display_statement()
        if self.match(TokenType.UNTIL):
            return self.until_statement()
        if self.match(TokenType.LEFT_BRACE):
            return BlockStmt(self.block())
        return self.expression_statement()

    def display_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return DisplayStmt(value)

    def until_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'until'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return UntilStmt(condition, body)

    def block(self) -> list[Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expr)

    # --- Expressions ---

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.primary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.primary()
            expr = Binary(expr, operator, right)

        return expr

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NUMBER): return Literal(self.previous().literal)
        if self.match(TokenType.IDENTIFIER): return Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr

        raise self.error(self.peek(), "Expect expression.")

    # --- Helper Methods ---

    def match(self, *types: TokenType) -> bool:
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False

    def check(self, type_: TokenType) -> bool:
        if self.is_at_end(): return False
        return self.peek().type == type_

    def advance(self) -> Token:
        if not self.is_at_end(): self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_): return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        if token.type == TokenType.EOF:
            ErrorHandler.report(token.line, " at end", message)
        else:
            ErrorHandler.report(token.line, f" at '{token.lexeme}'", message)
        return ParseError()

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON: return

            if self.peek().type in [TokenType.DEC, TokenType.DISPLAY, TokenType.UNTIL, TokenType.IF]:
                return

            self.advance()
