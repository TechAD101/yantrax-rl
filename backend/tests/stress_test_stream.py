
import requests
import json
import time
import sys

def test_stream():
    url = "http://localhost:5000/market-price-stream?symbol=AAPL&interval=1"
    print(f"🚀 Connecting to Stream: {url}")
    
    try:
        with requests.get(url, stream=True, timeout=10) as r:
            print(f"✅ Connection Established. Status: {r.status_code}")
            if r.status_code != 200:
                print(f"❌ Failed. Content: {r.text}")
                return

            start_time = time.time()
            count = 0
            
            for line in r.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        json_str = decoded[6:]
                        try:
                            data = json.loads(json_str)
                            price = data.get('price')
                            source = data.get('source')
                            print(f"📊 DATA #{count+1}: Price=${price} | Source={source}")
                            count += 1
                        except:
                            print(f"⚠️ Bad Data: {decoded}")
                
                # Run for 10 seconds
                if time.time() - start_time > 10:
                    break
                    
    except Exception as e:
        print(f"❌ STREAM FAILED: {e}")

if __name__ == "__main__":
    test_stream()
