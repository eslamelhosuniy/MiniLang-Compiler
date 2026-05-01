from typing import List, Any
from src.parser.ast_nodes import (
    ExprVisitor, StmtVisitor, Expr, Stmt,
    Binary, Literal, Variable, Assign,
    ExpressionStmt, DisplayStmt, DecStmt, UntilStmt, BlockStmt
)
from src.lexer.token import TokenType

class CodeGenerator(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.instructions: List[str] = []
        self.variables: set[str] = set()
        self.label_counter = 0

    def generate(self, statements: List[Stmt]) -> str:
        for stmt in statements:
            self.execute(stmt)
            
        bss_lines = []
        for var in self.variables:
            bss_lines.append(f"    {var} dd ?")
            
        bss_section = ""
        if bss_lines:
            bss_section = "section '.bss' readable writeable\n" + "\n".join(bss_lines)
            
        text_section = "\n".join(self.instructions)
        
        asm = f"""format PE console
entry start

include 'win32a.inc'

section '.data' data readable writeable
    fmt db "%d", 10, 0

{bss_section}

section '.text' code readable executable
start:
{text_section}
    invoke ExitProcess, 0

section '.idata' import data readable writeable
    library kernel32,'KERNEL32.DLL',\\
            msvcrt,'MSVCRT.DLL'

    import kernel32,\\
           ExitProcess,'ExitProcess'

    import msvcrt,\\
           printf,'printf'
"""
        return asm

    def emit(self, instruction: str):
        self.instructions.append(f"    {instruction}")

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def evaluate(self, expr: Expr):
        expr.accept(self)

    # ================= Statements =================
    
    def visit_block_stmt(self, stmt: BlockStmt):
        for s in stmt.statements:
            self.execute(s)
            
    def visit_expression_stmt(self, stmt: ExpressionStmt):
        self.evaluate(stmt.expression)
        # Pop the result of the expression to avoid stack overflow
        self.emit("pop eax")

    def visit_display_stmt(self, stmt: DisplayStmt):
        self.evaluate(stmt.expression)
        # Value to print is on top of stack
        self.emit("pop eax")
        # cinvoke automatically cleans up the stack after calling cdecl functions
        self.emit("cinvoke printf, fmt, eax")

    def visit_dec_stmt(self, stmt: DecStmt):
        var_name = stmt.name.lexeme
        self.variables.add(var_name)
        if stmt.initializer:
            self.evaluate(stmt.initializer)
            self.emit("pop eax")
            self.emit(f"mov [{var_name}], eax")
            
    def visit_until_stmt(self, stmt: UntilStmt):
        self.label_counter += 1
        loop_id = self.label_counter
        
        self.instructions.append(f"loop_start_{loop_id}:")
        self.evaluate(stmt.condition)
        self.emit("pop eax")
        self.emit("cmp eax, 0")
        # 'until' loops while condition is FALSE, so exit if TRUE (not equal to 0)
        self.emit(f"jne loop_end_{loop_id}") 
        
        self.execute(stmt.body)
        self.emit(f"jmp loop_start_{loop_id}")
        self.instructions.append(f"loop_end_{loop_id}:")

    # ================= Expressions =================
    
    def visit_literal_expr(self, expr: Literal):
        value = expr.value
        # For our basic implementation, we only handle ints and bools represented as ints
        if isinstance(value, bool):
            value = 1 if value else 0
        elif value is None:
            value = 0
        self.emit(f"push {int(value)}")
        
    def visit_variable_expr(self, expr: Variable):
        var_name = expr.name.lexeme
        self.emit(f"mov eax, [{var_name}]")
        self.emit("push eax")
        
    def visit_assign_expr(self, expr: Assign):
        var_name = expr.name.lexeme
        self.evaluate(expr.value)
        # Assignment leaves value on stack, so we peek instead of pop if we needed it,
        # but the easiest way is pop then push again.
        self.emit("pop eax")
        self.emit(f"mov [{var_name}], eax")
        self.emit("push eax")

    def visit_binary_expr(self, expr: Binary):
        self.evaluate(expr.left)
        self.evaluate(expr.right)
        
        self.emit("pop ebx") # right operand
        self.emit("pop eax") # left operand
        
        op = expr.operator.type
        if op == TokenType.PLUS:
            self.emit("add eax, ebx")
            self.emit("push eax")
        elif op == TokenType.MINUS:
            self.emit("sub eax, ebx")
            self.emit("push eax")
        elif op == TokenType.STAR:
            self.emit("imul eax, ebx")
            self.emit("push eax")
        elif op == TokenType.SLASH:
            self.emit("cdq") # sign extend eax into edx
            self.emit("idiv ebx")
            self.emit("push eax")
            
        elif op in [TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL]:
            self.emit("cmp eax, ebx")
            if op == TokenType.EQUAL_EQUAL:
                self.emit("sete al")
            elif op == TokenType.BANG_EQUAL:
                self.emit("setne al")
            elif op == TokenType.LESS:
                self.emit("setl al")
            elif op == TokenType.LESS_EQUAL:
                self.emit("setle al")
            elif op == TokenType.GREATER:
                self.emit("setg al")
            elif op == TokenType.GREATER_EQUAL:
                self.emit("setge al")
                
            self.emit("movzx eax, al") # zero extend AL to EAX
            self.emit("push eax")
