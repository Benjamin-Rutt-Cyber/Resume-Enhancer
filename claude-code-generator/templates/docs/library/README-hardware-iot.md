# Hardware/IoT Project

An embedded systems project for IoT devices, built with MicroPython or CircuitPython for rapid development and easy prototyping.

## Overview

This IoT project provides:
- Microcontroller firmware for embedded devices
- Sensor data collection and processing
- Network connectivity (WiFi, MQTT, HTTP)
- Power management
- Real-time data transmission
- Remote configuration and updates

## Hardware Platform

### Supported Boards
- Raspberry Pi Pico W (WiFi)
- ESP32 (WiFi + Bluetooth)
- ESP8266 (WiFi)
- Arduino-compatible boards
- Raspberry Pi (for gateway/edge computing)

### Common Sensors
- Temperature/Humidity (DHT11, DHT22, BME280)
- Motion/Proximity (PIR, ultrasonic)
- Light sensors (LDR, photodiodes)
- Gas sensors (MQ series)
- GPS modules
- Accelerometer/Gyroscope (MPU6050)

### Actuators
- LEDs and RGB strips
- Relays and switches
- Servo motors
- Stepper motors
- Buzzers and speakers
- Display modules (OLED, LCD)

## Software Stack

### Firmware Language
- MicroPython 1.20+ (recommended)
- CircuitPython 8.0+
- C/C++ (for advanced use cases)

### Connectivity
- WiFi (802.11 b/g/n)
- MQTT protocol for messaging
- HTTP/HTTPS for API calls
- WebSocket for real-time data
- Bluetooth Low Energy (BLE) - optional

### Libraries
- `umqtt` - MQTT client
- `urequests` - HTTP client
- `machine` - Hardware access
- `network` - WiFi management
- `time` and `ntptime` - Time management
- Device-specific drivers

## Features

- WiFi connectivity with auto-reconnect
- MQTT pub/sub for cloud communication
- Sensor data collection with configurable intervals
- Local data buffering for offline operation
- Power-saving sleep modes
- OTA (Over-The-Air) firmware updates
- Configuration via WiFi AP mode
- Watchdog timer for reliability
- Error handling and logging
- LED status indicators

## Getting Started

### Prerequisites

- Python 3.7+ (for development tools)
- USB cable for flashing
- Device driver (CP210x or CH340 for most boards)
- Terminal emulator (screen, minicom, or Thonny IDE)

### Development Tools

**Option 1: Thonny IDE** (Recommended for beginners)
```bash
# Install Thonny
# Download from https://thonny.org/

# Thonny includes MicroPython installation and file management
```

**Option 2: Command Line Tools**
```bash
# Install esptool for ESP32/ESP8266
pip install esptool

# Install ampy for file management
pip install adafruit-ampy

# Install rshell
pip install rshell
```

### Flashing MicroPython

#### Raspberry Pi Pico W
1. Download MicroPython firmware (.uf2 file)
2. Hold BOOTSEL button while connecting USB
3. Drag .uf2 file to RPI-RP2 drive
4. Device will reboot automatically

#### ESP32/ESP8266
```bash
# Erase flash
esptool.py --port /dev/ttyUSB0 erase_flash

# Flash MicroPython
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 esp32-firmware.bin
```

### Project Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Configure WiFi and MQTT**
   ```bash
   cp config.py.example config.py
   # Edit config.py with your credentials
   ```

3. **Upload files to device**
   ```bash
   # Using ampy
   ampy --port /dev/ttyUSB0 put main.py
   ampy --port /dev/ttyUSB0 put config.py
   ampy --port /dev/ttyUSB0 put lib/

   # Or using rshell
   rshell --port /dev/ttyUSB0
   cp main.py /pyboard/
   cp config.py /pyboard/
   cp -r lib/ /pyboard/
   ```

4. **Connect to serial console**
   ```bash
   # Using screen
   screen /dev/ttyUSB0 115200

   # Or use Thonny's built-in serial monitor
   ```

