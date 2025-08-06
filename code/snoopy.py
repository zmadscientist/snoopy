#!/usr/bin/env python3

import os
import re
import sys
import ast
import nbformat
import importlib.util
from pathlib import Path
from collections import defaultdict

STATIC_LICENSE_MAP = {
    "numpy": ("BSD-3-Clause", "https://spdx.org/licenses/BSD-3-Clause.html"),
    "scipy": ("BSD-3-Clause", "https://spdx.org/licenses/BSD-3-Clause.html"),
    "matplotlib": ("PSF", "https://spdx.org/licenses/PSF-2.0.html"),
    "pandas": ("BSD-3-Clause", "https://spdx.org/licenses/BSD-3-Clause.html"),
    "requests": ("Apache-2.0", "https://spdx.org/licenses/Apache-2.0.html"),
    "bark": ("Unknown", ""),
}

def get_package_license(package_name):
    return STATIC_LICENSE_MAP.get(package_name.lower(), ("Unknown", ""))

def is_std_lib(module_name):
    if module_name in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None and "site-packages" not in (spec.origin or "")
    except ModuleNotFoundError:
        return False

def extract_imports_from_code(code):
    try:
        node = ast.parse(code)
    except Exception:
        return set()
    imports = set()
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.Import):
            for alias in stmt.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(stmt, ast.ImportFrom):
            if stmt.module:
                imports.add(stmt.module.split('.')[0])
    return imports

def extract_imports(file_path):
    if file_path.suffix == ".py":
        code = file_path.read_text(encoding="utf-8")
        return extract_imports_from_code(code)
    elif file_path.suffix == ".ipynb":
        with open(file_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        imports = set()
        for cell in nb.cells:
            if cell.cell_type == "code":
                imports |= extract_imports_from_code(cell.source)
        return imports
    else:
        return set()

def extract_includes_from_code(code):
    includes = re.findall(r'#include\s*[<"]([^">]+)[">]', code)
    return set(includes)

def classify_include(header):
    std_headers = {
        'stdio.h', 'stdlib.h', 'string.h', 'math.h', 'time.h', 'assert.h',
        'iostream', 'vector', 'map', 'set', 'string', 'memory', 'algorithm'
    }
    if header in std_headers:
        return "Standard Library"
    elif '/' in header or header.endswith(('.h', '.hpp')):
        return "Local or Third-Party"
    else:
        return "Unknown"

def snoopy(path):
    path = Path(path)
    files = []

    if path.is_dir():
        files = list(path.rglob("*.py")) + list(path.rglob("*.ipynb")) + \
                list(path.rglob("*.c")) + list(path.rglob("*.cpp")) + \
                list(path.rglob("*.h")) + list(path.rglob("*.hpp"))
    else:
        files = [path]

    py_deps = defaultdict(set)
    cpp_deps = defaultdict(set)

    print("🐾 Snoopy is sniffing out your dependencies...")

    for file in files:
        print(f"\n📄 File: {file}")
        if file.suffix in [".py", ".ipynb"]:
            imports = extract_imports(file)
            for imp in sorted(imports):
                if is_std_lib(imp):
                    py_deps['standard_lib'].add(imp)
                    source = "Standard Library"
                elif imp in STATIC_LICENSE_MAP:
                    py_deps['third_party'].add(imp)
                    source = "Third-Party"
                else:
                    py_deps['local_or_missing'].add(imp)
                    source = "Local/Missing"
                print(f"  {imp:<25} → {source}")
        elif file.suffix in [".c", ".cpp", ".h", ".hpp"]:
            code = file.read_text(errors='ignore')
            includes = extract_includes_from_code(code)
            for inc in sorted(includes):
                category = classify_include(inc)
                cpp_deps[category].add(inc)
                print(f"  {inc:<25} → {category}")

    if py_deps:
        print("\n=== 🐍 Python Dependencies ===")
        for key in ['standard_lib', 'third_party', 'local_or_missing']:
            print(f"{key.replace('_', ' ').title()}:")
            for mod in sorted(py_deps[key]):
                print(f"  - {mod}")
            print()

        print("📦 Suggested requirements.txt with licenses:")
        with open("requirements.txt", "w") as f:
            for dep in sorted(py_deps['third_party']):
                license_name, license_url = get_package_license(dep)
                print(f"  {dep:<15} (License: {license_name}) {license_url}")
                f.write(f"{dep}  # License: {license_name} {license_url}\n")

    if cpp_deps:
        print("\n=== 💻 C/C++ Dependencies ===")
        for key in ['Standard Library', 'Local or Third-Party', 'Unknown']:
            print(f"{key}:")
            for header in sorted(cpp_deps.get(key, [])):
                print(f"  - {header}")

    cpp_sources = [f.name for f in files if f.suffix == ".cpp"]
    if cpp_sources:
        print("🛠️ Suggested Makefile:")
        print("-------------------------")
        print("CXX = g++")
        print("CXXFLAGS = -std=c++17 -Wall -O2\n")
        print("TARGET = main")
        print(f"SRCS = {' '.join(cpp_sources)}")
        print("OBJS = $(SRCS:.cpp=.o)\n")
        print("all: $(TARGET)\n")
        print("$(TARGET): $(OBJS)")
        print("\t$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)\n")
        print("clean:")
        print("\trm -f $(TARGET) $(OBJS)")
        print("-------------------------")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="snoopy",
        description=(
            "🐾 Snoopy - Annotate Python, Jupyter, and C/C++ dependencies\n\n"
            "Scans imports and includes, categorizes dependencies, suggests requirements.txt and Makefile.\n"
            "For more details and examples, see: /home/bob/tools/dev_utils/snoopy.ipynb"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("path", help="Path to a file or folder to scan")
    args = parser.parse_args()
    snoopy(args.path)
