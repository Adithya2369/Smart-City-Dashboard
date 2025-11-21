from google.oauth2 import service_account
import google.auth.transport.requests

SERVICE_ACCOUNT_FILE = "YOUR_SERVICE_ACCOUNT.json"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def generate_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

if __name__ == "__main__":
    token = generate_token()
    print("\n=== COPY THIS ACCESS TOKEN TO ESP32 CODE ===\n")
    print(token)
    print("\n=============================================\n")
