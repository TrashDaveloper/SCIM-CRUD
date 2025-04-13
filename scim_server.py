from flask import Flask, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

# In-Memory-Speicher
devices = {}
device_counter = 1

# Trustpoint SCIM Schema -> in einer öffentlichen Dokumentation vermerken, damit Clients dies erfüllen können
TRUSTPOINT_SCHEMA = {
    "schemas": ["urn:ietf:params:scim:schemas:trustpoint:2.0:Device"],
     "attributes": [
    {
      "name": "uniqueName",
      "type": "string",
      "multiValued": False,
      "description": "Unique name for the device",
      "required": True,
      "caseExact": True,
      "mutability": "readWrite",
      "returned": "always",
      "uniqueness": "server"
    },
    {
      "name": "domainName",
      "type": "string",
      "multiValued": False,
      "description": "Unique name of the domain to which the device belongs",
      "required": True
    },
    {
      "name": "createdAt",
      "type": "dateTime",
      "description": "Timestamp when the device was created",
      "required": False
    },
    {
      "name": "certificates",
      "type": "complex",
      "multiValued": True,
      "description": "Certificates associated with this device",
      "required": False,
      "subAttributes": [
        { "name": "commonName", "type": "string" },
        { "name": "sha256Fingerprint", "type": "string" },
        { "name": "serialNumber", "type": "string" },
        { "name": "issuer", "type": "string" },
        { "name": "subject", "type": "string" },
        { "name": "notValidBefore", "type": "dateTime" },
        { "name": "notValidAfter", "type": "dateTime" },
        { "name": "certPem", "type": "string" },
      ]
    }
  ]
}
# Helper-Funktion für Timestamps (Metadata)
def current_timestamp():
    germany_tz = pytz.timezone('Europe/Berlin')
    return datetime.now(germany_tz).isoformat()

 # SCIM-Validierung
 # Schema prüfen
def validate_device_schema(data):
    # Überprüfen, ob die SCIM-Schema-URN korrekt ist
    if "schemas" not in data or "urn:ietf:params:scim:schemas:trustpoint:2.0:Device" not in data["schemas"]:
        return False, "Invalid SCIM schema"

    # Überprüfen der erforderlichen Felder
    required_attributes = ["uniqueName", "domainName"]
    for attr in required_attributes:
        if attr not in data or not data[attr]:
            return False, f"Missing required attribute: '{attr}'"

    # Optionale Felder prüfen
    if "certificates" in data:
        for cert in data["certificates"]:
            if not isinstance(cert, dict):
                return False, "Each certificate must be a JSON object"
            sub_attributes = ["commonName", "sha256Fingerprint", "serialNumber"]
            for sub_attr in sub_attributes:
                if sub_attr in cert and not isinstance(cert[sub_attr], str):
                    return False, f"Certificate attribute '{sub_attr}' must be a string"


                # Beispiel für komplexe Attribute
                for sub_attr_name, sub_attr_type in [
                    ("commonName", "string"),
                    ("sha256Fingerprint", "string"),
                    ("serialNumber", "string"),
                    ("issuer", "string"),
                    ("subject", "string"),
                    ("notValidBefore", "dateTime"),
                    ("notValidAfter", "dateTime"),
                    ("certPem", "string"),
                ]:
                    if sub_attr_name in cert:
                        if sub_attr_type == "string" and not isinstance(cert[sub_attr_name], str):
                            return False, f"Sub-attribute '{sub_attr_name}' must be of type {sub_attr_type}"
                        elif sub_attr_type == "dateTime" and not isinstance(cert[sub_attr_name], str):
                            try:
                                # Optional: Überprüfen, ob das Datum gültig ist
                                datetime.fromisoformat(cert[sub_attr_name])
                            except ValueError:
                                return False, f"Sub-attribute '{sub_attr_name}' must be a valid dateTime"

    is_valid, error_message = validate_attributes(data, TRUSTPOINT_SCHEMA)
    if not is_valid:
        return False, error_message

    return True, None


def validate_attributes(data, schema):
    for attr in schema["attributes"]:
        name = attr["name"]
        required = attr.get("required", False)
        attr_type = attr["type"]
        multi_valued = attr.get("multiValued", False)

        # Überprüfen, ob ein erforderliches Attribut fehlt
        if required and name not in data:
            return False, f"Missing required attribute: '{name}'"

        # Wenn das Attribut vorhanden ist, den Typ überprüfen
        if name in data:
            value = data[name]
            if multi_valued:
                if not isinstance(value, list):
                    return False, f"Attribute '{name}' must be a list"
                for item in value:
                    if not isinstance(item, str) and attr_type == "string":
                        return False, f"Items in '{name}' must be of type {attr_type}"
            else:
                if not isinstance(value, str) and attr_type == "string":
                    return False, f"Attribute '{name}' must be of type {attr_type}"


    return True, None


# Geräte erstellen (POST /scim/v2/Devices)
@app.route('/scim/v2/Devices', methods=['POST'])
def create_device():
    global device_counter
    data = request.json

    # SCIM-Validierung
    is_valid, error_message = validate_device_schema(data)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    # Device ID generieren
    device_id = str(device_counter)
    device_counter += 1

    # Gerät anlegen gemäß SCIM-Schema
    device = {
        "id": device_id,  # ID des Geräts
        "schemas": ["urn:ietf:params:scim:schemas:trustpoint:2.0:Device"],  # SCIM-Schema des Geräts
        "uniqueName": data["uniqueName"],  # Name des Geräts (erforderlich)
        "domainName": data["domainName"],  # Domainname des Geräts (erforderlich)
        "createdAt": current_timestamp(),  # Erstellungszeitpunkt
        "certificates": data.get("certificates", []),  # Zertifikate (optional)
        "meta": {  # Metadaten
            "resourceType": "Device",
            "created": current_timestamp(),  # Zeitstempel der Erstellung
            "lastModified": current_timestamp()  # Zeitstempel der letzten Änderung
        }
    }

    # Gerät im Speicher ablegen
    devices[device_id] = device

    # Erfolgreiche Antwort zurückgeben
    return jsonify(device), 201


# Geräte abrufen (GET /scim/v2/Devices)
@app.route('/scim/v2/Devices', methods=['GET'])
def list_devices():
    device_list = list(devices.values())
    return jsonify({
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(device_list),
        "Resources": device_list
    }), 200

# Einzelnes Gerät abrufen (GET /scim/v2/Devices/<id>)
@app.route('/scim/v2/Devices/<device_id>', methods=['GET'])
def get_device(device_id):
    device = devices.get(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    return jsonify(device), 200

# Gerät aktualisieren (PUT /scim/v2/Devices/<id>)
@app.route('/scim/v2/Devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    data = request.json
    print(data)

    device = devices.get(device_id)

    if not device:
        return jsonify({"error": "Device not found"}), 404

    # SCIM-Validierung
    is_valid, error_message = validate_device_schema(data)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    device.update({
        "uniqueName": data.get("uniqueName", device["uniqueName"]),
        "domainName": data.get("domainName", device["domainName"]),
        "certificates": data.get("certificates", device["certificates"]),
        "meta": {
            "resourceType": "Device",
            "created": device["meta"]["created"],
            "lastModified": current_timestamp()
        }
    })

    return jsonify(device), 200

# Gerät löschen (DELETE /scim/v2/Devices/<id>)
@app.route('/scim/v2/Devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    if device_id in devices:
        del devices[device_id]
        return '', 204
    return jsonify({"error": "Device not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
