import json
import getpass
import socket
from datetime import datetime

def generate_log(level, service, message):
    log = {
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "level": level,
        "service": service,
        "user": getpass.getuser(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "message": message
    }
    # Print log as a JSON string
    log_entry = json.dumps(log, indent=4)

    with open("servansible.log", "a") as logfile:
        logfile.write(log_entry + "\n")
    
    print("Log saved to servansible.log")

# Exemple d'utilisation
if __name__ == "__main__":
    level = input("Enter log level (e.g., INFO, ERROR): ")
    service = input("Enter service name: ")
    message = input("Enter log message: ")
    
    generate_log(level, service, message)
