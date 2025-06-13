# The configuration file for the ZKTeco API and Frappe API
# Please fill in the necessary details before running the Attendance script
# Devices
devices = [
  # In case transfer protocol configurations are needed, they will be added later
  # Please fill in the necessary details for each device
  {
    "name": "Device 1",
    "ip": "192.168.0.121",
    # The username and password are not needed for ZKTeco devices
    # "username": "admin",
    # "password": "@Attendancekabuy",
  }
]

# Frappe API key
frappe_api_key = "92586e5482a6749"

# Frappe secret key
frappe_secret_key = "2d2366813622918"

# Frappe API URL
frappe_api_url = "https://erp.opensuite.tech"

# Max work hours
maxWorkHours = 24

# The shifts to be excluded from the no update policy. These are shifts with a strict constant schedule
updateFor = [""]
  