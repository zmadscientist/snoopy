#!/bin/bash

# 🛑 Detect if the script is being sourced
(return 0 2>/dev/null) && {
    echo "🚫 This script should NOT be sourced (no '.' or 'source')."
    echo "    Please run it like: bash install_snoopy.sh"
    return 1
}

set -e  # Exit on error

CURRENT_ENV=$(basename "$CONDA_PREFIX" 2>/dev/null || echo "")

if [[ "$CURRENT_ENV" == "snoopy" ]]; then
  echo "🚫 You are currently inside the 'snoopy' environment."
  echo "    Please deactivate it first with:"
  echo ""
  echo "      conda deactivate"
  echo ""
  echo "Then re-run this script:"
  echo "      bash install_snoopy.sh"
  exit 1
fi

SOURCE_FILE="./code/snoopy.py"
INSTALL_DIR="$HOME/tools/dev_utils"
TARGET="$INSTALL_DIR/snoopy"
LINK_PATH="$HOME/.local/bin/snoopy"

echo "🐾 Installing Snoopy..."

mkdir -p "$INSTALL_DIR"

if [[ ! -f "$SOURCE_FILE" ]]; then
    echo "❌ Could not find '$SOURCE_FILE'. Expected in ./code/"
    exit 1
fi

cp "$SOURCE_FILE" "$TARGET"
chmod +x "$TARGET"

mkdir -p "$HOME/.local/bin"

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  echo "✅ Added ~/.local/bin to PATH in ~/.bashrc (you may need to run: source ~/.bashrc)"
fi

ln -sf "$TARGET" "$LINK_PATH"

echo "✅ Snoopy installed successfully!"
echo ""
echo "🚀 You can now run it like:"
echo "    snoopy /path/to/your/project"
echo ""
echo "💡 Reminder: To use snoopy-related tools, activate the environment first:"
echo "    mamba activate snoopy"
