#!/usr/bin/env bash

DIR="$(pwd)"

if [[ $DIR != *"biometrics" ]]; then
  echo -e "\x1b[1m[\x1b[31m ERROR \x1b[0m\x1b[1m]\x1b[22m This script must be run from the biometrics directory."
  exit 1
fi

sudo apt-get update
sudo apt-get install -y gnupg curl zsh

# Add MongoDB repository for Ubuntu Focal
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt-get update -y 
sudo apt-get install -y python3 python3-pip python3-venv mongodb-org
sudo service cron start

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r ZKTeco/requirements.txt

echo -e "\x1b[1m[\x1b[33m INFO \x1b[0m\x1b[1m]\x1b[22m Setting up the cron job..."
# Get the current directory

if [ -f "$DIR/cf/runner.sh" ]; then
  (sudo crontab -l 2>/dev/null; echo "* * * * * cd $DIR && cf/runner.sh >> $DIR/debug.log > 2>&1") | sudo crontab -
else
  echo -e "\x1b[1m[\x1b[31m ERROR \x1b[0m\x1b[1m]\x1b[22m File $DIR/cf/runner.sh does not exist. Did you delete it? if so, run -> 'git restore .' to restore it"
  exit 1
fi

echo -e "\x1b[1m[\x1b[32m SUCCESS \x1b[0m\x1b[1m]\x1b[22m Cron job for the HikVision integration has been setup successfully!"

# check if oh-my-zsh is installed
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo -e "\x1b[1m[\x1b[33m INFO \x1b[0m\x1b[1m]\x1b[22m Installing Oh My Zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
else
    echo -e "\x1b[1m[\x1b[32m SUCCESS \x1b[0m\x1b[1m]\x1b[22m Oh My Zsh is already installed."
fi
