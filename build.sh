#!/usr/bin/env bash
set -e  # Stop on any error

# ----------- Colors & Emojis -----------
GREEN="\\033[0;32m"
YELLOW="\\033[1;33m"
RED="\\033[0;31m"
RESET="\\033[0m"
OK="✅"
FAIL="❌"
INFO="ℹ️"
BUILD="🏗️"
TEST="🧪"
DONE="🎉"

# ----------- Helper Functions -----------
fail_exit() {
    echo -e "${RED}${FAIL} ${1}${RESET}"
    exit 1
}

check_cmd() {
    command -v "$1" >/dev/null 2>&1 || fail_exit "$1 not found. Please install it."
}

# ----------- Preflight Checks -----------
echo -e "${INFO} Checking prerequisites..."

check_cmd python3
check_cmd pip3
check_cmd npm
check_cmd node

PY_VER=$(python3 -V 2>&1 | awk '{print $2}')
NODE_VER=$(node -v)
echo -e "${GREEN}${OK} Python $PY_VER detected${RESET}"
echo -e "${GREEN}${OK} Node $NODE_VER detected${RESET}"

# ----------- Virtual Environment Setup -----------
echo -e "${INFO} Setting up Python virtual environment..."
python3 -m venv .venv || fail_exit "Failed to create virtual environment."
source .venv/bin/activate || fail_exit "Failed to activate virtual environment."


# ----------- Backend Build -----------
echo -e "${BUILD} Building Backend..."
echo -e "${INFO} Cleaning old backend build artifacts..."
rm -rf build dist __pycache__ backend_main backend_main.exe || true
cd Backend || fail_exit "Backend folder not found."

pip3 install -r requirements.txt || fail_exit "Failed to install backend dependencies."
pip3 install pyinstaller || fail_exit "Failed to install PyInstaller."

cd ..
pyinstaller --onefile --name backend_main ./Backend/main.py --add-data ".env:." || fail_exit "Backend build failed."
mv dist/backend_main* ./ 2>/dev/null || fail_exit "Failed to move backend binary."

echo -e "${GREEN}${OK} Backend built successfully!${RESET}"



# ----------- Frontend Build -----------
echo -e "${BUILD} Building Frontend..."
echo -e "${INFO} Cleaning old frontend build artifacts..."
rm -rf Frontend/node_modules Frontend_builds frontend_main-* || true
cd Frontend || fail_exit "Frontend folder not found."

npm install || fail_exit "npm install failed."
npm run build || fail_exit "Frontend build failed."

cd ..

# Build frontend binaries
npm install || fail_exit "Root npm install failed."
npm run build:frontend || fail_exit "Frontend binary build failed."

mv Frontend_builds/frontend_main-* ./ 2>/dev/null || fail_exit "Failed to move frontend binary."

echo -e "${GREEN}${OK} Frontend built successfully!${RESET}"

# ----------- Final Check -----------
echo -e "${INFO} Verifying built executables..."
if ls ./backend_main* >/dev/null 2>&1 && ls ./frontend_main-* >/dev/null 2>&1; then
    echo -e "${GREEN}${OK} Both backend and frontend binaries are present.${RESET}"
else
    fail_exit "Executables missing after build."
fi

# ----------- Done -----------
echo -e "${DONE} Build completed successfully!${RESET}"
