from abc import ABC, abstractmethod
from typing import Any
from src.lexer.token import Token

class ExprVisitor(ABC):
    pass

class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor) -> Any:
        pass

class StmtVisitor(ABC):
    pass

class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> Any:
        pass

# ================= Expressions =================

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_binary_expr(self)

class Literal(Expr):
    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_literal_expr(self)

class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_variable_expr(self)

class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_assign_expr(self)

# ================= Statements =================

class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_expression_stmt(self)

class DisplayStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_display_stmt(self)

class DecStmt(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_dec_stmt(self)

class UntilStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_until_stmt(self)

class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_block_stmt(self)