## Project Structure

```
.
├── main.py                 # Main application entry point
├── boot.py                 # Runs on device boot
├── config.py               # Configuration (WiFi, MQTT, etc.)
├── lib/                    # Libraries and modules
│   ├── wifi.py            # WiFi management
│   ├── mqtt_client.py     # MQTT client wrapper
│   ├── sensors/           # Sensor drivers
│   │   ├── dht.py        # DHT11/22 driver
│   │   ├── bme280.py     # BME280 driver
│   │   └── ...
│   └── utils.py          # Helper functions
│
├── tests/                 # Test scripts
├── docs/                  # Documentation
│   ├── wiring.md         # Hardware wiring diagrams
│   ├── setup.md          # Setup instructions
│   └── troubleshooting.md
│
├── tools/                 # Development tools
│   ├── flash.sh          # Flashing script
│   └── upload.sh         # File upload script
│
├── requirements.txt       # Python tools dependencies
└── README.md             # This file
```

## Configuration

### config.py Example

```python
# WiFi Configuration
WIFI_SSID = 'your-wifi-ssid'
WIFI_PASSWORD = 'your-wifi-password'

# MQTT Configuration
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'device-001'
MQTT_USERNAME = None  # Optional
MQTT_PASSWORD = None  # Optional
MQTT_TOPIC = 'iot/devices/001'

# Device Configuration
DEVICE_ID = 'device-001'
DEVICE_NAME = 'Temperature Sensor'
LOCATION = 'Living Room'

# Sensor Configuration
SENSOR_READ_INTERVAL = 60  # seconds
DATA_SEND_INTERVAL = 300   # seconds

# Power Management
ENABLE_DEEP_SLEEP = False
SLEEP_DURATION = 60  # seconds

# Pin Configuration
DHT_PIN = 15
LED_PIN = 2
BUTTON_PIN = 0
```

## Main Application

### main.py Example

```python
import time
import machine
from lib.wifi import connect_wifi
from lib.mqtt_client import MQTTClient
from lib.sensors.dht import DHT22
import config

# Initialize hardware
led = machine.Pin(config.LED_PIN, machine.Pin.OUT)
dht_sensor = DHT22(machine.Pin(config.DHT_PIN))

# Connect to WiFi
print('Connecting to WiFi...')
if connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD):
    print('WiFi connected!')
    led.on()  # Indicate connection
else:
    print('WiFi connection failed')
    # Handle error

# Setup MQTT
mqtt = MQTTClient(
    client_id=config.MQTT_CLIENT_ID,
    server=config.MQTT_BROKER,
    port=config.MQTT_PORT
)

try:
    mqtt.connect()
    print('MQTT connected!')
except Exception as e:
    print(f'MQTT connection failed: {e}')

# Main loop
last_read_time = 0

while True:
    try:
        current_time = time.time()

        # Read sensor at intervals
        if current_time - last_read_time >= config.SENSOR_READ_INTERVAL:
            temperature = dht_sensor.temperature()
            humidity = dht_sensor.humidity()

            print(f'Temperature: {temperature}°C, Humidity: {humidity}%')

            # Publish to MQTT
            payload = f'{{"temp": {temperature}, "humidity": {humidity}, "device": "{config.DEVICE_ID}"}}'
            mqtt.publish(config.MQTT_TOPIC, payload)

            last_read_time = current_time

        # Small delay to prevent CPU hogging
        time.sleep(0.1)

    except KeyboardInterrupt:
        print('Interrupted by user')
        break
    except Exception as e:
        print(f'Error in main loop: {e}')
        time.sleep(5)  # Wait before retry

# Cleanup
mqtt.disconnect()
led.off()
```

## WiFi Management

### Auto-Reconnect

```python
import network
import time

def connect_wifi(ssid, password, timeout=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f'Connecting to {ssid}...')
        wlan.connect(ssid, password)

        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                return False
            time.sleep(0.5)

    print('Network config:', wlan.ifconfig())
    return True
```

