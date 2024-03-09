import os
import subprocess
import sys

def get_installed_packages():
    """Get a list of installed pip packages"""
    return [p.split('==')[0] for p in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode().split()]

def main():
    # Confirm before proceeding
    confirm = input("This will remove all installed Python packages and reinstall them from requirements.txt. Are you sure? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        return

    # Get list of installed packages
    installed_packages = get_installed_packages()

    # Uninstall all packages
    print("Uninstalling all packages...")
    for package in installed_packages:
        subprocess.call([sys.executable, '-m', 'pip', 'uninstall', '-y', package])

    # Reinstall packages from requirements.txt
    print("Reinstalling packages from requirements.txt...")
    subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    print("Operation completed.")

if __name__ == "__main__":
    main()
