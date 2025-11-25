# Flash Firmware

Upload firmware to IoT Test hardware device.


## Quick Flash Commands

### Raspberry Pi Pico/Pico W

```bash
# Flash MicroPython firmware
# 1. Hold BOOTSEL button while connecting USB
# 2. Device appears as mass storage device (RPI-RP2)

# Download latest MicroPython
wget https://micropython.org/download/rp2-pico-w/rp2-pico-w-latest.uf2

# Flash firmware (drag & drop or copy)
cp rp2-pico-w-latest.uf2 /Volumes/RPI-RP2/  # macOS
cp rp2-pico-w-latest.uf2 /media/RPI-RP2/     # Linux
# Or drag file to RPI-RP2 drive on Windows

# Device will reboot automatically
```

### ESP32/ESP8266

```bash
# Install esptool
pip install esptool

# Erase flash (recommended before first flash)
esptool.py --port /dev/ttyUSB0 erase_flash

# Flash MicroPython/CircuitPython
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-firmware.bin

# On Windows, port is usually COM3, COM4, etc.
esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-firmware.bin

# Flash your application code
ampy --port /dev/ttyUSB0 put firmware/main.py
```

### Arduino Boards

```bash
# Using Arduino CLI
arduino-cli compile --fqbn arduino:avr:uno firmware/
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno firmware/

# Using avrdude directly
avrdude -c arduino -p atmega328p -P /dev/ttyACM0 -b 115200 -U flash:w:firmware.hex
```

## Detailed Flashing Instructions

### 1. Prepare Device

```bash
# Check device is connected
# List USB devices
ls /dev/tty*  # Unix/macOS
# Look for /dev/ttyUSB0, /dev/ttyACM0, etc.

# On Windows, check Device Manager for COM port

# Verify device connection
```

### 2. Download/Build Firmware

```bash
# For Raspberry Pi Pico W with MicroPython
cd firmware
wget https://micropython.org/download/rp2-pico-w/rp2-pico-w-latest.uf2

```

### 3. Flash Firmware

#### Raspberry Pi Pico W

```bash
# Method 1: BOOTSEL mode (easiest)
# 1. Disconnect Pico from USB
# 2. Hold BOOTSEL button
# 3. Connect USB while holding button
# 4. Release button
# 5. Pico appears as mass storage (RPI-RP2)
# 6. Copy UF2 file

cp rp2-pico-w-latest.uf2 /Volumes/RPI-RP2/

# Method 2: Using picotool
sudo apt install picotool
picotool load firmware.uf2
picotool reboot
```


### 4. Upload Application Code

After flashing firmware, upload your application:

```bash
# Using ampy (Adafruit MicroPython tool)
pip install adafruit-ampy

# Upload single file
ampy --port /dev/ttyUSB0 put firmware/main.py

# Upload entire directory
ampy --port /dev/ttyUSB0 put firmware/lib

# List files on device
ampy --port /dev/ttyUSB0 ls

# Using rshell (alternative)
pip install rshell
rshell --port /dev/ttyUSB0
# In rshell:
# > cp firmware/* /pyboard/
# > repl  # Enter REPL to test
```


## Advanced Flashing

### Over-the-Air (OTA) Updates

```python
# Implement custom OTA for Pico W
# Download firmware over WiFi and write to flash
import urequests as requests
import machine

def ota_update(url):
    response = requests.get(url)
    with open('new_firmware.uf2', 'wb') as f:
        f.write(response.content)
    machine.reset()
```


### Batch Flashing Multiple Devices

```bash
# Flash multiple devices in sequence
for port in /dev/ttyUSB*; do
    echo "Flashing device on $port..."
done
```

### Custom Bootloader

```bash
```

## Firmware Verification

### Verify Flash Success

```bash
# Connect via serial and check
screen /dev/ttyUSB0 115200
# Press Ctrl+C to enter REPL
# Type: import sys; print(sys.implementation)

```

### Test Device

```bash
# Open serial monitor
/monitor-serial

# Check device responds
# Should see boot messages and application output
```

## Troubleshooting

### Device Not Detected

```bash
# Try different USB cable (some are power-only)
# Hold BOOTSEL button longer
# Try different USB port


# List all serial devices
ls -l /dev/tty*
```

### Flash Fails

```bash
# Reset device and retry
# Check USB cable quality
# Try different computer/port

```

### Wrong Firmware Version

```bash
# Check current firmware version
/monitor-serial
# Look for version in boot messages

# Flash correct firmware for your board
# Pico W: rp2-pico-w-xxxxx.uf2
# Pico (no WiFi): rp2-pico-xxxxx.uf2

```

### Device Bricked

```bash
# Pico cannot be bricked via software
# Can always enter BOOTSEL mode and reflash

```

## Safety Checklist

- [ ] Correct firmware file for device model
- [ ] Backup important data/config if applicable
- [ ] Device fully charged or on stable power
- [ ] Using quality USB cable (not charge-only)
- [ ] Correct COM port/device selected
- [ ] Bootloader present (if needed)

## Next Steps

After successful flash:
- Run `/monitor-serial` to see output
- Test basic functionality
- Upload application code
- Configure WiFi/network (if applicable)
- Test sensors/peripherals

Firmware flashed successfully for IoT Test! ⚡
