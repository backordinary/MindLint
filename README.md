# MindLint
## Project Structure

```
├── ast_operations.py      # AST parser and MQ-Attributes / MQ-Operations extractor
├── mindLint.py            # Core checking logic and rule definitions (IIS, IM, PE)
├── main.py                # CLI entry point for file/folder analysis
└── data/
    ├── 0/                 # Defect-free MindQuantum program samples
    └── 1/                 # Faulty MindQuantum program samples
```

------

##  Getting Started

### 1. Environment

Requires Python 3.x. No additional dependencies are needed.

```sh
python --version  # Recommended: Python 3.8+
```

### 2. Usage

```sh
# Analyze a single MindQuantum Python file
python main.py --mode 1 --path data/0/sample0.py

# Analyze all Python files in a folder (recursive)
python main.py --mode 0 --path data/1/
```

------

## Output

Results are saved in the `./result/` directory:

- If no issues are found, the report contains:

  ```
  no error or warining
  ```

- If errors or warnings are found, the report includes:

  - Rule name
  - Type: Error / Warning
  - Line number and code snippet
  - Explanation message

------

## Built-in Checkers

| Code | Name                    | Description                                               |
| ---- | ----------------------- | --------------------------------------------------------- |
| IIS  | Incorrect Initial State | Invalid back-end, non-positive qubit count, or overload   |
| IM   | Incorrect Measurement   | Reuse of measured qubits as control qubits                |
| PE   | Parameter Error         | Duplicate qubit use as both control and target, over-args |

------

## Customization

To add new rules, define a checker function in `mindLint.py` and register it in the `Rules` dictionary. No changes to the front-end (AST parser) are needed.

------

## Dataset

This project includes a manually curated dataset:

- `data/0/` contains valid, defect-free MindQuantum programs.
- `data/1/` contains faulty programs with critical errors (e.g., unexecutable logic).

You may add more samples to either folder for extended evaluation.

