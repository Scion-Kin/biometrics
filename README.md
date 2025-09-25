# Biometrics ERP Integration

## Installation

To install and configure the project, run the following command:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Scion-Kin/biometrics/refs/heads/main/ZKTeco/setup.sh)"
```

## Configuration

After installation, you can configure the project by editing the configuration files.
First change user to biouser with the following command:

```bash
sudo su - biouser
```

Then for laravel edit the configuration file:

```bash
nano ~/biometrics/ZKTeco/milmall/config.py
```

For the biometrics service edit the configuration file:

```bash
nano ~/biometrics/ZKTeco/bio_config.py
```
