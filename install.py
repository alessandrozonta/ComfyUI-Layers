import subprocess
import sys

def install_package(package_name, options=""):
    command = [sys.executable, "-m", "pip", "install", package_name] + options.split()
    subprocess.check_call(command)

def main():
    try:
        print("Installing pytoshop...")
        install_package("pytoshop", "-I --no-cache-dir")
        print("pytoshop installed successfully.")
        
        print("Installing psd-tools...")
        install_package("psd-tools", "--no-deps")
        print("psd-tools installed successfully.")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing packages: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
