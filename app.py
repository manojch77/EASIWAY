from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# ✅ Initialize Firebase only once
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://easy-22b8-default-rtdb.firebaseio.com/'
    })

@app.route('/', methods=['GET'])
def index():
    return "✅ Flask middleware is running and ready to receive GPS POST data", 200

@app.route('/', methods=['POST'])
def receive_data():
    print("\n📥 Incoming POST from Traccar Client")

    # Debug all incoming content
    print("🔸 Headers:", dict(request.headers))
    print("🔸 Form:", request.form)
    print("🔸 Raw Body:", request.get_data(as_text=True))

    # Try parsing JSON
    json_data = request.get_json(silent=True)
    print("🔹 JSON body:", json_data)

    # Extract correctly from Traccar's nested format
    device_id = None
    lat = None
    lon = None

    if json_data:
        device_id = json_data.get("device_id")  # ✅ correct key for ID
        location = json_data.get("location", {})
        coords = location.get("coords", {})
        lat = coords.get("latitude")
        lon = coords.get("longitude")

    print(f"🔍 Parsed: ID={device_id}, lat={lat}, lon={lon}")

    # Send to Firebase if complete
    if device_id and lat and lon:
        try:
            db.reference(f"buses/{device_id}/location").set({
                "lat": float(lat),
                "lng": float(lon)
            })
            print(f"✅ Firebase updated: buses/{device_id}/location → ({lat}, {lon})")
            return "Location updated", 200
        except Exception as e:
            print(f"❌ Firebase error: {e}")
            return "Firebase error", 500

    print("❌ Missing id, lat, or lon")
    return "Missing id, lat, or lon", 400

if __name__ == '__main__':
    print("🚀 Flask running on port 5055")
    app.run(host="0.0.0.0", port=5055, debug=True)
