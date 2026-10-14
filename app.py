import time
import random
import re
import threading
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

STATUS_LOG = "System idle. Ready for today's token payload input."
IS_RUNNING = False

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Telenor Cloud Automation</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; background: #f4f6f9; color: #333; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h2 { color: #0076FF; margin-top: 0; }
        textarea { width: 100%; border: 1px solid #ccc; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 13px; background: #fafafa; box-sizing: border-box; }
        button { background: #0076FF; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 15px; margin-top: 15px; width: 100%; }
        button:hover { background: #0056b3; }
        .status-box { background: #eef2f7; border-left: 4px solid #0076FF; padding: 15px; margin-bottom: 20px; border-radius: 0 8px 8px 0; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="card">
        <h2>⚡ Daily Telenor Packet Automator</h2>
        <div class="status-box"><strong>Current Logs:</strong><br>{{ status }}</div>
        
        <form action="/trigger" method="post">
            <label style="font-weight: 600; display: block; margin-bottom: 8px;">Paste Raw Packet Log from Interceptor:</label>
            <textarea name="raw_packet" rows="12" placeholder="POST /api/streak/claim HTTP/1.1..."></textarea>
            <button type="submit">Deploy 20,000 Loops to Cloud</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    global STATUS_LOG
    return render_template_string(DASHBOARD_HTML, status=STATUS_LOG)

@app.route('/trigger', methods=['POST'])
def trigger():
    global IS_RUNNING, STATUS_LOG
    if IS_RUNNING:
        return "A loop session is actively processing in the background right now!", 400
    
    raw_text = request.form.get('raw_packet', '')
    if not raw_text:
        return "Error: Clipboard text input was blank.", 400

    # UPGRADED PARSER: Case-insensitive flags ensure it reads variations perfectly
    token_match = re.search(r'X-XENON-TOKEN-V2:\s*([^\r\n]+)', raw_text, re.IGNORECASE)
    signature_match = re.search(r'signature:\s*([^\r\n]+)', raw_text, re.IGNORECASE)
    device_id_match = re.search(r'X-Device-Id:\s*([^\r\n]+)', raw_text, re.IGNORECASE)

    if not token_match or not signature_match:
        STATUS_LOG = f"❌ Parsing Error!\nToken Found: {'Yes' if token_match else 'No'}\nSignature Found: {'Yes' if signature_match else 'No'}\n\nPlease re-copy and paste the entire raw text block cleanly."
        return "Parsing failure. Check UI status log screen.", 400

    token = token_match.group(1).strip()
    signature = signature_match.group(1).strip()
    device_id = device_id_match.group(1).strip() if device_id_match else "f4f32fc407b4bd83"

    IS_RUNNING = True
    # The fix: Using a safe background processor thread handler
    thread = threading.Thread(target=run_packet_engine, args=(token, signature, device_id))
    thread.start()

    STATUS_LOG = "🚀 Cloud background engine successfully initialized! Processing requests..."
    return "🚀 Received! Processing loop on server dashboard..."

def run_packet_engine(token, signature, device_id):
    global STATUS_LOG, IS_RUNNING
    url = "https://telenor.com.pk"
    
    headers = {
        "Accept": "application/json",
        "X-request-os": "Android",
        "X-app-version": "4.2.61",
        "X-app-build-version": "4.2.61",
        "X-os-version": "14",
        "X-request-channel": "DCE-APP-ANDROID",
        "X-app-language": "EN",
        "X-user-price-plan": "djuice",
        "X-user-segment": "Private",
        "X-device-make": "SSH Telecom SMC (Pvt.) Ltd",
        "X-device-model": "Ssh telecom smc (pvt.) ltd NOTE 23",
        "X-screen-resolution": "{1080,2210}",
        "x-user-segment-type": "djuice",
        "x-user-package-plan": "Qbrand4",
        "x-user-plan-type": "prepaid",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "://telenor.com.pk",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/5.1.0",
        "X-Device-Id": device_id,
        "X-XENON-TOKEN-V2": token,
        "signature": signature
    }
    
    body = {"msisdn": "03434877651"}
    total_iterations = 20000
    success_count = 0
    fail_count = 0

    for i in range(1, total_iterations + 1):
        try:
            response = requests.post(url, json=body, headers=headers, timeout=8)
            if response.status_code == 200:
                success_count += 1
            else:
                fail_count += 1
                # If Telenor blocks the IP, this message will immediately populate your interface
                if i % 10 == 0:
                    print(f"[Server Warning] Telenor returned error status: {response.status_code}")
            
            # Displays detailed status information inside your control webpage
            STATUS_LOG = f"Processing loop: {i}/{total_iterations} completed.\n✅ Successful (200 OK): {success_count}\n❌ Rejected/Errors: {fail_count}"
        
        except Exception as error_msg:
            fail_count += 1
            STATUS_LOG = f"Processing loop: {i}/{total_iterations}\n⚠️ Connection interrupted by cloud error framework."

        # Keep safe, random anti-ban delay parameters active
        time.sleep(random.uniform(1.4, 2.8))

    STATUS_LOG = f"🏁 Loop Session Finished!\nTotal processed: {total_iterations}\nSuccessful claims: {success_count}\nFailed/Rejected: {fail_count}"
    IS_RUNNING = False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    
