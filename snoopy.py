#!/usr/bin/env python3
# snoopy.py
from __future__ import annotations
import os
import sys
import argparse
import ast
import csv
import re
from pathlib import Path
import subprocess

lookup = {}

def load_license_lookup(csv_path="pythonLicenses.csv"):
    global __Version__ 

    dict_of_dicts = {}
    with open('pythonLicenses.csv', mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            dict_of_dicts[row['package']] = row
    return dict_of_dicts


def summarize_imports(import_dict, makefile_suggestions=None):
    # summarize the imports I have used
    print("=== 🐍 Package or file dependencies ===")
    for file, imports in import_dict.items():
        suffix = Path(file).suffix

        # Handle Python and Jupyter files
        if suffix in [".py", ".ipynb"]:
            print(f"📄 {file}")
            for imp in sorted(imports):
                impStr = str(imp.split('.')[0]).lower()
                try:
                    license_info = lookup[impStr]['license'] # <-- your original license lookup logic
                except:
                    print(f"  {imp}  {impStr}")

        elif suffix in [".c", ".cpp"]:
            print(f"📄 {file}")
            
            flat_imports = []
            for imp in imports:
                if isinstance(imp, list):
                    flat_imports.extend(imp)
                else:
                    flat_imports.append(imp)
        
            for header in sorted(flat_imports):
                print(f"  #include <{header}>")
        
            if makefile_suggestions and file in makefile_suggestions:
                print("\n🛠 Suggested Makefile:\n")
                print(makefile_suggestions[file])
        
        else:
            print(f"📄 {file}")
            print("  ❓ Unknown file type — skipped")

    # make suggestions for requirements.txt (only for Python files)
    all_deps = sorted({imp for file, deps in import_dict.items()
                       if Path(file).suffix in [".py", ".ipynb"]
                       for imp in deps})
    if all_deps:
        print("\n📦 Suggested requirements.txt:")
        for dep in all_deps:
            print(dep)

def parse_python_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=filepath)
    return sorted({n.name.split('.')[0]  for n in ast.walk(node) if isinstance(n, ast.Import) for n in n.names} |
                  {n.module.split('.')[0]  for n in ast.walk(node) if isinstance(n, ast.ImportFrom) and n.module})

def parse_ipynb_file(filepath):
    try:
        import nbformat
    except ImportError:
        print("nbformat not installed, skipping notebook parsing.")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    imports = set()
    for cell in nb.cells:
        if cell.cell_type == "code":
            try:
                node = ast.parse(cell.source)
                imports |= {n.name.split('.')[0]  for n in ast.walk(node) if isinstance(n, ast.Import) for n in n.names}
                imports |= {n.module.split('.')[0]  for n in ast.walk(node) if isinstance(n, ast.ImportFrom) and n.module}
            except:
                pass
    return sorted(imports)

    return sorted(includes)

def parse_c_cpp_file(filepath):
    """
    Parses a C++ source or header file to extract included headers and suggest a Makefile.

    Returns:
        includes: List of included headers (standard or local)
        makefile_suggestion: String with Makefile boilerplate if it's a .cpp file
    """
    includes = []
    makefile_suggestion = None
    filename = Path(filepath).name
    base_name = filename.replace(".cpp", "")

    try:
        with open(filepath, "r") as f:
            lines = f.readlines()

        for line in lines:
            match = re.match(r'^\s*#include\s+[<"](.*?)[">]', line)
            if match:
                includes.append(match.group(1))

        # Only generate Makefile for .cpp files (not headers)
        if str(filepath).endswith(".cpp"):
            makefile_suggestion = f"""# Makefile

CXX = g++
CXXFLAGS = -Wall -O2
LDFLAGS = -lblas
TARGET = {base_name}
OBJS = {base_name}.o

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
\t$(CXX) -o $@ $^ $(LDFLAGS)

%.o: %.cpp
\t$(CXX) $(CXXFLAGS) -c $<

clean:
\trm -f $(TARGET) $(OBJS)
"""

    except Exception as e:
        print(f"Error parsing {filepath}: {e}")

    return includes, makefile_suggestion



