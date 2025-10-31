#!/usr/bin/env python3
import os
import sys
import subprocess

def run_command(cmd, cwd=None):
    """Run a command and print output"""
    print(f"Running: {cmd}")
    process = subprocess.Popen(cmd, shell=True, cwd=cwd, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT,
                             universal_newlines=True)
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    return process.returncode

def main():
    # Check if buildozer is installed
    try:
        import buildozer
    except ImportError:
        print("Buildozer not found. Installing...")
        run_command("pip install buildozer")
    
    # Create buildozer.spec if it doesn't exist
    if not os.path.exists("buildozer.spec"):
        run_command("buildozer init")
    
    # Build the APK
    print("Starting APK build...")
    result = run_command("buildozer android debug")
    
    if result == 0:
        print("Build completed successfully!")
        if os.path.exists("bin/bluetoothfiletransfer-0.1-arm64-v8a_armeabi-v7a-debug.apk"):
            print("APK file: bin/bluetoothfiletransfer-0.1-arm64-v8a_armeabi-v7a-debug.apk")
    else:
        print("Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()