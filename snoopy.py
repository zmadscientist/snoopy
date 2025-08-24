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

# ------------------------
# CSV LOADING / ARG PARSE
# ------------------------

DEFAULT_CSV_NAME = "pythonLicenses.csv"

def load_license_lookup(csv_path: str = DEFAULT_CSV_NAME):
    """
    Load the license CSV into a dict-of-dicts keyed by 'package'.
    Honors the csv_path passed in.
    """
    csv_path = Path(csv_path).expanduser().resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"License CSV not found: {csv_path}")

    dict_of_dicts = {}
    with csv_path.open(mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            pkg = (row.get('package') or '').strip()
            if pkg:
                dict_of_dicts[pkg.lower()] = row  # normalize key to lower
    return dict_of_dicts


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



def resolve_csv_from_args(args) -> Path:
    # 1) --csv FILE wins if provided
    if args.csv:
        return Path(args.csv).expanduser().resolve()

    # 2) --license-dir DIR -> DIR/pythonLicenses.csv
    if args.license_dir:
        return (Path(args.license_dir).expanduser().resolve() / DEFAULT_CSV_NAME)

    # 3) Look in a "licenses" subdir next to snoopy.py
    candidate = Path(__file__).resolve().parent / "licenses" / DEFAULT_CSV_NAME
    if candidate.exists():
        return candidate

    # 4) Fallback: next to snoopy.py
    return Path(__file__).resolve().parent / DEFAULT_CSV_NAME

# ------------------------
# PARSERS
# ------------------------

def parse_python_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=filepath)
    return sorted(
        {n.name.split('.')[0] for n in ast.walk(node) if isinstance(n, ast.Import) for n in n.names}
        |
        {n.module.split('.')[0] for n in ast.walk(node) if isinstance(n, ast.ImportFrom) and n.module}
    )

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
                imports |= {n.name.split('.')[0] for n in ast.walk(node) if isinstance(n, ast.Import) for n in n.names}
                imports |= {n.module.split('.')[0] for n in ast.walk(node) if isinstance(n, ast.ImportFrom) and n.module}
            except Exception:
                pass
    return sorted(imports)

def parse_c_cpp_file(filepath):
    """
    Parses a C/C++ source or header file to extract included headers and suggest a Makefile.

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


# ------------------------
# REPORTING
# ------------------------

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
                    license_info = lookup.get(impStr, {}).get('license')
                    if license_info:
                        print(f"  {imp} — {license_info}")
                    else:
                        print(f"  {imp}")
                except Exception:
                    print(f"  {imp}")

        elif suffix in [".c", ".cpp"]:
            print(f"📄 {file}")

            # imports may be a list (includes) OR a tuple (includes, mkfile) if caller didn't flatten
            flat_imports = []
            if isinstance(imports, tuple):
                flat, _ = imports
                imports = flat
            for imp in imports:
                if isinstance(imp, list):
                    flat_imports.extend(imp)
                else:
                    flat_imports.append(imp)

            for header in sorted(flat_imports):
                print(f"  #include <{header}>")

            if makefile_suggestions and file in makefile_suggestions and makefile_suggestions[file]:
                print("\n🛠 Suggested Makefile:\n")
                print(makefile_suggestions[file])

        else:
            print(f"📄 {file}")
            print("  ❓ Unknown file type — skipped")

    # make suggestions for requirements.txt (only for Python files)
    all_deps = sorted({
        imp for file, deps in import_dict.items()
        if Path(file).suffix in [".py", ".ipynb"]
        for imp in deps
    })
    if all_deps:
        print("\n📦 Suggested requirements.txt:")
        for dep in all_deps:
            print(dep)


# ------------------------
# DRIVER
# ------------------------

def snoopy_entry_point(path):
    """
    Scans a file or directory. Relies on the global `lookup` already loaded in `main()`.
    """
    print("snoopy_entry_point is running ...")
    all_imports = {}
    makefile_suggestions = {}

    path = Path(path)
    if path.is_file():
        ext = path.suffix.lower()
        if ext == ".py":
            imports = parse_python_file(path)
            all_imports[str(path)] = imports
        elif ext == ".ipynb":
            imports = parse_ipynb_file(path)
            all_imports[str(path)] = imports
        elif ext in [".c", ".cpp", ".h"]:
            includes, mk = parse_c_cpp_file(path)
            all_imports[str(path)] = includes
            if mk:
                makefile_suggestions[str(path)] = mk
        else:
            print(f"⚠️ Unsupported file type: {ext}")
    else:
        # directory walk
        for file in path.rglob("*"):
            ext = file.suffix.lower()
            if ext == ".py":
                imports = parse_python_file(file)
                all_imports[str(file)] = imports
            elif ext == ".ipynb":
                imports = parse_ipynb_file(file)
                all_imports[str(file)] = imports
            elif ext in [".c", ".cpp", ".h"]:
                includes, mk = parse_c_cpp_file(file)
                all_imports[str(file)] = includes
                if mk:
                    makefile_suggestions[str(file)] = mk

    summarize_imports(all_imports, makefile_suggestions=makefile_suggestions)


def main():
    global lookup

    args = parse_args()
    csv_path = resolve_csv_from_args(args)

    if not csv_path.exists():
        print(f"[snoopy] CSV not found: {csv_path}", file=sys.stderr)
        print("Tip: use --csv FILE or --license-dir DIR (which must contain pythonLicenses.csv).", file=sys.stderr)
        sys.exit(2)

    print("Snoopy is running...")

    # Load CSV once into global lookup for the run
    lookup = load_license_lookup(csv_path=str(csv_path))

    # Scan each target
    for t in (args.targets or ["."]):
        snoopy_entry_point(str(Path(t).resolve()))


if __name__ == "__main__":
    main()
