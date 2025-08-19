import requests

def handle_scan(scanned_id):
    url = f"http://localhost:5000/scan?id={scanned_id}"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            print(f"Student: {data['student']} marked as {data['status']}")
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Failed to call attendance API: {e}")

# Example usage when barcode scanned
# handle_scan("12345")