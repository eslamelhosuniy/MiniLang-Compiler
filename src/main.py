import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.core.errors import ErrorHandler

# --- Interpreter Mode (Commented Out) ---
# from src.interpreter.tree_walker import Interpreter
# interpreter = Interpreter()

# --- Compiler Mode ---
from src.compiler.codegen import CodeGenerator

def main():
    if len(sys.argv) > 2:
        print("Usage: python main.py [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()

def run_file(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        source_code = file.read()
    run(source_code)
    
    if ErrorHandler.had_error:
        sys.exit(65)
    if ErrorHandler.had_runtime_error:
        sys.exit(70)

def run_prompt():
    print("MiniLang Compiler REPL (Interactive Mode)")
    while True:
        try:
            line = input("#> ")
            if line.strip() == "exit":
                break
            run(line)
        except EOFError:
            break

def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    if ErrorHandler.had_error:
        ErrorHandler.reset()
        return

    parser = Parser(tokens)
    statements = parser.parse()

    if ErrorHandler.had_error:
        print("\n[Parser] Finished with syntax errors.")
        ErrorHandler.reset()
        return

    print(f"\n[Parser] Successfully parsed {len(statements)} top-level statements.")
    
    # --- Interpreter Mode (Commented Out) ---
    # interpreter.interpret(statements)
    # if ErrorHandler.had_runtime_error:
    #     print("\n[Interpreter] Finished with runtime errors.")
    #     ErrorHandler.reset()

    # --- Compiler Mode ---
    print("\n[Compiler] Generating Assembly Code (FASM)...")
    codegen = CodeGenerator()
    asm_code = codegen.generate(statements)
    
    with open("output.asm", "w", encoding="utf-8") as f:
        f.write(asm_code)
        
    print("[Compiler] Generated output.asm successfully!")
    
    print("[Compiler] Running FASM to generate output.exe...")
    fasm_path = r"fasmw17335\fasm.exe"
    import subprocess
    import os
    
    # Setup environment with correct INCLUDE path for FASM
    env = os.environ.copy()
    env["INCLUDE"] = os.path.abspath(r"fasmw17335\INCLUDE")
    
    try:
        # Compile
        subprocess.run([fasm_path, "output.asm"], env=env, check=True, capture_output=True)
        
        # Run automatically
        print("\n--- Execution Output ---")
        subprocess.run([r".\output.exe"])
        print("------------------------\n")
        
    except subprocess.CalledProcessError as e:
        print(f"[Compiler] Failed to run FASM. Error:\n{e.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"[Compiler] Execution Error: {e}")

if __name__ == "__main__":
    main()
