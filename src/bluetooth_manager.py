from kivy.logger import Logger
from jnius import autoclass, cast
import threading
import time

class BluetoothManager:
    def __init__(self):
        self.bluetooth_adapter = None
        self.bluetooth_socket = None
        self.connected_device = None
        self.input_stream = None
        self.output_stream = None
        self.is_connected = False
        
    def initialize_bluetooth(self):
        try:
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            self.bluetooth_adapter = BluetoothAdapter.getDefaultAdapter()
            
            if self.bluetooth_adapter is None:
                Logger.error("BluetoothManager: Device does not support Bluetooth")
                return False
                
            if not self.bluetooth_adapter.isEnabled():
                Logger.info("BluetoothManager: Bluetooth is not enabled")
                # Note: In production, you'd request user to enable Bluetooth
                return False
                
            Logger.info("BluetoothManager: Bluetooth initialized successfully")
            return True
            
        except Exception as e:
            Logger.error(f"BluetoothManager: Initialization failed - {str(e)}")
            return False
    
    def enable_discoverability(self):
        try:
            Intent = autoclass('android.content.Intent')
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            
            discoverableIntent = Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE)
            discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 300)
            
            from android import mActivity
            mActivity.startActivity(discoverableIntent)
            return True
        except Exception as e:
            Logger.error(f"BluetoothManager: Enable discoverability failed - {str(e)}")
            return False
    
    def start_server(self):
        def server_thread():
            try:
                UUID = autoclass('java.util.UUID')
                BluetoothServerSocket = autoclass('android.bluetooth.BluetoothServerSocket')
                
                uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
                server_socket = self.bluetooth_adapter.listenUsingRfcommWithServiceRecord(
                    "BluetoothFileTransfer", uuid)
                
                Logger.info("BluetoothManager: Server started, waiting for connection...")
                
                self.bluetooth_socket = server_socket.accept()
                server_socket.close()
                
                self.input_stream = self.bluetooth_socket.getInputStream()
                self.output_stream = self.bluetooth_socket.getOutputStream()
                self.is_connected = True
                
                Logger.info("BluetoothManager: Client connected")
                
            except Exception as e:
                Logger.error(f"BluetoothManager: Server error - {str(e)}")
        
        thread = threading.Thread(target=server_thread)
        thread.daemon = True
        thread.start()
        return True
    
    def connect_to_device(self, device_address):
        def connect_thread():
            try:
                BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
                UUID = autoclass('java.util.UUID')
                
                device = self.bluetooth_adapter.getRemoteDevice(device_address)
                uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
                
                self.bluetooth_socket = device.createRfcommSocketToServiceRecord(uuid)
                self.bluetooth_socket.connect()
                
                self.input_stream = self.bluetooth_socket.getInputStream()
                self.output_stream = self.bluetooth_socket.getOutputStream()
                self.is_connected = True
                self.connected_device = device
                
                Logger.info(f"BluetoothManager: Connected to {device_address}")
                
            except Exception as e:
                Logger.error(f"BluetoothManager: Connection failed - {str(e)}")
        
        thread = threading.Thread(target=connect_thread)
        thread.daemon = True
        thread.start()
        return True
    
    def send_byte(self, byte_value):
        if not self.is_connected or self.output_stream is None:
            Logger.error("BluetoothManager: Not connected, cannot send byte")
            return False
        
        try:
            self.output_stream.write(byte_value)
            self.output_stream.flush()
            return True
        except Exception as e:
            Logger.error(f"BluetoothManager: Send byte failed - {str(e)}")
            self.is_connected = False
            return False
    
    def send_data(self, data):
        if not self.is_connected or self.output_stream is None:
            return False
        
        try:
            self.output_stream.write(data)
            self.output_stream.flush()
            return True
        except Exception as e:
            Logger.error(f"BluetoothManager: Send data failed - {str(e)}")
            self.is_connected = False
            return False
    
    def receive_data(self):
        if not self.is_connected or self.input_stream is None:
            return None
        
        try:
            available = self.input_stream.available()
            if available > 0:
                data = bytearray(available)
                self.input_stream.read(data)
                return bytes(data)
        except Exception as e:
            Logger.error(f"BluetoothManager: Receive data failed - {str(e)}")
            self.is_connected = False
        
        return None
    
    def disconnect(self):
        try:
            if self.bluetooth_socket:
                self.bluetooth_socket.close()
            self.is_connected = False
            self.input_stream = None
            self.output_stream = None
            Logger.info("BluetoothManager: Disconnected")
        except Exception as e:
            Logger.error(f"BluetoothManager: Disconnect failed - {str(e)}")