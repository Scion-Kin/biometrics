# Biometrics Integration for ERPs

## Installation

To install and configure the project, run the following command:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Scion-Kin/biometrics/refs/heads/main/ZKTeco/setup.sh)" -m erpnext
```

This command will download and execute the setup script, which will install the
necessary dependencies and configure the project for ERPNext integration.
If you want Laravel/Milmall integration,
replace `-m erpnext` with `-m milmall` in the command above.

## Configuration

After installation, you can configure the project by editing the configuration files.
First change user to biouser with the following command:

```bash
sudo su biouser
```

For ERPNext edit the configuration file:

```bash
nano ~/biometrics/ZKTeco/erpnext/config.py
```

For Laravel/Milmall edit the configuration file:

```bash
nano ~/biometrics/ZKTeco/milmall/config.py
```

For the biometrics service edit the configuration file:

```bash
nano ~/biometrics/ZKTeco/bio_config.py
```
