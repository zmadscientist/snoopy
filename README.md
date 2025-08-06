# 🐾 Snoopy

**Snoopy** is a lightweight dependency annotation tool for Python, Jupyter Notebooks, and C/C++ projects. It scans your files and reports the libraries they import or include, categorized by source, and helps generate a Python `requirements.txt` file with license information.

---

## 🚀 Features

✅ **Python & Jupyter Support**  
- Parses `import` statements in `.py` and `.ipynb` files  
- Differentiates between standard library, third-party, and local/missing modules  
- Generates `requirements.txt` with license names and links

✅ **C/C++ Support**  
- Parses `#include` statements from `.c`, `.cpp`, `.h`, and `.hpp` files  
- Classifies headers as Standard Library, Local/Third-Party, or Unknown  
- Suggests a `Makefile` if `.cpp` files are found

✅ **Project-Wide Analysis**  
- Works recursively through directories  
- Handles mixed-language projects  

✅ **Clean Output**  
- Color-coded, categorized CLI output  
- Auto-generates `requirements.txt` with license info  
- Shows Makefile suggestions for C++

---

## 📦 Installation

### One-time setup:
```bash
# Deactivate snoopy environment first if active
conda deactivate

# Run install script (assumes snoopy.py is in ./code)
bash install_snoopy.sh
```

This will:
- Copy `code/snoopy.py` to `~/tools/dev_utils/snoopy`
- Make it executable
- Create a symlink at `~/.local/bin/snoopy`

Add to your path if needed:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🧪 Usage

```bash
# Analyze a single file
snoopy my_script.py

# Analyze a Jupyter notebook
snoopy notebook.ipynb

# Analyze an entire folder recursively
snoopy my_project/
```

---

## 📌 Example Output

```text
🐾 Snoopy is sniffing out your dependencies...

📄 File: examples/podcastGenerator/podGen.py
  bark                      → Local/Missing
  os                        → Standard Library
  re                        → Standard Library
  scipy                     → Third-Party
  warnings                  → Standard Library

=== 🐍 Python Dependencies ===
Standard Lib:
  - os
  - re
  - warnings

Third Party:
  - scipy

Local Or Missing:
  - bark

📦 Suggested requirements.txt with licenses:
  scipy            (License: BSD License, https://opensource.org/licenses/BSD-3-Clause)
```

---

### 🛠️ Example C++ Output

```text
📄 File: examples/math_demo.cpp
  cmath                    → Standard Library
  iostream                 → Standard Library

=== 💻 C/C++ Dependencies ===
Standard Library:
  - cmath
  - iostream

🛠️ Suggested Makefile:
CXX = g++
CXXFLAGS = -std=c++17 -Wall -O2

TARGET = main
SRCS = math_demo.cpp
OBJS = $(SRCS:.cpp=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

clean:
	rm -f $(TARGET) $(OBJS)
```

---

## 🧠 Notes

- Python license data is looked up using `importlib.metadata` (static analysis only)
- Missing modules do not stop execution — just flagged as `Local/Missing`
- You should still verify versions for production `requirements.txt`

---

## 🧩 Future Ideas

- JavaScript/HTML parsing support
- Optional dependency graph visualization
- Package version auto-resolution (static)

---

## 🐍 Recommended Workflow

1. Activate your env:
   ```bash
   mamba activate snoopy
   ```

2. Scan your project:
   ```bash
   snoopy path/to/project/
   ```

3. Review output + generated `requirements.txt`

---

## 👋 Author

Bob Chesebrough with help from ChatGPT Built for developers and educators by someone who hates dependency surprises 🧪🐾