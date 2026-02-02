import sys
import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def wait_for_server(url, retries=10, delay=2):
    print(f"Waiting for server at {url}...")
    for i in range(retries):
        try:
            requests.get(url)
            print("Server is up!")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(delay)
    return False

def test_loki_endpoints():
    # 1. Health Check
    try:
        resp = requests.get("http://127.0.0.1:8000/health")
        print(f"Health Check: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")

    # 2. Auth (Mock)
    try:
        resp = requests.post(f"{BASE_URL}/auth/login/access-token", data={"username": "admin", "password": "admin"})
        if resp.status_code == 200:
            print("Auth Login: SUCCESS")
            token = resp.json()["access_token"]
        else:
            print(f"Auth Login Failed: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print(f"Auth Request Failed: {e}")
        return

    # 3. AI Firm Status
    try:
        resp = requests.get(f"{BASE_URL}/ai-firm/status")
        if resp.status_code == 200:
            data = resp.json()
            print(f"AI Firm Status: {data['status']}")
            print(f"Swarm Mode: {data['ai_firm']['mode']}")
            print(f"Agents Active: {data['ai_firm']['total_agents']}")
        else:
            print(f"AI Firm Status Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"AI Firm Request Failed: {e}")

if __name__ == "__main__":
    if wait_for_server("http://127.0.0.1:8000/health"):
        test_loki_endpoints()
    else:
        print("Server failed to start.")
