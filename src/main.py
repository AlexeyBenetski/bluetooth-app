from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.logger import Logger

from bluetooth_manager import BluetoothManager
from file_transfer import FileTransfer

class BluetoothApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.bt_manager = BluetoothManager()
        self.file_transfer = FileTransfer(self.bt_manager)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = Label(text='Bluetooth File Transfer', size_hint_y=None, height=50)
        self.add_widget(title)
        
        # Connection status
        self.status_label = Label(text='Status: Disconnected', size_hint_y=None, height=30)
        self.add_widget(self.status_label)
        
        # Byte transfer section
        byte_section = Label(text='Byte Transfer:', size_hint_y=None, height=30)
        self.add_widget(byte_section)
        
        # Byte input and send
        byte_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.byte_input = TextInput(hint_text='Enter byte (0-255)', multiline=False)
        self.send_byte_btn = Button(text='Send Byte', on_press=self.send_byte)
        byte_layout.add_widget(self.byte_input)
        byte_layout.add_widget(self.send_byte_btn)
        self.add_widget(byte_layout)
        
        # Received bytes display
        self.received_bytes_label = Label(text='Received bytes: ', size_hint_y=None, height=30)
        self.add_widget(self.received_bytes_label)
        
        # File transfer section
        file_section = Label(text='File Transfer:', size_hint_y=None, height=30)
        self.add_widget(file_section)
        
        # File selection and transfer buttons
        file_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.select_file_btn = Button(text='Select File', on_press=self.select_file)
        self.send_file_btn = Button(text='Send File', on_press=self.send_file)
        self.receive_file_btn = Button(text='Receive File', on_press=self.receive_file)
        
        file_buttons.add_widget(self.select_file_btn)
        file_buttons.add_widget(self.send_file_btn)
        file_buttons.add_widget(self.receive_file_btn)
        self.add_widget(file_buttons)
        
        # Progress bar
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
        self.add_widget(self.progress_bar)
        self.progress_bar.value = 0
        
        # Log area
        log_label = Label(text='Log:', size_hint_y=None, height=30)
        self.add_widget(log_label)
        
        self.log_scroll = ScrollView()
        self.log_text = Label(text='', size_hint_y=None, text_size=(None, None))
        self.log_scroll.add_widget(self.log_text)
        self.add_widget(self.log_scroll)
        
        # Start Bluetooth
        Clock.schedule_once(self.initialize_bluetooth, 1)
    
    def initialize_bluetooth(self, dt):
        if self.bt_manager.initialize_bluetooth():
            self.update_status('Bluetooth initialized')
            Clock.schedule_interval(self.check_incoming_data, 0.1)
        else:
            self.update_status('Bluetooth initialization failed')
    
    def update_status(self, message):
        self.status_label.text = f'Status: {message}'
        self.log_message(message)
    
    def log_message(self, message):
        Logger.info(f"App: {message}")
        current_text = self.log_text.text
        self.log_text.text = f"{message}\n{current_text}"
        self.log_text.height = max(400, len(self.log_text.text.split('\n')) * 20)
    
    def send_byte(self, instance):
        try:
            byte_value = int(self.byte_input.text)
            if 0 <= byte_value <= 255:
                if self.bt_manager.send_byte(byte_value):
                    self.update_status(f'Sent byte: {byte_value}')
                else:
                    self.update_status('Failed to send byte')
            else:
                self.update_status('Byte must be between 0-255')
        except ValueError:
            self.update_status('Invalid byte value')
    
    def check_incoming_data(self, dt):
        data = self.bt_manager.receive_data()
        if data:
            if isinstance(data, bytes) and len(data) == 1:
                # Single byte received
                byte_value = data[0]
                self.received_bytes_label.text = f'Received bytes: {byte_value}'
                self.update_status(f'Received byte: {byte_value}')
            elif isinstance(data, dict) and data.get('type') == 'file_progress':
                # File transfer progress
                progress = data.get('progress', 0)
                self.progress_bar.value = progress
                if progress == 100:
                    self.update_status('File transfer completed!')
            elif isinstance(data, dict) and data.get('type') == 'file_info':
                # File info received
                filename = data.get('filename')
                filesize = data.get('filesize')
                self.update_status(f'Receiving file: {filename} ({filesize} bytes)')
    
    def select_file(self, instance):
        from android.storage import primary_external_storage_path
        from android import mActivity
        from jnius import autoclass
        
        try:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            Environment = autoclass('android.os.Environment')
            
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("*/*")
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            
            mActivity.startActivityForResult(intent, 100)
            self.update_status('File picker opened')
        except Exception as e:
            self.update_status(f'Error opening file picker: {str(e)}')
    
    def send_file(self, instance):
        # This would be connected to the file picker result
        # For demo, we'll use a test approach
        self.update_status('Use file picker to select file first')
    
    def receive_file(self, instance):
        if self.file_transfer.start_receiving():
            self.update_status('Ready to receive files')
        else:
            self.update_status('Failed to start file reception')

class BluetoothFileTransferApp(App):
    def build(self):
        return BluetoothApp()
    
    def on_pause(self):
        return True
    
    def on_resume(self):
        pass

if __name__ == '__main__':
    BluetoothFileTransferApp().run()