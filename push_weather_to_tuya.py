import requests
import time
import hmac
import hashlib
import json
import os

# === CONFIGURATION ===
# Read from environment variables for security (GitHub Actions)
# Set these as GitHub Secrets or environment variables
IQAIR_API_KEY = os.getenv("IQAIR_API_KEY")
TUYA_CLIENT_ID = os.getenv("TUYA_CLIENT_ID")
TUYA_CLIENT_SECRET = os.getenv("TUYA_CLIENT_SECRET")
TUYA_DEVICE_ID = os.getenv("TUYA_DEVICE_ID")
TUYA_API_ENDPOINT = os.getenv("TUYA_API_ENDPOINT") or "https://openapi.tuyaeu.com"

# === VALIDATION ===
def validate_config():
    """Validate that all required environment variables are set"""
    required_vars = {
        "IQAIR_API_KEY": IQAIR_API_KEY,
        "TUYA_CLIENT_ID": TUYA_CLIENT_ID,
        "TUYA_CLIENT_SECRET": TUYA_CLIENT_SECRET,
        "TUYA_DEVICE_ID": TUYA_DEVICE_ID
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# === STEP 1: Get weather data from IQAir ===
def get_weather():
    url = f"https://api.airvisual.com/v2/city?city=Ivano%20Frankivsk&state=Ivano%20Frankivsk&country=Ukraine&key={IQAIR_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"IQAir API error: {response.status_code}")
    data = response.json()
    weather = data["data"]["current"]["weather"]
    temperature = weather["tp"]        # Celsius
    humidity = weather["hu"]           # %
    return temperature, humidity

# === STEP 2: Get Tuya cloud access token ===
def get_tuya_token():
    t = str(int(time.time() * 1000))
    # For GET requests with no body, the Content-SHA256 is a fixed value
    content_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    
    # Construct stringToSign
    # HTTPMethod + "\n" + Content-SHA256 + "\n" + Headers + "\n" + Url
    # Headers are empty for token requests.
    # Url is the path + query.
    
    url_path = "/v1.0/token"
    url_query = "grant_type=1"
    
    string_to_sign = f"GET\n{content_sha256}\n\n/{url_path.lstrip('/')}?{url_query}"

    message = TUYA_CLIENT_ID + t + string_to_sign
    sign = hmac.new(
        TUYA_CLIENT_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()

    headers = {
        "client_id": TUYA_CLIENT_ID,
        "sign": sign,
        "t": t,
        "sign_method": "HMAC-SHA256"
    }

    url = f"{TUYA_API_ENDPOINT}{url_path}?{url_query}"
    res = requests.get(url, headers=headers)

    print(">> STATUS:", res.status_code)
    print(">> BODY:", res.text)

    if not res.ok:
        raise Exception("Bad HTTP response")

    data = res.json()
    if not data.get("success"):
        raise Exception(f"Tuya error: {data}")

    return data["result"]["access_token"]

# === STEP 3: Send weather data to Tuya virtual device ===
def push_to_tuya(temp, hum, token):
    temp_scaled = int(temp * 10)  # Tuya expects temp * 10
    hum_int = int(hum)

    # Your inner properties
    props = {
        "va_temperature": temp_scaled,
        "va_humidity": hum_int
    }

    # Serialize the inner dict to a JSON string
    props_str = json.dumps(props)
    
    # Wrap it inside the outer structure
    payload = {
        "properties": props_str  # This is a string, not a dict
    }

    t = str(int(time.time() * 1000))
    headers = {
        "client_id": TUYA_CLIENT_ID,
        "access_token": token,
        "sign_method": "HMAC-SHA256",
        "t": t
    }

    url_path = f"/v2.0/cloud/thing/{TUYA_DEVICE_ID}/shadow/properties/issue"
    
    # Calculate Content-SHA256 for the payload
    payload_str = json.dumps(payload, separators=(',', ':')) # Ensure no spaces for consistent hash
    content_sha256 = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

    # Construct stringToSign for service management operations
    # str = client_id + access_token + t + nonce + stringToSign
    # stringToSign = HTTPMethod + "\n" + Content-SHA256 + "\n" + Headers + "\n" + Url
    # Nonce is optional and not used here. Headers are empty.
    
    string_to_sign_part = f"POST\n{content_sha256}\n\n{url_path}"
    
    # Use client_id + access_token + t + stringToSign for signature
    message = TUYA_CLIENT_ID + headers["access_token"] + t + string_to_sign_part
    sign = hmac.new(
        TUYA_CLIENT_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    
    headers["sign"] = sign
    # Add Content-Type header
    headers["Content-Type"] = "application/json"

    url = f"{TUYA_API_ENDPOINT}{url_path}"

    # --- DEBUG PRINTS ---
    print("\n--- TUYA SIGNATURE DEBUG ---")
    print("Payload (dict):", payload)
    print("Payload (JSON):", payload_str)
    print("Content-SHA256:", content_sha256)
    print("String to sign:", string_to_sign_part)
    print("Message to sign:", message)
    print("Sign:", sign)
    print("Headers:", headers)
    print("URL:", url)
    print("--- END DEBUG ---\n")

    res = requests.post(url, data=payload_str, headers=headers)

    if res.status_code != 200:
        raise Exception(f"Failed to push data to Tuya: {res.status_code}, {res.text}")
    print("DEBUG res.text:", res.text)
    print("✅ Data sent to Tuya:", payload_str)

# === MAIN ===
if __name__ == "__main__":
    print(f"🚀 Starting weather sync at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    try:
        # Validate configuration first
        validate_config()
        print("✅ Configuration validated")
        
        temp, hum = get_weather()
        print(f"🌤 Weather from IQAir: {temp}°C, {hum}% RH")
        token = get_tuya_token()
        push_to_tuya(temp, hum, token)
        print(f"✅ Weather sync completed successfully at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    except Exception as e:
        print(f"❌ Error at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}: {str(e)}")
        exit(1)  # Exit with error code for GitHub Actions