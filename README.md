# 🐾 Snoopy - Python & C/C++ Dependency Analyzer

## Overview

**Snoopy** is a developer tool for scanning Python (.py, .ipynb) and C/C++ (.c, .cpp, .h) source files to:
- Identify imported packages or included headers.
- Look up license information for Python packages (via pythonLicenses.csv).
- Suggest requirements.txt entries for Python projects.
- Suggest boilerplate Makefiles for C/C++ projects.

## Features
- **Python analysis**: Lists all imported packages and their licenses.
- **Jupyter Notebook analysis**: Scans code cells for imports.
- **C/C++ analysis**: Lists all #include headers.
- **Makefile suggestion**: Generates a BLAS-enabled Makefile for .cpp files.
- **requirements.txt generation** for Python projects.
- **License lookup** from *pythonLicenses.csv*, which can be kept up-to-date using the sister project . [licenseLookupRAG](https://github.com/zmadscientist/pythonLicenseDB)

## Prerequisites
- Python 3.8+
- *pythonLicenses.csv* in the same directory as snoopy.py

## Python Dependencies:
```bash
pip install nbformat beautifulsoup4
```



## Recommended: 
- Keep your *pythonLicenses.csv* up to date using [licenseLookupRAG](https://github.com/zmadscientist/pythonLicenseDB).

-------

## 🚀 Usage 

### Scan a single Python file:

```bash
python snoopy.py my_script.py
```

### Scan a Jupyter notebook:

```bash
python snoopy.py analysis.ipynb
```

### Scan a C++ file and get Makefile suggestion:

```bash
python snoopy.py matrix_mul.cpp
```

### Scan an entire project directory:

```bash
python snoopy.py /path/to/project
``` 

-------

## Output Examples

### Python example:

```bash
=== 🐍 Python Dependencies ===
📄 my_script.py
  numpy                → BSD
  requests             → Apache-2.0

📦 Suggested requirements.txt:
numpy
requests
```

### C++ example:

```bash
📄 matrix_mul.cpp
  #include <iostream>
  #include <cblas.h>

🛠 Suggested Makefile:

CXX = g++
CXXFLAGS = -Wall -O2
LDFLAGS = -lblas
TARGET = matrix_mul
OBJS = matrix_mul.o
```
-----

## 📦 Folder Structure

```bash
snoopy/
├── snoopy.py                   # Main tool entry point
├── pythonLicenses.csv          # CSV with known Python license info
├── license_lookup_results.csv  # Optional LLM-enriched lookup CSV
├── *.ipynb                     # Your supporting notebooks or examples
├── pythonLicense*.csv          # Snapshots from earlier runs
```

-------
### 1.0 Quick Setup & Installation Notes (for future me)

When coming back to `snoopy`, here are the steps to get the CLI working again:

#### 1.1 Softlinks (optional convenience)
If you want to run `snoopy.py` without installing, create a symlink to a directory on your `$PATH`:

```bash
ln -s /home/bob/examples/snoopy/snoopy.py ~/tools/dev_utils/snoopy
chmod +x ~/tools/dev_utils/snoopy
```

#### Now you can run it directly with:

```bash
snoopy --help

```
### 2.0   Install via pipx (preferred)

Make sure pipx is installed:

```bash
sudo apt install pipx
pipx ensurepath

```
Then, from the project root (where pyproject.toml lives):

### 3.0 Install via editable pip (fallback)
If you don’t want to use pipx:

```bash
pip install -e .
```

This also exposes snoopy globally, but tied to the active Python environment.

### 4.0 Run the README viewer

As a reminder, you added a --readme option:

```bash
snoopy --readme

```
This will dump the project’s README.md to your terminal so you don’t need to open the file manually.

### Pro tip for future me:
If you see error: does not appear to be a Python project, double-check that pyproject.toml is present in the project root. Without it, **pip install -e **. or **pipx install -e .**preview readme won’t work.

-------
## Credits

#### Created by Bob Chesebrough, with code refinement assistance from ChatGPT.

runs
