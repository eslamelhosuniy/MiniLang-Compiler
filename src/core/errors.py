from src.lexer.token import Token

class LangRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token
        self.message = message

class ErrorHandler:
    had_error = False
    had_runtime_error = False

    @classmethod
    def error(cls, line: int, message: str):
        cls.report(line, "", message)

    @classmethod
    def report(cls, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        cls.had_error = True

    @classmethod
    def runtime_error(cls, error: LangRuntimeError):
        print(f"{error.message}\n[line {error.token.line}]")
        cls.had_runtime_error = True

    @classmethod
    def reset(cls):
        cls.had_error = False
        cls.had_runtime_error = False
