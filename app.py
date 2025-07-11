from flask import Flask, render_template_string, request
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)


html_page = """
<!DOCTYPE html>
<html>
<head>
  <title>Get GPS Location</title>
</head>
<body>
  <script>
    function sendLocation(position) {
      fetch('/location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        })
      }).then(res => console.log("GPS Location saved."));
    }

    function fallbackToIP() {
      fetch('/get_ip_location', {
        method: 'POST'
      }).then(res => {
        if (res.ok) {
          console.log("IP-based location saved.");
        } else {
          console.log("Failed to get location via IP.");
        }
      });
    }

    function errorHandler(error) {
      console.warn("GPS error:", error.message);
      fallbackToIP();  // fallback if GPS fails
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(sendLocation, errorHandler);
    } else {
      fallbackToIP();  // if geolocation not supported
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_page)


@app.route("/location", methods=["POST"])
def location():
    data = request.get_json()
    lat = data.get("latitude")
    lon = data.get("longitude")


    with open("location.txt", "a") as f:
        time_stamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"Latitude :{lat}  longitude: {lon} time: {time_stamp} [gps exact location]\n")

    return {"message": "ok"}, 200


@app.route("/get_ip_location", methods=["POST"])
def ip_location():
    ip_addr = request.remote_addr

    response = requests.get(f'https://ipinfo.io/{ip_addr}/json')
    data = response.json()

    print("data: ", data)
    if "loc" in data:
      location = data["loc"].split(",")
      lat, lon = location[0], location[1]

      with open("location.txt", "a") as f:
          time_stamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
          f.write(f"Latitude :{lat}  longitude: {lon} time: {time_stamp} [30 km approx location]\n")

      return {"message": "ok"}, 200
    
    return {"message": "location not found"}, 400

    

if __name__ == "__main__":
    app.run(debug=True)

