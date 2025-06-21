import os
import msal
import requests
import json
import time

# --- Configuration ---
# These values will be loaded from GitHub secrets (environment variables)
TENANT_ID = os.getenv('TENANT_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
# Updated list of endpoints that work with Application permissions
GRAPH_API_ENDPOINTS = [
    # Get a list of users in the organization
    "https://graph.microsoft.com/v1.0/users",
    # Get the root SharePoint site
    "https://graph.microsoft.com/v1.0/sites/root",
    # Get a list of applications in the organization
    "https://graph.microsoft.com/v1.0/applications"
]

def get_access_token():
    """Acquires an access token from Azure AD."""
    print("Attempting to acquire access token...")
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_silent(SCOPE, account=None)
    if not result:
        print("No suitable token in cache, getting a new one from AAD.")
        result = app.acquire_token_for_client(scopes=SCOPE)
    
    if "access_token" in result:
        print("Access token acquired successfully.")
        return result['access_token']
    else:
        print("Error acquiring token:")
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))
        raise Exception("Could not acquire access token")

def call_graph_api(access_token, endpoint):
    """Calls a Microsoft Graph API endpoint."""
    headers = {'Authorization': 'Bearer ' + access_token}
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        print(f"Successfully called endpoint: {endpoint.split('/v1.0/')[-1]}")
    except requests.exceptions.RequestException as e:
        print(f"Error calling endpoint {endpoint}: {e}")

def main():
    """Main function to run the renewal process."""
    print(f"Script started at {time.ctime()}")
    try:
        if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
            print("One or more environment variables (TENANT_ID, CLIENT_ID, CLIENT_SECRET) are not set.")
            return

        access_token = get_access_token()
        for endpoint in GRAPH_API_ENDPOINTS:
            call_graph_api(access_token, endpoint)
            time.sleep(2) # Small delay between API calls

        print(f"Script finished successfully at {time.ctime()}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
