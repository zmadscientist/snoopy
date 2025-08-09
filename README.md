# 🐾 Snoopy - Python & C/C++ Dependency Analyzer

**Snoopy** is a command-line and notebook-friendly tool that helps you:
- Identify Python & Jupyter Notebook imports
- Detect C/C++ `#include` dependencies
- Look up known licenses from a CSV
- Generate a `requirements.txt`
- Suggest Makefile targets (for C/C++

🚀 Usage
From Command Line
bash
Copy
Edit
python3 snoopy.py path/to/your/project
Example:

bash
Copy
Edit
python3 snoopy.py ~/projects/my_analysis_notebook/
From Jupyter Notebook
python
Copy
Edit
from snoopy import snoopy_entry_point
snoopy_entry_point("/path/to/your/code_or_folder")
📋 CSV Input Format (for pythonLicenses.csv)
package	license
pandas	BSD License
numpy	BSD License
torch	BSD-3-Clause

## ✅ Features

### Detects:

    * .py files
    * .ipynb notebooks
    * .c, .cpp, .h, .hpp files

* Reads CSV to match licenses
* Handles unknown modules gracefully
* Prints suggested requirements.txt and Makefile targets

### 🔧 Dependencies
* Python 3.6+
* nbformat (optional, for .ipynb parsing)

Install nbformat:

```bash
pip install nbformat

```


## 💡 Use Case
Snoopy can be used to auto-generate documentation sections of a repo like:

### Dependencies

- Python
  - pandas (BSD)
  - numpy (BSD)
- C++
  - iostream
  - vector

This makes it easier to:

* Build OSS-compliant documentation

* Audit open-source projects

* Auto-generate requirements.txt and Makefile templates

## 📦 Folder Structure

```bash
snoopy/
├── snoopy.py                   # Main tool entry point
├── pythonLicenses.csv          # CSV with known Python license info
├── license_lookup_results.csv  # Optional LLM-enriched lookup CSV
├── *.ipynb                     # Your supporting notebooks or examples
├── pythonLicense*.csv          # Snapshots from earlier runs
---
s from earlier runs
