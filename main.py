import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import BluetoothFileTransferApp

if __name__ == '__main__':
    BluetoothFileTransferApp().run()