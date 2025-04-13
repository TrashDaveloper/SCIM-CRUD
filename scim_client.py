import requests
import json

BASE_URL = "http://localhost:5000/scim/v2/Devices"

# Hilfsfunktion für schöne Ausgabe
def pretty_print(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=4))
    except json.JSONDecodeError:
        print(response.text)

# Beispiel-Gerät
def create_device():
    payload = {
        "schemas": ["urn:ietf:params:scim:schemas:trustpoint:2.0:Device"],
        "uniqueName": "device01",
        "domainName": "example.com",
        "certificates": [
            {
                "commonName": "cert01",
                "sha256Fingerprint": "abcdef123456",
                "notValidBefore": "2025-01-01T00:00:00Z",
                "notValidAfter": "2026-01-01T00:00:00Z"
            }
        ]
    }
    response = requests.post(BASE_URL, json=payload)
    pretty_print(response)

# Alle Geräte abrufen
def list_devices():
    response = requests.get(BASE_URL)
    pretty_print(response)

# Einzelnes Gerät abrufen
def get_device(device_id):
    response = requests.get(f"{BASE_URL}/{device_id}")
    pretty_print(response)

# Gerät aktualisieren
def update_device(device_id):
    payload = {
        "schemas": ["urn:ietf:params:scim:schemas:trustpoint:2.0:Device"],
        "uniqueName": "updated_device01",
        "domainName": "updated-example.com",
        "certificates": [
            {
                "commonName": "updated_cert01",
                "sha256Fingerprint": "updated_abcdef123456",
                "notValidBefore": "2025-01-01T00:00:00Z",
                "notValidAfter": "2027-01-01T00:00:00Z"
            }
        ]
    }
    response = requests.put(f"{BASE_URL}/{device_id}", json=payload)
    pretty_print(response)

# Gerät löschen
def delete_device(device_id):
    response = requests.delete(f"{BASE_URL}/{device_id}")
    pretty_print(response)

if __name__ == "__main__":
    print("Creating a device...")
    create_device()

    print("\nListing all devices...")
    list_devices()

    # Assuming the first device created has ID 1
    device_id = "1"

    print("\nGetting the device...")
    get_device(device_id)

    print("\nUpdating the device...")
    update_device(device_id)

    print("\nListing all devices after update...")
    list_devices()

    print("\nDeleting the device...")
    delete_device(device_id)

    print("\nListing all devices after deletion...")
    list_devices()
