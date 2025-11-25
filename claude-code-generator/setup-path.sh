#!/bin/bash
# Bash script to add Python Scripts directory to PATH
# For Linux/Mac users

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
SCRIPTS_PATH="$HOME/.local/bin"

echo "Checking Python Scripts directory..."
echo "Location: $SCRIPTS_PATH"

if [ -d "$SCRIPTS_PATH" ]; then
    echo "✓ Scripts directory exists"

    # Check if already in PATH
    if [[ ":$PATH:" == *":$SCRIPTS_PATH:"* ]]; then
        echo "✓ Already in PATH"
        echo ""
        echo "You can now use: claude-gen --help"
    else
        echo "Adding to PATH..."

        # Detect shell
        if [ -n "$ZSH_VERSION" ]; then
            SHELL_RC="$HOME/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            SHELL_RC="$HOME/.bashrc"
        else
            SHELL_RC="$HOME/.profile"
        fi

        # Add to shell RC file
        echo "" >> "$SHELL_RC"
        echo "# Added by claude-code-generator setup" >> "$SHELL_RC"
        echo "export PATH=\"\$PATH:$SCRIPTS_PATH\"" >> "$SHELL_RC"

        echo "✓ Added to PATH in $SHELL_RC"
        echo ""
        echo "IMPORTANT: Run this command to apply changes:"
        echo "  source $SHELL_RC"
        echo ""
        echo "Or close and reopen your terminal"
        echo ""
        echo "Then you can use: claude-gen --help"
    fi

    # Test if claude-gen exists
    if [ -f "$SCRIPTS_PATH/claude-gen" ]; then
        echo ""
        echo "✓ claude-gen found at: $SCRIPTS_PATH/claude-gen"
    else
        echo ""
        echo "⚠ claude-gen not found. Make sure package is installed:"
        echo "  pip install -e ."
    fi
else
    echo "✗ Scripts directory not found at: $SCRIPTS_PATH"
    echo "Make sure Python is installed correctly"
fi

echo ""
echo "Current workaround (always works):"
echo "  python -m src.cli.main --help"
