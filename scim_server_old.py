from flask import Flask, request, jsonify
import pytz
from datetime import datetime

app = Flask(__name__)


#https://datatracker.ietf.org/doc/html/rfc7643#section-4.3


# In-Memory-Speicher
users = {}
machines = {}
certificates = {}

user_counter = 1
machine_counter = 1
certificate_counter = 1

# Helper-Funktion zum Generieren von Timestamps
def current_timestamp():
    # Zeitzone für Deutschland (MEZ/MESZ)
    germany_tz = pytz.timezone('Europe/Berlin')
    return datetime.now(germany_tz).isoformat()

# 🟢 Benutzer erstellen (POST /scim/v2/Users)
@app.route('/scim/v2/Users', methods=['POST'])
def create_user():
    global user_counter
    data = request.json

    if "schemas" not in data or "urn:ietf:params:scim:schemas:core:2.0:User" not in data["schemas"]:
        return jsonify({"error": "Invalid SCIM schema"}), 400

    user_id = str(user_counter)
    user_counter += 1

    user = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user_id,
        "userName": data.get("userName"),
        "name": data.get("name"),
        "emails": data.get("emails"),
        "meta": {
            "resourceType": "User",
            "created": current_timestamp(),
            "lastModified": current_timestamp()
        }
    }

    users[user_id] = user
    return jsonify(user), 201

# 🔹 Maschinen erstellen (POST /scim/v2/Machines)
@app.route('/scim/v2/Machines', methods=['POST'])
def create_machine():
    global machine_counter
    data = request.json

    if "schemas" not in data or "urn:ietf:params:scim:schemas:extension:machine:2.0:Machine" not in data["schemas"]:
        return jsonify({"error": "Invalid SCIM schema"}), 400

    machine_id = str(machine_counter)
    machine_counter += 1

    machine = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:machine:2.0:Machine"],
        "id": machine_id,
        "machineName": data.get("machineName"),
        "attributes": data.get("attributes"),
        "certificates": data.get("certificates"),
        "meta": {
            "resourceType": "Machine",
            "created": current_timestamp(),
            "lastModified": current_timestamp()
        }
    }

    machines[machine_id] = machine
    return jsonify(machine), 201

# 🔵 Zertifikate erstellen (POST /scim/v2/Certificates)
@app.route('/scim/v2/Certificates', methods=['POST'])
def create_certificate():
    global certificate_counter
    data = request.json

    if "schemas" not in data or "urn:ietf:params:scim:schemas:extension:certificate:2.0:Certificate" not in data["schemas"]:
        return jsonify({"error": "Invalid SCIM schema"}), 400

    certificate_id = str(certificate_counter)
    certificate_counter += 1

    certificate = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:certificate:2.0:Certificate"],
        "id": certificate_id,
        "certificateType": data.get("certificateType"),
        "issuedTo": data.get("issuedTo"),
        "validFrom": data.get("validFrom"),
        "validTo": data.get("validTo"),
        "meta": {
            "resourceType": "Certificate",
            "created": current_timestamp(),
            "lastModified": current_timestamp()
        }
    }

    certificates[certificate_id] = certificate
    return jsonify(certificate), 201

# 🗾 Benutzer, Maschinen und Zertifikate abrufen
@app.route('/scim/v2/<resource_type>', methods=['GET'])
def list_resources(resource_type):
    resource_map = {
        "Users": users,
        "Machines": machines,
        "Certificates": certificates
    }

    if resource_type not in resource_map:
        return jsonify({"error": "Resource type not found"}), 404

    resources = list(resource_map[resource_type].values())
    return jsonify({
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(resources),
        "Resources": resources
    }), 200

# 🔒 Einzelne Ressourcen abrufen
@app.route('/scim/v2/<resource_type>/<resource_id>', methods=['GET'])
def get_resource(resource_type, resource_id):
    resource_map = {
        "Users": users,
        "Machines": machines,
        "Certificates": certificates
    }

    if resource_type not in resource_map:
        return jsonify({"error": "Resource type not found"}), 404

    resource = resource_map[resource_type].get(resource_id)
    if resource:
        return jsonify(resource), 200
    else:
        return jsonify({"error": f"{resource_type[:-1]} not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
