# MiniLang Compiler

MiniLang is a custom, fully functional compiler and interpreter built entirely in Python from scratch. It parses a minimalistic custom programming language and compiles it Ahead-Of-Time (AOT) into native **x86 Assembly**, which is then automatically assembled into a standalone Windows Executable (`.exe`) using FASM (Flat Assembler).

The project was designed with clean architecture principles in mind, utilizing the classic compiler pipeline and the **Visitor Design Pattern** to ensure high extensibility.

---

## Key Features

- **Dual Execution Modes:** 
  - **AOT Compiler:** Translates code into pure x86 Assembly (`output.asm`) and uses FASM to generate a native `.exe`.
  - **Tree-Walk Interpreter:** Evaluates the Abstract Syntax Tree (AST) directly in Python at runtime (accessible via the interactive REPL or by modifying `main.py`).
- **Custom Syntax:** Uses unique keywords like `dec` (declare), `display` (print), and `until` (loop while false).
- **Lexical Scoping:** Proper handling of variable scopes, enabling localized variables and nested blocks.
- **Robust Error Handling:** Precise reporting for Lexical, Syntax, and Runtime/Semantic errors with line tracking.

---

## Language Syntax

The language is designed to be simple and intuitive. Currently, it supports integer arithmetic, boolean logic, variables, conditional loops, and console output.

### Example Code (`test_code.lang`)
```javascript
// Variable Declaration
dec limit = 10;
dec n = 1;

// Loop until 'n == limit' becomes true
until (n == limit) {
    display n;      // Print to console
    n = n + 1;      // Assignment and arithmetic
}
```

---

## Architecture & Workflow

The compiler follows a classic multi-pass architecture. Here is the step-by-step workflow of how source code is transformed into a native executable:

### 1. Lexical Analysis (`src/lexer/scanner.py`)
- **Input:** Raw source code string.
- **Process:** The Scanner reads the code character by character, discarding whitespace, and groups characters into meaningful **Tokens** (e.g., `DEC`, `IDENTIFIER`, `NUMBER`, `PLUS`).
- **Output:** A list of `Token` objects.

### 2. Syntax Analysis (`src/parser/parser.py`)
- **Input:** The list of `Token`s.
- **Process:** A Recursive Descent Parser processes the tokens based on defined grammar rules (EBNF). It constructs an **Abstract Syntax Tree (AST)** composed of Expression (`Expr`) and Statement (`Stmt`) nodes.
- **Output:** An AST representing the structural flow of the program.

### 3. Code Generation (AOT Compiler) (`src/compiler/codegen.py`)
- **Input:** The AST.
- **Process:** The `CodeGenerator` traverses the AST using the Visitor Pattern. Instead of executing the nodes, it emits equivalent **x86 Assembly instructions (FASM syntax)**.
  - Variables are dynamically allocated in the `.bss` section.
  - Arithmetic is handled via the CPU Stack (`push`, `pop`, `add`).
  - System output relies on Windows C-runtime DLLs (`cinvoke printf`).
- **Output:** A pure assembly file (`output.asm`).

### 4. Assembling (`FASM`)
- **Input:** `output.asm`.
- **Process:** Python automatically invokes the FASM (Flat Assembler) executable via `subprocess`. FASM natively compiles and links the assembly code without the need for GCC.
- **Output:** A tiny, incredibly fast native Windows executable (`output.exe`).

*(Note: The project also contains an `Interpreter` inside `src/interpreter/tree_walker.py` which can evaluate the AST dynamically instead of generating Assembly. This is useful for debugging and REPL environments).*

---

## Project Structure

```text
d:\Compiler\
├── examples\
│   └── test_code.lang          # Example source code written in MiniLang
├── src\
│   ├── main.py                 # Application entry point and pipeline coordinator
│   ├── core\
│   │   └── errors.py           # Global error handling and reporting
│   ├── lexer\
│   │   ├── scanner.py          # Lexical Analyzer (String -> Tokens)
│   │   └── token.py            # Token definitions and Keyword mapping
│   ├── parser\
│   │   ├── ast_nodes.py        # AST Data Classes and Visitor Interfaces
│   │   └── parser.py           # Recursive Descent Parser (Tokens -> AST)
│   ├── compiler\
│   │   └── codegen.py          # AOT Backend: Generates x86 Assembly
│   └── interpreter\
│       ├── environment.py      # Lexical Scope and Symbol Table manager
│       └── tree_walker.py      # Dynamic Tree-Walk execution engine
├── fasmw17335\                 # FASM Windows binaries (Required for Compilation)
└── README.md                   # Project Documentation
```

---

## Prerequisites & Installation

1. **Python 3.10+**: Ensure Python is installed on your system.
2. **FASM (Flat Assembler)**: 
   - Ensure the `fasmw17335` directory is present in the project root, or update the `fasm_path` variable inside `src/main.py` to point to your `fasm.exe` location.
   - You can download it from flatassembler.net.

---

## Usage

### Compile and Run a File
To compile a MiniLang script into a `.exe`:
```bash
python src/main.py examples/test_code.lang
```
If successful, the compiler will generate an `output.asm` file and invoke FASM to generate `output.exe`.
You can then run the executable natively:
```bash
.\output.exe
```

### Interactive Mode (REPL)
Run the script without arguments to enter the Interactive REPL (Currently configured for Compiler mode testing, but easily adaptable to the Interpreter):
```bash
python src/main.py
```

---

## Extensibility
The use of the Visitor Pattern makes adding new features incredibly simple:
1. **New Syntax:** Add a new AST Node class in `ast_nodes.py`.
2. **Parsing:** Add the parsing rule in `parser.py`.
3. **Execution/Compilation:** Implement the corresponding `visit_*` method in `codegen.py` (and `tree_walker.py` if maintaining the interpreter).
