#!/bin/bash
# Setup script for Liberta pra Nois
# This script installs all system dependencies required for the project

set -e

echo "============================================================"
echo "Liberta pra Nois - Dependency Installer"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    if [ -f /etc/debian_version ]; then
        DISTRO="debian"
    elif [ -f /etc/redhat-release ]; then
        DISTRO="redhat"
    else
        DISTRO="unknown"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
    exit 1
fi

echo "Detected OS: $OS"
if [ "$OS" == "linux" ]; then
    echo "Detected distro type: $DISTRO"
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for sudo access
check_sudo() {
    if ! command_exists sudo; then
        echo -e "${YELLOW}Warning: sudo not found. Will attempt to install without sudo.${NC}"
        return 1
    fi
    
    if sudo -n true 2>/dev/null; then
        echo -e "${GREEN}✓ Sudo access available${NC}"
        return 0
    else
        echo -e "${YELLOW}Warning: Sudo requires password. You may be prompted.${NC}"
        return 0
    fi
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}Warning: Running as root. This script should be run as a normal user.${NC}"
    echo -e "${YELLOW}The script will use sudo only when needed for system packages.${NC}"
    echo ""
    echo "Please run without sudo: ./setup.sh"
    exit 1
fi

# Install pandoc
install_pandoc() {
    echo ""
    echo "--- Installing pandoc ---"
    
    if command_exists pandoc; then
        echo -e "${GREEN}✓ pandoc already installed ($(pandoc --version | head -1))${NC}"
        return 0
    fi
    
    if [ "$OS" == "macos" ]; then
        if command_exists brew; then
            echo "Installing pandoc via Homebrew..."
            brew install pandoc
        else
            echo -e "${RED}Error: Homebrew not found. Please install Homebrew first.${NC}"
            echo "Visit: https://brew.sh"
            return 1
        fi
    elif [ "$OS" == "linux" ]; then
        if [ "$DISTRO" == "debian" ]; then
            echo "Installing pandoc via apt..."
            sudo apt-get update
            sudo apt-get install -y pandoc
        else
            # Try to download standalone binary
            echo "Downloading standalone pandoc binary..."
            PANDOC_VERSION="3.1.11"
            PANDOC_URL="https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-amd64.tar.gz"
            
            cd /tmp
            curl -L -o pandoc.tar.gz "$PANDOC_URL"
            tar xvzf pandoc.tar.gz
            sudo cp "pandoc-${PANDOC_VERSION}/bin/pandoc" /usr/local/bin/
            rm -rf pandoc.tar.gz "pandoc-${PANDOC_VERSION}"
            cd -
        fi
    fi
    
    if command_exists pandoc; then
        echo -e "${GREEN}✓ pandoc installed successfully${NC}"
    else
        echo -e "${RED}✗ Failed to install pandoc${NC}"
        return 1
    fi
}

# Install Playwright browsers
install_playwright_browsers() {
    echo ""
    echo "--- Installing Playwright browsers ---"
    
    # Check if playwright is available as a Python module
    if ! python -c "import playwright" 2>/dev/null; then
        echo -e "${RED}Error: Playwright Python module not found.${NC}"
        echo ""
        echo "Please install Python dependencies first:"
        echo "  python3 -m venv .venv"
        echo "  source .venv/bin/activate  # or: .venv\\Scripts\\activate on Windows"
        echo "  pip install -r requirements.txt"
        echo ""
        echo "Then re-run this setup script."
        return 1
    fi
    
    # Try to use the playwright module directly
    echo "Installing Chromium browser for Playwright..."
    python -m playwright install chromium
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Playwright Chromium installed${NC}"
    else
        echo -e "${RED}✗ Failed to install Playwright browsers${NC}"
        return 1
    fi
}

