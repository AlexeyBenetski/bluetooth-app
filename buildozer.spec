[app]
title = Bluetooth File Transfer
package.name = bluetoothfiletransfer
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy,pyjnius,android

orientation = portrait

[buildozer]
log_level = 2

[app]
presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png

android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

android.gradle_dependencies = implementation 'androidx.appcompat:appcompat:1.6.1'

[app]
android.manifest.intent_filters = <intent-filter>
                                   <action android:name="android.intent.action.MAIN" />
                                   <category android:name="android.intent.category.LAUNCHER" />
                                   </intent-filter>