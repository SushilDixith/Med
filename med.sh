#!/bin/bash

# Text colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Error counter
errors=0

# Function to print messages
print_message() {
    echo -e "${BOLD}$1${NC}"
}

# Function to print errors
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
    ((errors++))
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

# Function to check command existence
check_command() {
    if ! command -v $1 &> /dev/null; then
        return 1
    fi
    return 0
}

# Function to install system packages based on OS
install_system_dependencies() {
    print_message "Installing system dependencies..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Check for apt-based systems (Debian/Ubuntu)
        if check_command apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3-pip python3-dev libsndfile1 ffmpeg portaudio19-dev
            if [ $? -ne 0 ]; then
                print_error "Failed to install system dependencies using apt-get"
                return 1
            fi
        # Check for dnf-based systems (Fedora)
        elif check_command dnf; then
            sudo dnf install -y python3-pip python3-devel libsndfile ffmpeg portaudio-devel
            if [ $? -ne 0 ]; then
                print_error "Failed to install system dependencies using dnf"
                return 1
            fi
        # Check for pacman-based systems (Arch)
        elif check_command pacman; then
            sudo pacman -Sy python-pip libsndfile ffmpeg portaudio
            if [ $? -ne 0 ]; then
                print_error "Failed to install system dependencies using pacman"
                return 1
            fi
        else
            print_error "Unsupported Linux distribution"
            return 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! check_command brew; then
            print_error "Homebrew is not installed. Please install it first."
            return 1
        fi
        brew install libsndfile ffmpeg portaudio
        if [ $? -ne 0 ]; then
            print_error "Failed to install system dependencies using brew"
            return 1
        fi
    else
        print_error "Unsupported operating system: $OSTYPE"
        return 1
    fi
    
    print_success "System dependencies installed successfully"
    return 0
}

# Function to create and activate virtual environment
setup_virtual_environment() {
    print_message "Setting up Python virtual environment..."
    
    if ! check_command python3; then
        print_error "Python 3 is not installed"
        return 1
    fi
    
    # Create virtual environment
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        return 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        print_error "Failed to activate virtual environment"
        return 1
    fi
    
    print_success "Virtual environment created and activated"
    return 0
}

# Function to install Python packages
install_python_packages() {
    print_message "Installing Python packages..."
    
    # Upgrade pip
    pip install --upgrade pip
    if [ $? -ne 0 ]; then
        print_error "Failed to upgrade pip"
        return 1
    fi
    
    # Create requirements.txt
    cat > requirements.txt << EOL
numpy==1.24.3
scipy==1.10.1
soundfile==0.12.1
gtts==2.3.2
pydub==0.25.1
pyroomacoustics==0.7.3
librosa==0.10.1
python_speech_features==0.6
EOL
    
    # Install requirements
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install Python packages"
        return 1
    }
    
    print_success "Python packages installed successfully"
    return 0
}

# Main installation process
main() {
    print_message "Starting installation process..."
    
    # Install system dependencies
    install_system_dependencies
    if [ $? -ne 0 ]; then
        print_error "System dependencies installation failed"
        exit 1
    fi
    
    # Setup virtual environment
    setup_virtual_environment
    if [ $? -ne 0 ]; then
        print_error "Virtual environment setup failed"
        exit 1
    fi
    
    # Install Python packages
    install_python_packages
    if [ $? -ne 0 ]; then
        print_error "Python packages installation failed"
        exit 1
    fi
    
    if [ $errors -eq 0 ]; then
        print_success "Installation completed successfully!"
        print_message "To activate the virtual environment, run: source venv/bin/activate"
    else
        print_error "Installation completed with $errors errors"
        exit 1
    fi
}

# Run main function
main