# Install Playwright system dependencies
install_playwright_deps() {
    echo ""
    echo "--- Installing Playwright system dependencies ---"
    
    if [ "$OS" == "macos" ]; then
        echo -e "${GREEN}✓ macOS typically has required libraries pre-installed${NC}"
        echo "If you encounter issues, you may need to install additional libraries via Homebrew"
        return 0
    fi
    
    if [ "$OS" == "linux" ] && [ "$DISTRO" == "debian" ]; then
        echo "Installing required system libraries for Chromium..."
        
        # Update package list first
        sudo apt-get update
        
        # Install packages with error handling
        # Note: Some packages may have different names on different Ubuntu versions
        # libnss3 includes libnssutil3 and libsmime3
        # libatk1.0-0 (not libatk-1.0-0)
        # libatk-bridge2.0-0 (not libatk-bridge-2.0-0)
        
        sudo apt-get install -y \
            libnspr4 \
            libnss3 \
            libsqlite3-0 \
            libatk1.0-0 \
            libatk-bridge2.0-0 \
            libatspi2.0-0 \
            libxcomposite1 \
            libxdamage1 \
            libxfixes3 \
            libxrandr2 \
            libgbm1 \
            libxkbcommon0 \
            libasound2 \
            libcurl4 \
            libgtk-3-0 \
            libgdk-pixbuf2.0-0 || true
        
        # Check if critical libraries are now available
        echo ""
        echo "Verifying library installation..."
        local missing_libs=()
        
        if ! ldconfig -p | grep -q libnspr4.so; then
            missing_libs+=("libnspr4")
        fi
        
        if ! ldconfig -p | grep -q libnss3.so; then
            missing_libs+=("libnss3")
        fi
        
        if [ ${#missing_libs[@]} -eq 0 ]; then
            echo -e "${GREEN}✓ System dependencies installed${NC}"
        else
            echo -e "${YELLOW}Warning: Some libraries may be missing: ${missing_libs[*]}${NC}"
            echo "Attempting to use Playwright's built-in dependency installer..."
            python -m playwright install-deps chromium || true
            echo ""
            echo -e "${YELLOW}Note: Some libraries may still be missing, but the browser might still work.${NC}"
            echo "If you encounter browser errors, install the missing packages manually."
        fi
    else
        echo -e "${YELLOW}Warning: Automatic dependency installation only supported for Debian/Ubuntu${NC}"
        echo "Please install Playwright dependencies manually:"
        echo "  playwright install-deps chromium"
    fi
}

# Verify installation
verify_installation() {
    echo ""
    echo "============================================================"
    echo "Verifying Installation"
    echo "============================================================"
    
    local errors=0
    
    # Check pandoc
    if command_exists pandoc; then
        echo -e "${GREEN}✓ pandoc: $(pandoc --version | head -1)${NC}"
    else
        echo -e "${RED}✗ pandoc: NOT FOUND${NC}"
        errors=$((errors + 1))
    fi
    
    # Check Python packages
    if python -c "import playwright" 2>/dev/null; then
        echo -e "${GREEN}✓ playwright: installed${NC}"
    else
        echo -e "${RED}✗ playwright: NOT FOUND${NC}"
        errors=$((errors + 1))
    fi
    
    if python -c "import httpx" 2>/dev/null; then
        echo -e "${GREEN}✓ httpx: installed${NC}"
    else
        echo -e "${RED}✗ httpx: NOT FOUND${NC}"
        errors=$((errors + 1))
    fi
    
    if python -c "import trafilatura" 2>/dev/null; then
        echo -e "${GREEN}✓ trafilatura: installed${NC}"
    else
        echo -e "${RED}✗ trafilatura: NOT FOUND${NC}"
        errors=$((errors + 1))
    fi
    
    if python -c "from PIL import Image" 2>/dev/null; then
        echo -e "${GREEN}✓ Pillow: installed${NC}"
    else
        echo -e "${RED}✗ Pillow: NOT FOUND${NC}"
        errors=$((errors + 1))
    fi
    
    # Check Playwright browsers
    if [ -d "$HOME/.cache/ms-playwright/chromium_headless_shell-"* ] 2>/dev/null || \
       [ -d "$HOME/.cache/ms-playwright/chromium-"* ] 2>/dev/null; then
        echo -e "${GREEN}✓ Playwright Chromium browser: installed${NC}"
    else
        echo -e "${YELLOW}⚠ Playwright Chromium browser: NOT FOUND (run: playwright install chromium)${NC}"
    fi
    
    echo ""
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}============================================================"
        echo "Installation complete! All dependencies are ready."
        echo "============================================================${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Configure your .env file: cp .env.example .env"
        echo "  2. Edit .env with your credentials"
        echo "  3. Run tests: python -m pytest tests/unit/ -v"
        echo "  4. Run the pipeline: python main.py"
    else
        echo -e "${RED}============================================================"
        echo "Installation incomplete. $errors dependency(s) missing."
        echo "============================================================${NC}"
        return 1
    fi
}

# Main installation process
main() {
    check_sudo
    
    # Check if we're in a virtual environment
    if [ -z "${VIRTUAL_ENV}" ]; then
        echo -e "${YELLOW}Warning: Not in a virtual environment. It's recommended to use one.${NC}"
        echo ""
        echo "To create and activate a virtual environment:"
        echo "  python3 -m venv .venv"
        echo "  source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate"
        echo "  pip install -r requirements.txt"
        echo ""
        
        # Check if .venv exists
        if [ -d ".venv" ]; then
            echo -e "${GREEN}Found .venv directory. Activating it...${NC}"
            source .venv/bin/activate
            if [ -z "${VIRTUAL_ENV}" ]; then
                echo -e "${RED}Failed to activate virtual environment.${NC}"
                echo "Please activate it manually and run again."
                exit 1
            fi
            echo -e "${GREEN}✓ Virtual environment activated: ${VIRTUAL_ENV}${NC}"
        else
            read -p "Continue without virtual environment? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Please set up a virtual environment first:"
                echo "  python3 -m venv .venv"
                echo "  source .venv/bin/activate"
                echo "  pip install -r requirements.txt"
                exit 1
            fi
        fi
    else
        echo -e "${GREEN}✓ Virtual environment detected: ${VIRTUAL_ENV}${NC}"
    fi
    
    # Check Python dependencies
    echo ""
    echo "--- Checking Python dependencies ---"
    if ! python -c "import playwright" 2>/dev/null; then
        echo -e "${RED}Python dependencies not installed.${NC}"
        echo "Installing from requirements.txt..."
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install Python dependencies.${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Python dependencies installed${NC}"
    else
        echo -e "${GREEN}✓ Python dependencies already installed${NC}"
    fi
    
    # Install system dependencies
    install_pandoc
    install_playwright_browsers
    install_playwright_deps
    
    # Verify
    verify_installation
}

# Run main function
main
