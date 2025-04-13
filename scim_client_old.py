import requests

class ScimClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def create_user(self, user_data):
        url = f"{self.base_url}/scim/v2/Users"
        response = requests.post(url, json=user_data)
        return self._handle_response(response)

    def create_machine(self, machine_data):
        url = f"{self.base_url}/scim/v2/Machines"
        response = requests.post(url, json=machine_data)
        return self._handle_response(response)

    def create_certificate(self, certificate_data):
        url = f"{self.base_url}/scim/v2/Certificates"
        response = requests.post(url, json=certificate_data)
        return self._handle_response(response)

    def get_resources(self, resource_type):
        url = f"{self.base_url}/scim/v2/{resource_type}"
        response = requests.get(url)
        return self._handle_response(response)

    def get_resource_by_id(self, resource_type, resource_id):
        url = f"{self.base_url}/scim/v2/{resource_type}/{resource_id}"
        response = requests.get(url)
        return self._handle_response(response)

    @staticmethod
    def _handle_response(response):
        if response.ok:
            return response.json()
        else:
            return {"error": response.status_code, "message": response.text}

# Beispiel-Verwendung des SCIM-Clients
if __name__ == "__main__":
    client = ScimClient("http://localhost:5000")

    # Benutzer erstellen
    user_data = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": "johndoe",
        "name": {
            "givenName": "John",
            "familyName": "Doe"
        },
        "emails": [
            {
                "value": "johndoe@example.com",
                "type": "work",
                "primary": True
            }
        ]
    }
    print("Creating user:", client.create_user(user_data))

    # Maschine erstellen
    machine_data = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:machine:2.0:Machine"],
        "machineName": "machine001",
        "attributes": {"os": "Linux", "version": "Ubuntu 22.04"},
        "certificates": []
    }
    print("Creating machine:", client.create_machine(machine_data))

    # Zertifikat erstellen
    certificate_data = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:certificate:2.0:Certificate"],
        "certificateType": "SSL",
        "issuedTo": "machine001",
        "validFrom": "2025-01-01T00:00:00Z",
        "validTo": "2026-01-01T00:00:00Z"
    }
    print("Creating certificate:", client.create_certificate(certificate_data))

    # Ressourcen abrufen
    print("Listing users:", client.get_resources("Users"))
    print("Listing machines:", client.get_resources("Machines"))
    print("Listing certificates:", client.get_resources("Certificates"))

    # Einzelne Ressource abrufen
    print("Getting user by ID:", client.get_resource_by_id("Users", "1"))
