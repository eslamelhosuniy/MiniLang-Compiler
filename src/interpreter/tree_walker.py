from typing import Any, List
from src.parser.ast_nodes import (
    ExprVisitor, StmtVisitor, Expr, Stmt,
    Binary, Literal, Variable, Assign,
    ExpressionStmt, DisplayStmt, DecStmt, UntilStmt, BlockStmt
)
from src.lexer.token import TokenType, Token
from src.interpreter.environment import Environment
from src.core.errors import LangRuntimeError

class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.environment = Environment()

    def interpret(self, statements: List[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except LangRuntimeError as error:
            from src.core.errors import ErrorHandler
            ErrorHandler.runtime_error(error)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)
        
    def execute_block(self, statements: List[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    # ================= Statements =================

    def visit_block_stmt(self, stmt: BlockStmt):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_expression_stmt(self, stmt: ExpressionStmt):
        self.evaluate(stmt.expression)
        return None

    def visit_display_stmt(self, stmt: DisplayStmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_dec_stmt(self, stmt: DecStmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_until_stmt(self, stmt: UntilStmt):
        # "until" executes its body while the condition is FALSE.
        while not self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    # ================= Expressions =================

    def visit_literal_expr(self, expr: Literal) -> Any:
        return expr.value

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self.environment.get(expr.name)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr: Binary) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        op_type = expr.operator.type

        if op_type == TokenType.PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise LangRuntimeError(expr.operator, "Operands must be two numbers or two strings.")
            
        elif op_type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return left - right
            
        elif op_type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            if right == 0:
                raise LangRuntimeError(expr.operator, "Division by zero.")
            return left / right
            
        elif op_type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return left * right
            
        elif op_type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return left > right
            
        elif op_type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left >= right
            
        elif op_type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return left < right
            
        elif op_type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left <= right
            
        elif op_type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
            
        elif op_type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        return None

    # ================= Utilities =================

    def is_truthy(self, obj: Any) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, (int, float)):
            return
        raise LangRuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise LangRuntimeError(operator, "Operands must be numbers.")

    def stringify(self, obj: Any) -> str:
        if obj is None:
            return "nil"
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(obj)
