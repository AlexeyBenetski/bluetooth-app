# Bluetooth File Transfer Android App

Android application for Bluetooth communication and file transfer.

## Features
- Send and receive bytes via Bluetooth
- Transfer files between devices
- Simple and intuitive UI

## Build Instructions

### Using Docker (Recommended)
```bash
docker build -t bluetooth-app-builder .
docker run --rm -v ${PWD}:/app bluetooth-app-builder