## MQTT Communication

### Publish Data

```python
# Publish sensor data
topic = 'sensors/temperature'
payload = '{"value": 25.5, "unit": "C"}'
mqtt.publish(topic, payload)
```

### Subscribe to Commands

```python
def on_message(topic, msg):
    print(f'Received: {topic} - {msg}')
    if topic == b'commands/led':
        if msg == b'on':
            led.on()
        elif msg == b'off':
            led.off()

mqtt.set_callback(on_message)
mqtt.subscribe('commands/led')

# Check for messages in main loop
mqtt.check_msg()
```

## Power Management

### Deep Sleep Mode

```python
import machine
import time

# Read sensor
temperature = read_temperature()

# Send data
send_to_cloud(temperature)

# Deep sleep for 5 minutes
print('Entering deep sleep...')
machine.deepsleep(300000)  # 300,000 ms = 5 minutes
```

### Light Sleep Mode

```python
# Light sleep (faster wake, higher power)
machine.lightsleep(60000)  # 1 minute
```

## Testing

### Unit Tests

```bash
# Run tests on host machine (simulation)
python -m pytest tests/

# Test specific module
python tests/test_sensors.py
```

### Hardware Testing

```python
# tests/test_led.py
from machine import Pin
import time

led = Pin(2, Pin.OUT)

# Blink test
for i in range(5):
    led.on()
    time.sleep(0.5)
    led.off()
    time.sleep(0.5)

print('LED test passed!')
```

## Deployment

### OTA Updates

```python
# Simple OTA implementation
import urequests

def check_for_update():
    url = 'http://your-server.com/firmware/version.txt'
    response = urequests.get(url)
    latest_version = response.text.strip()

    if latest_version != CURRENT_VERSION:
        download_update()
        install_update()
        machine.reset()
```

### Production Checklist

- [ ] WiFi credentials secured (not in git)
- [ ] MQTT credentials secured
- [ ] Error handling implemented
- [ ] Watchdog timer enabled
- [ ] Power management configured
- [ ] LED status indicators working
- [ ] Remote logging configured
- [ ] OTA updates tested
- [ ] Hardware connections secure
- [ ] Enclosure/housing prepared

## Troubleshooting

### Device Not Connecting

```bash
# Check USB connection
ls /dev/tty*  # Look for /dev/ttyUSB0 or similar

# Check driver installation
# Install CH340/CP210x driver if needed

# Try different baud rate
screen /dev/ttyUSB0 9600
```

### WiFi Issues

```python
# Check WiFi status
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(wlan.scan())  # List available networks
```

### Memory Issues

```python
# Check free memory
import gc
gc.collect()
print(gc.mem_free())

# Free up memory
gc.collect()
```

### Reset Device

```python
# Soft reset
import machine
machine.soft_reset()

# Hard reset
machine.reset()
```

## Wiring Diagrams

See `docs/wiring.md` for detailed wiring diagrams for common sensors and actuators.

## Security

- Use WPA2 for WiFi
- Use TLS/SSL for MQTT (port 8883)
- Don't hardcode credentials (use config files, not in git)
- Implement authentication for OTA updates
- Validate all remote commands
- Use secure boot (if available)

## Performance

- Minimize WiFi connections (batch data)
- Use deep sleep for battery-powered devices
- Buffer data locally when offline
- Optimize sensor reading intervals
- Use interrupts instead of polling when possible

## Resources

- [MicroPython Documentation](https://docs.micropython.org/)
- [CircuitPython Documentation](https://circuitpython.org/)
- [Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/)
- [ESP32 Documentation](https://docs.espressif.com/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on actual hardware
5. Submit a pull request

## License

[Your License Here]

## Support

- Issues: [GitHub Issues]
- Forum: [Your Forum URL]
- Email: iot-support@your-company.com

---

**Built with Claude Code Generator** - IoT development made simple.
