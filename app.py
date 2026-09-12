import geoip2.database
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# Path to your GeoLite2 database file
DATABASE_PATH = "GeoLite2-City.mmdb"

def get_client_ip(req):
    """Get the real client IP, handles proxy headers."""
    # Check for standard proxy headers first
    if req.headers.get("X-Forwarded-For"):
        # X-Forwarded-For can contain a list, the first is the original client
        return req.headers.get("X-Forwarded-For").split(",")[0].strip()
    # Fallback to the direct connection address
    return req.remote_addr
    

def get_location_from_ip(ip_address):
    """Look up the location for a given IP using GeoIP2."""
    try:
        with geoip2.database.Reader(DATABASE_PATH) as reader:
            response = reader.city(ip_address)
            return {
                "country": response.country.name,
                "city": response.city.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "timezone": response.location.time_zone
            }
    except geoip2.errors.AddressNotFoundError:
        return {"error": "Address not found in database"}
    except Exception as e:
        return {"error": str(e)}
        
        

@app.route("/")
def index():
    # 1. Get the visitor's IP address
    client_ip = get_client_ip(request)
    
    # 2. Look up the location based on that IP
    location = get_location_from_ip(client_ip)
    
    # 3. Log the results
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{now} | IP: {client_ip} | Location: {location}"
    
    print(log_line)  # Also print to console for debugging
    with open("location_log.txt", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    
    # 4. Show a simple message to the user
    return f"""
    <h1>Location Logged (via IP)</h1>
    <p>IP Address: {client_ip}</p>
    <p>Estimated Location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)