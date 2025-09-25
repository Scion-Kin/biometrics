#!/usr/bin/env bash
set -e
sudo apt-get update
sudo apt-get install -y gnupg zsh

source /etc/os-release
source /etc/lsb-release

# Add MongoDB repository if not already added
if [ ! -f "/etc/apt/sources.list.d/mongodb-org-8.0.list" ]; then
  curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor
  echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu ${DISTRIB_CODENAME:-$VERSION_CODENAME}/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
fi

sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv mongodb-org
sudo service cron start

# Add user
if ! id -u biouser &>/dev/null; then
    echo -e "\x1b[1m[\x1b[33m INFO \x1b[0m\x1b[1m]\x1b[22m Creating 'biouser user..."
    sudo useradd -ms $(which zsh) biouser
    sudo usermod -aG sudo biouser
    echo "biouser ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/biouser
    sudo chmod 440 /etc/sudoers.d/biouser
    echo -e "\x1b[1m[\x1b[32m SUCCESS \x1b[0m\x1b[1m]\x1b[22m Added 'biouser user."
else
    echo -e "\x1b[1m[\x1b[32m SUCCESS \x1b[0m\x1b[1m]\x1b[22m User 'biouser' already exists."
fi

echo "Switching to 'biouser' user..."
sudo -i -u biouser bash << 'EOF'
set -e
cd ~
# check if oh-my-zsh is installed
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo -e "\x1b[1m[\x1b[33m INFO \x1b[0m\x1b[1m]\x1b[22m Installing Oh My Zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" --unattended
fi

# Clone the repository
if [ ! -d "$HOME/biometrics" ]; then
    echo -e "\x1b[1m[\x1b[33m INFO \x1b[0m\x1b[1m]\x1b[22m Cloning the repository..."
    git clone https://github.com/Scion-Kin/biometrics
    echo -e "\x1b[1m[\x1b[32m SUCCESS \x1b[0m\x1b[1m]\x1b[22m Repository cloned successfully."
fi
cd $HOME/biometrics

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r ZKTeco/requirements.txt

echo -e "\x1b[1m[\x1b[33m INFO \x1b[0m\x1b[1m]\x1b[22m Setting up the cron job..."
if [ -f "cf/runner.sh" ]; then
  (crontab -l 2>/dev/null; echo "*/10 * * * * cd $HOME/biometrics && cf/runner.sh >> debug.log 2>&1") | crontab -
fi

echo -e "\x1b[1m[\x1b[32m SUCCESS \x1b[0m\x1b[1m]\x1b[22m Set up successfull"
EOF
