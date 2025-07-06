# Tuya Weather Integration

A Python script that fetches weather data from IQAir API and pushes it to a Tuya virtual device for home automation integration.

## Features

- 🌤️ Fetches real-time weather data (temperature and humidity) from IQAir API
- 🔐 Authenticates with Tuya Cloud API using HMAC-SHA256 signature
- 📊 Pushes weather data to a Tuya virtual device
- 🛡️ Secure API key management
- 📝 Comprehensive error handling and debugging

## Prerequisites

- Python 3.6+
- Tuya Cloud Developer Account
- IQAir API Key
- Tuya Virtual Device

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd tuya_weather
```

2. Install required dependencies:
```bash
pip install requests
```

## Configuration

Update the configuration variables in `push_weather_to_tuya.py`:

```python
# === CONFIGURATION ===
IQAIR_API_KEY = "your_iqair_api_key"
TUYA_CLIENT_ID = "your_tuya_client_id"
TUYA_CLIENT_SECRET = "your_tuya_client_secret"
TUYA_DEVICE_ID = "your_tuya_virtual_device_id"
TUYA_API_ENDPOINT = "https://openapi.tuyaeu.com"  # or openapi.tuyacn.com for China
```

### Getting API Keys

1. **IQAir API Key**: Sign up at [IQAir](https://www.iqair.com/) and get your API key
2. **Tuya Credentials**: 
   - Create a Tuya Cloud Developer account
   - Create a cloud project
   - Get your Client ID and Client Secret
   - Create a virtual device and note its Device ID

## Usage

Run the script to fetch weather data and push it to Tuya:

```bash
python3 push_weather_to_tuya.py
```

The script will:
1. Fetch current weather data for Ivano-Frankivsk, Ukraine
2. Authenticate with Tuya Cloud API
3. Push temperature and humidity data to your virtual device

## Output

The script provides detailed output including:
- Weather data from IQAir
- Tuya authentication status
- API request details and signatures
- Success/error messages

Example output:
```
🌤 Weather from IQAir: 29°C, 39% RH
✅ Data sent to Tuya: {"properties":"{\"va_temperature\": 290, \"va_humidity\": 39}"}
```

## API Endpoints

- **IQAir**: `https://api.airvisual.com/v2/city` - Weather data
- **Tuya**: `https://openapi.tuyaeu.com` - Device management

## Security

- API keys are stored in the script (consider using environment variables for production)
- HMAC-SHA256 signature authentication for Tuya API
- HTTPS communication for all API calls

## Troubleshooting

### Common Issues

1. **"sign invalid" error**: Check your Tuya credentials and ensure system time is synchronized
2. **API rate limits**: IQAir and Tuya have rate limits - add delays if needed
3. **Network issues**: Ensure internet connectivity and firewall settings

### Debug Mode

The script includes comprehensive debug output. Check the console output for:
- API response status codes
- Request/response bodies
- Signature calculation details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions:
- Check the troubleshooting section
- Review Tuya and IQAir API documentation
- Open an issue on GitHub 