def snoopy_entry_point(path):
    global lookup 
    print(f"snoopy_entry_point is running ...")
    lookup = load_license_lookup(csv_path="pythonLicenses.csv")
    all_imports = {}

    path = Path(path)
    if path.is_file():
        # Handle a single file
        ext = path.suffix
        print(f"snoopy_entry_pointext  {ext}")
        print("(*** Bob: ", ext)
        if ext == ".py":
            imports = parse_python_file(path)
            all_imports[str(path)] = imports
        elif ext == ".ipynb":
            imports = parse_ipynb_file(path)
            all_imports[str(path)] = imports
        elif ext in [".c", ".cpp", ".h"]:
            print("got to if cpp")
            imports = parse_c_cpp_file(path)
            all_imports[str(path)] = imports
        else:
            print(f"⚠️ Unsupported file type: {ext}")
    else:
        # Handle a directory
        for file in path.rglob("*"):
            if file.suffix == ".py":
                imports = parse_python_file(file)
                all_imports[str(file)] = imports
            elif file.suffix == ".ipynb":
                imports = parse_ipynb_file(file)
                all_imports[str(file)] = imports
            elif file.suffix in [".c", ".cpp", ".h"]:
                print("got to else cpp")
                imports = parse_c_cpp_file(file)
                all_imports[str(file)] = imports

    summarize_imports(all_imports)
    
import argparse

DEFAULT_CSV_NAME = "pythonLicenses.csv"

def parse_args():
    p = argparse.ArgumentParser(
        prog="snoopy",
        description="Dependency and license finder for .py/.ipynb (and friends).",
    )
    p.add_argument(
        "--csv", metavar="FILE",
        help="Full path to licenses CSV (overrides everything)."
    )
    p.add_argument(
        "--license-dir", metavar="DIR",
        help=f"Directory containing {DEFAULT_CSV_NAME}."
    )
    p.add_argument(
        "targets", nargs="*", default=["."],
        help="Files/dirs to scan (default: current directory)"
    )
    return p.parse_args()

from pathlib import Path

DEFAULT_CSV_NAME = "pythonLicenses.csv"  # keep consistent with parse_args above

def resolve_csv_from_args(args) -> Path:
    # 1) --csv FILE wins if provided
    if args.csv:
        return Path(args.csv).expanduser().resolve()

    # 2) --license-dir DIR -> DIR/pythonLicenses.csv
    if args.license_dir:
        return (Path(args.license_dir).expanduser().resolve() / DEFAULT_CSV_NAME)

    # 3) Fallback: next to this script
    return Path(__file__).resolve().parent / DEFAULT_CSV_NAME



def resolve_data_csv(args, name="pythonLicenses.csv") -> Path:
    """Resolve CSV by priority: CLI file > CLI dir > env file > env dir > fallback."""
    # 1) CLI file
    if args.csv_path:
        return Path(args.csv_path)

    # 2) CLI dir
    if args.data_dir:
        return Path(args.data_dir) / name

    # 3) Env vars
    env_file = os.environ.get("SNOOPY_CSV_PATH")
    if env_file:
        return Path(env_file)

    env_dir = os.environ.get("SNOOPY_DATA_DIR")
    if env_dir:
        return Path(env_dir) / name

    # 4) Fallback near this file (repo layout)
    here = Path(__file__).resolve().parent
    # Adjust if your file lives elsewhere
    return here / "data" / name

def main():
    args = parse_args()
    csv_path = resolve_csv_from_args(args)

    if not csv_path.exists():
        print(f"[snoopy] CSV not found: {csv_path}", file=sys.stderr)
        print("Tip: use --csv FILE or --license-dir DIR (which must contain pythonLicenses.csv).", file=sys.stderr)
        sys.exit(2)

    print("Snoopy is running...")

    # If you already had: lookup = load_license_lookup(csv_path="pythonLicenses.csv")
    # change it to:
    lookup = load_license_lookup(csv_path=str(csv_path))

    # Do NOT change your snoopy_entry_point signature if it didn't accept extra args
    for t in (args.targets or ["."]):
        snoopy_entry_point(str(Path(t).resolve()))


if __name__ == "__main__":
    main()









