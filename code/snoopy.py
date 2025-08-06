#!/usr/bin/env python3
import os
import re
import sys
import ast
import nbformat
import importlib.util
from pathlib import Path
from collections import defaultdict

def is_std_lib(module_name):
    if module_name in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None or not spec.origin:
            return False
        return "site-packages" not in spec.origin
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

def get_license_info(package_name):
    try:
        import importlib.metadata as metadata
    except ImportError:
        import importlib_metadata as metadata  # For Python < 3.8

    try:
        dist = metadata.metadata(package_name)
        license_name = dist.get("License", "Unknown").strip()
        if license_name.lower().startswith("bsd"):
            license_url = "https://opensource.org/licenses/BSD-3-Clause"
        elif "mit" in license_name.lower():
            license_url = "https://opensource.org/licenses/MIT"
        elif "apache" in license_name.lower():
            license_url = "https://www.apache.org/licenses/LICENSE-2.0"
        elif "gpl" in license_name.lower():
            license_url = "https://www.gnu.org/licenses/gpl-3.0.html"
        else:
            license_url = "https://pypi.org/project/" + package_name + "/"
        return license_name, license_url
    except metadata.PackageNotFoundError:
        return "Unknown", "https://pypi.org/project/" + package_name + "/"

def show_help():
    notebook_path = Path(__file__).resolve().parents[1] / "snoopy.ipynb"
    print(f"""Usage: snoopy [file_or_folder]

Examples:
  snoopy my_script.py
  snoopy my_project/

Options:
  -h, --help      Show this help message and exit

📓 For examples and docs, see:
  {notebook_path}
""")

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

    print("\U0001F43E Snoopy is sniffing out your dependencies...")

    for file in files:
        print(f"\n\U0001F4C4 File: {file}")
        if file.suffix in [".py", ".ipynb"]:
            imports = extract_imports(file)
            for imp in sorted(imports):
                if is_std_lib(imp):
                    py_deps['standard_lib'].add(imp)
                    source = "Standard Library"
                else:
                    py_deps['third_party'].add(imp)
                    source = "Third-Party"
                print(f"  {imp:<25} → {source}")
        elif file.suffix in [".c", ".cpp", ".h", ".hpp"]:
            code = file.read_text(errors='ignore')
            includes = extract_includes_from_code(code)
            for inc in sorted(includes):
                category = classify_include(inc)
                cpp_deps[category].add(inc)
                print(f"  {inc:<25} → {category}")

    if py_deps:
        print("\n=== \U0001F40D Python Dependencies ===")
        for key in ['standard_lib', 'third_party']:
            print(f"{key.replace('_', ' ').title()}:")
            for mod in sorted(py_deps[key]):
                print(f"  - {mod}")
            print()

        print("\U0001F4E6 Suggested requirements.txt with licenses:")
        with open("requirements.txt", "w") as f:
            for dep in sorted(py_deps['third_party']):
                license_name, license_url = get_license_info(dep)
                print(f"  {dep:<15} (License: {license_name}, {license_url})")
                f.write(f"{dep}  # License: {license_name}, {license_url}\n")

    if cpp_deps:
        print("\n=== \U0001F4BB C/C++ Dependencies ===")
        for key in ['Standard Library', 'Local or Third-Party', 'Unknown']:
            print(f"{key}:")
            for header in sorted(cpp_deps.get(key, [])):
                print(f"  - {header}")

        cpp_sources = [f.name for f in files if f.suffix == ".cpp"]
        if cpp_sources:
            print("\U0001F6E0 Suggested Makefile:")
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
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        show_help()
    else:
        snoopy(sys.argv[1])
