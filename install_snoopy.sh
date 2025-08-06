#!/bin/bash

# 🛑 Prevent sourcing
(return 0 2>/dev/null) && {
    echo "🚫 Do not source this script. Run it like: bash install_snoopy.sh"
    return 1
}

set -e

CURRENT_ENV=$(basename "$CONDA_PREFIX" 2>/dev/null || echo "")

if [[ "$CURRENT_ENV" == "snoopy" ]]; then
  echo "🚫 You're in the 'snoopy' environment. Please deactivate it first:"
  echo "    conda deactivate"
  exit 1
fi

# 📁 Paths
SOURCE_FILE="./code/snoopy.py"
INSTALL_DIR="$HOME/tools/dev_utils"
TARGET="$INSTALL_DIR/snoopy"
LINK_PATH="$HOME/.local/bin/snoopy"

echo "🐾 Installing Snoopy from $SOURCE_FILE..."

# 🔍 Check if source file exists
if [[ ! -f "$SOURCE_FILE" ]]; then
    echo "❌ Could not find: $SOURCE_FILE"
    exit 1
fi

# 📦 Make sure destination directory exists
mkdir -p "$INSTALL_DIR"

# 🛡️ Backup existing snoopy if it exists
if [[ -f "$TARGET" ]]; then
    VERSION=0
    while [[ -f "${TARGET}${VERSION}" ]]; do
        ((VERSION++))
    done
    mv "$TARGET" "${TARGET}${VERSION}"
    echo "📦 Existing snoopy backed up to: ${TARGET}${VERSION}"
fi

# 📋 Copy instead of move
cp "$SOURCE_FILE" "$TARGET"
chmod +x "$TARGET"

# 🔗 Ensure ~/.local/bin exists and is in PATH
mkdir -p "$HOME/.local/bin"
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  echo "✅ Added ~/.local/bin to PATH in ~/.bashrc (run: source ~/.bashrc)"
fi

# 🔗 Create symlink
ln -sf "$TARGET" "$LINK_PATH"

echo "✅ Snoopy installed successfully!"
echo ""
echo "🧪 Try it: snoopy /path/to/your/project"
echo "💡 Reminder: activate the environment first:"
echo "    mamba activate snoopy"

