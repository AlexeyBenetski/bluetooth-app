import os
import struct
from kivy.logger import Logger
from kivy.clock import Clock

class FileTransfer:
    def __init__(self, bluetooth_manager):
        self.bt_manager = bluetooth_manager
        self.current_file = None
        self.file_size = 0
        self.received_bytes = 0
        
    def send_file(self, file_path):
        if not self.bt_manager.is_connected:
            Logger.error("FileTransfer: Not connected, cannot send file")
            return False
        
        try:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Send file info (filename and size)
            filename_encoded = filename.encode('utf-8')
            header = struct.pack('!I', len(filename_encoded)) + filename_encoded
            header += struct.pack('!Q', file_size)
            
            if not self.bt_manager.send_data(header):
                return False
            
            # Send file data
            with open(file_path, 'rb') as file:
                sent_bytes = 0
                chunk_size = 1024
                
                while sent_bytes < file_size:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    
                    if not self.bt_manager.send_data(chunk):
                        return False
                    
                    sent_bytes += len(chunk)
                    progress = (sent_bytes / file_size) * 100
                    
                    # Send progress update (for UI)
                    progress_data = struct.pack('!B', int(progress))
                    self.bt_manager.send_data(b'PROGRESS:' + progress_data)
            
            Logger.info(f"FileTransfer: File {filename} sent successfully")
            return True
            
        except Exception as e:
            Logger.error(f"FileTransfer: Send file failed - {str(e)}")
            return False
    
    def start_receiving(self):
        self.current_file = None
        self.file_size = 0
        self.received_bytes = 0
        return True
    
    def process_received_data(self, data):
        if not self.current_file:
            # Expecting file header
            if len(data) >= 4:
                filename_length = struct.unpack('!I', data[:4])[0]
                
                if len(data) >= 4 + filename_length + 8:
                    filename = data[4:4+filename_length].decode('utf-8')
                    self.file_size = struct.unpack('!Q', data[4+filename_length:4+filename_length+8])[0]
                    
                    # Create file for writing
                    from android.storage import primary_external_storage_path
                    download_dir = os.path.join(primary_external_storage_path(), 'Download')
                    os.makedirs(download_dir, exist_ok=True)
                    
                    file_path = os.path.join(download_dir, filename)
                    self.current_file = open(file_path, 'wb')
                    self.received_bytes = 0
                    
                    Logger.info(f"FileTransfer: Receiving file {filename} ({self.file_size} bytes)")
                    
                    # Return remaining data after header
                    return data[4+filename_length+8:], {'type': 'file_info', 'filename': filename, 'filesize': self.file_size}
        
        else:
            # Receiving file data
            remaining_data = data
            
            # Check for progress updates
            if data.startswith(b'PROGRESS:'):
                if len(data) >= 10:
                    progress = struct.unpack('!B', data[9:10])[0]
                    remaining_data = data[10:]
                    return remaining_data, {'type': 'file_progress', 'progress': progress}
            
            # Write file data
            if self.current_file and remaining_data:
                write_size = min(len(remaining_data), self.file_size - self.received_bytes)
                self.current_file.write(remaining_data[:write_size])
                self.received_bytes += write_size
                
                progress = (self.received_bytes / self.file_size) * 100
                
                # Check if file transfer is complete
                if self.received_bytes >= self.file_size:
                    self.current_file.close()
                    self.current_file = None
                    Logger.info("FileTransfer: File received successfully")
                    return remaining_data[write_size:], {'type': 'file_progress', 'progress': 100}
                else:
                    return remaining_data[write_size:], {'type': 'file_progress', 'progress': progress}
        
        return data, None