"""
Air Quality & Pollution Tracking Portal (CLI) - Windows friendly
- No shebang line to avoid PowerShell errors.
- Menu-driven Admin & Citizen CLI.
- Includes sample pollutants and AQI data for 20 Indian cities (Jan 1-15, 2025).
Run:
    python main.py
Admin credentials: admin / admin123
"""
import os
import sys
import json
import uuid
import random
import datetime
from collections import defaultdict

try:
    from tabulate import tabulate
except Exception:
    tabulate = None

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
FILES = {
    "air": "air_quality.json",
    "citizens": "citizens.json",
    "pollutants": "pollutants.json",
    "alerts": "alerts.json",
    "guidelines": "guidelines.json",
}

ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    for fn in FILES.values():
        path = os.path.join(DATA_DIR, fn)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

def load_json(name):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, FILES[name])
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_json(name, data):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, FILES[name])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

def gen_id(prefix="id"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def print_table(rows, headers=None):
    if tabulate:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        if headers:
            print(" | ".join(headers))
            print("-" * max(40, len(headers) * 10))
        for r in rows:
            print(" | ".join(str(x) for x in r))

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def find_by_id(list_obj, key_name, key_value):
    for item in list_obj:
        if item.get(key_name) == key_value:
            return item
    return None

# Admin functions (same as before)
def admin_login():
    print("Admin login")
    u = input("Username: ").strip()
    p = input("Password: ").strip()
    if u == ADMIN_CREDENTIALS["username"] and p == ADMIN_CREDENTIALS["password"]:
        print("Logged in as admin.")
        return True
    print("Invalid credentials.")
    return False

def admin_menu():
    while True:
        print("--- Admin Menu ---")
        print("1. Add Air Quality Record")
        print("2. Update/Delete Air Record")
        print("3. Manage Pollutants")
        print("4. Upload Bulk Data (JSON/CSV)")
        print("5. Generate Reports")
        print("6. Manage Alerts")
        print("7. Back to Main Menu")
        ch = input("Choice: ").strip()
        if ch == "1":
            add_air_quality_record()
        elif ch == "2":
            update_delete_aq_record()
        elif ch == "3":
            manage_pollutants()
        elif ch == "4":
            upload_bulk_data()
        elif ch == "5":
            generate_reports()
        elif ch == "6":
            manage_alerts()
        elif ch == "7":
            break
        else:
            print("Invalid choice.")

def add_air_quality_record():
    air = load_json("air")
    pollutants_list = load_json("pollutants")
    print("Add Air Quality Record")
    region = input("Region / City: ").strip()
    date = input("Date (YYYY-MM-DD): ").strip()
    if date == "":
        date = str(datetime.date.today())
    aqi = safe_float(input("AQI (numeric): ").strip() or 0)
    pollutant_levels = {}
    print("Enter pollutant levels (blank to skip):")
    for p in pollutants_list:
        name = p.get("name")
        val = input(f"  {name}: ").strip()
        if val != "":
            pollutant_levels[name] = safe_float(val)
    rec = {
        "record_id": gen_id("rec"),
        "region": region,
        "date": date,
        "AQI": int(aqi),
        "pollutants": pollutant_levels,
        "health_risk": ""
    }
    air.append(rec)
    save_json("air", air)
    print("Record added.")

def update_delete_aq_record():
    air = load_json("air")
    if not air:
        print("No air quality records available.")
        return
    rows = [[r["record_id"], r["region"], r["date"], r["AQI"]] for r in air]
    print_table(rows, headers=["ID", "Region", "Date", "AQI"])
    rid = input("Enter record_id to update/delete (blank to cancel): ").strip()
    if not rid:
        return
    rec = find_by_id(air, "record_id", rid)
    if not rec:
        print("Record not found.")
        return
    action = input("Enter 'u' to update, 'd' to delete, anything else to cancel: ").strip().lower()
    if action == "d":
        air = [r for r in air if r["record_id"] != rid]
        save_json("air", air)
        print("Deleted.")
    elif action == "u":
        rec["region"] = input(f"Region [{rec['region']}]: ").strip() or rec['region']
        rec["date"] = input(f"Date [{rec['date']}]: ").strip() or rec['date']
        aqi_in = input(f"AQI [{rec['AQI']}]: ").strip()
        if aqi_in != "":
            rec["AQI"] = int(safe_float(aqi_in, rec["AQI"]))
        for k in list(rec.get("pollutants", {}).keys()):
            newv = input(f"{k} [{rec['pollutants'].get(k,'')}]: ").strip()
            if newv != "":
                rec['pollutants'][k] = safe_float(newv)
        save_json("air", air)
        print("Updated.")
    else:
        print("Cancelled.")

def manage_pollutants():
    while True:
        pollutants = load_json("pollutants")
        rows = [[p["pollutant_id"], p["name"], p.get("description",""), p.get("safe_limit","")] for p in pollutants]
        print_table(rows, headers=["ID", "Name", "Description", "Safe limit"])
        print("Options: 1.Add 2.Update 3.Delete 4.Back")
        ch = input("Choice: ").strip()
        if ch == "1":
            name = input("Name: ").strip()
            desc = input("Description: ").strip()
            sl = input("Safe limit (numeric): ").strip()
            pollutants.append({"pollutant_id": gen_id("pol"), "name": name, "description": desc, "safe_limit": safe_float(sl)})
            save_json("pollutants", pollutants)
            print("Pollutant added.")
        elif ch == "2":
            pid = input("Pollutant ID to update: ").strip()
            p = find_by_id(pollutants, "pollutant_id", pid)
            if not p:
                print("Not found.")
                continue
            p["name"] = input(f"Name [{p['name']}]: ").strip() or p["name"]
            p["description"] = input(f"Description [{p.get('description','')}]: ").strip() or p.get("description","")
            sl = input(f"Safe limit [{p.get('safe_limit','')}]: ").strip()
            if sl != "":
                p["safe_limit"] = safe_float(sl)
            save_json("pollutants", pollutants)
            print("Updated.")
        elif ch == "3":
            pid = input("Pollutant ID to delete: ").strip()
            pollutants = [x for x in pollutants if x["pollutant_id"] != pid]
            save_json("pollutants", pollutants)
            print("Deleted if existed.")
        elif ch == "4":
            break
        else:
            print("Invalid choice.")

def upload_bulk_data():
    path = input("Enter path to JSON or CSV file: ").strip()
    if not os.path.exists(path):
        print("File not found.")
        return
    ext = os.path.splitext(path)[1].lower()
    air = load_json("air")
    if ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for rec in data:
                if "record_id" not in rec:
                    rec["record_id"] = gen_id("rec")
                air.append(rec)
            save_json("air", air)
            print(f"Imported {len(data)} records.")
        else:
            print("JSON must be a list of records.")
    elif ext == ".csv":
        import csv
        pollutants = [p["name"] for p in load_json("pollutants")]
        with open(path, newline="", encoding="utf-8") as cf:
            reader = csv.DictReader(cf)
            added = 0
            for row in reader:
                rec = {
                    "record_id": gen_id("rec"),
                    "region": row.get("region", ""),
                    "date": row.get("date", str(datetime.date.today())),
                    "AQI": int(safe_float(row.get("AQI",0))),
                    "pollutants": {},
                    "health_risk": row.get("health_risk","")
                }
                for pn in pollutants:
                    if pn in row and row[pn] != "":
                        rec["pollutants"][pn] = safe_float(row[pn])
                air.append(rec)
                added += 1
            save_json("air", air)
            print(f"Imported {added} rows from CSV.")
    else:
        print("Unsupported file type. Use .json or .csv")

def generate_reports():
    air = load_json("air")
    if not air:
        print("No data available.")
        return
    print("Report options: 1.Top polluted regions (avg AQI) 2.Monthly trend for a region 3.Alerts summary 4.Back")
    ch = input("Choice: ").strip()
    if ch == "1":
        region_map = defaultdict(list)
        for r in air:
            region_map[r["region"]].append(r.get("AQI",0))
        rows = [[region, round(sum(vals)/len(vals),1), len(vals)] for region, vals in region_map.items()]
        rows.sort(key=lambda x: x[1], reverse=True)
        print_table(rows, headers=["Region", "Average AQI", "Records"])
    elif ch == "2":
        region = input("Region: ").strip()
        rows = [r for r in air if r["region"].lower() == region.lower()]
        if not rows:
            print("No data for that region.")
            return
        monthly = defaultdict(list)
        for r in rows:
            try:
                d = datetime.datetime.strptime(r["date"], "%Y-%m-%d")
                key = f"{d.year}-{d.month:02d}"
            except Exception:
                key = r["date"]
            monthly[key].append(r.get("AQI",0))
        data = sorted([(k, sum(v)/len(v)) for k,v in monthly.items()])
        print_table(data, headers=["Month", "Avg AQI"])
    elif ch == "3":
        alerts = load_json("alerts")
        if not alerts:
            print("No alerts.")
            return
        rows = [[a["alert_id"], a["region"], a["AQI_level"], a["status"], a["issue_date"]] for a in alerts]
        print_table(rows, headers=["ID","Region","AQI_level","Status","Issue date"])
    else:
        return

def manage_alerts():
    alerts = load_json("alerts")
    print("1.Issue alert 2.Withdraw alert 3.Back")
    ch = input("Choice: ").strip()
    if ch == "1":
        region = input("Region: ").strip()
        level = input("AQI level: ").strip()
        issue_date = str(datetime.date.today())
        expiry = input("Expiry date (YYYY-MM-DD) or blank: ").strip()
        alerts.append({"alert_id": gen_id("alert"), "region": region, "AQI_level": level, "status": "active", "issue_date": issue_date, "expiry_date": expiry})
        save_json("alerts", alerts)
        print("Alert issued.")
    elif ch == "2":
        aid = input("Alert ID to withdraw: ").strip()
        a = find_by_id(alerts, "alert_id", aid)
        if a:
            a["status"] = "withdrawn"
            save_json("alerts", alerts)
            print("Alert withdrawn.")
    else:
        return

# Citizen functions
def register_citizen():
    citizens = load_json("citizens")
    print("Register new citizen")
    name = input("Name: ").strip()
    age = input("Age: ").strip()
    location = input("Location / Region: ").strip()
    contact = input("Contact (email/phone): ").strip()
    citizen = {"citizen_id": gen_id("cit"), "name": name, "age": age, "location": location, "contact": contact}
    citizens.append(citizen)
    save_json("citizens", citizens)
    print("Registered. Your Citizen ID:", citizen["citizen_id"])

def citizen_login():
    citizens = load_json("citizens")
    cid = input("Enter Citizen ID: ").strip()
    c = find_by_id(citizens, "citizen_id", cid)
    if c:
        citizen_menu(c)
    else:
        print("Citizen not found. Please register.")

def citizen_menu(citizen):
    while True:
        print(f"\\n--- Citizen Menu ({citizen['name']}) ---")
        print("1.View Current Air Quality (your region)")
        print("2.Search Historical AQI Data")
        print("3.View Pollution Trends (text)")
        print("4.Access Health Guidelines")
        print("5.Manage Profile")
        print("6.Logout")
        ch = input("Choice: ").strip()
        if ch == "1":
            view_current_aqi(citizen)
        elif ch == "2":
            search_historical_data()
        elif ch == "3":
            view_trends()
        elif ch == "4":
            access_guidelines()
        elif ch == "5":
            manage_profile(citizen)
        elif ch == "6":
            break
        else:
            print("Invalid choice.")

def view_current_aqi(citizen):
    region = citizen.get("location","")
    air = load_json("air")
    region_records = [r for r in air if r["region"].lower() == region.lower()]
    if not region_records:
        print(f"No AQI data for region: {region}")
        return
    region_records.sort(key=lambda r: r["date"], reverse=True)
    r = region_records[0]
    print_table([[r["date"], r["region"], r["AQI"], r.get("pollutants",{})]], headers=["Date","Region","AQI","Pollutants"])
    alerts = load_json("alerts")
    for a in alerts:
        if a["region"].lower() == region.lower() and a["status"] == "active":
            print(f"ALERT: {a['AQI_level']} issued on {a['issue_date']} (id {a['alert_id']})")

def search_historical_data():
    air = load_json("air")
    if not air:
        print("No air quality data available.")
        return
    print("Search by:\\n1.Date\\n2.Region\\n3.Pollutant\\n4.All Regions (latest AQI per region)\\n5.Back")
    ch = input("Choice: ").strip()
    results = []
    if ch == "1":
        d = input("Date (YYYY-MM-DD): ").strip()
        results = [r for r in air if r["date"] == d]
    elif ch == "2":
        reg = input("Region: ").strip().lower()
        results = [r for r in air if r["region"].lower() == reg]
    elif ch == "3":
        pol = input("Pollutant name (e.g. PM2.5): ").strip()
        results = [r for r in air if pol in r.get("pollutants",{})]
    elif ch == "4":
        latest = {}
        for r in air:
            key = r["region"]
            if key not in latest or r["date"] > latest[key]["date"]:
                latest[key] = r
        results = list(latest.values())
    else:
        return
    if not results:
        print("No matches found.")
        return
    rows = [[r.get("record_id"), r.get("date"), r.get("region"), r.get("AQI"), r.get("pollutants",{})] for r in results]
    print_table(rows, headers=["ID","Date","Region","AQI","Pollutants"])

def view_trends():
    print("Trend view (text-only). Use Generate Reports to see aggregated stats.")

def access_guidelines():
    guides = load_json("guidelines")
    if not guides:
        print("No guidelines available.")
        return
    rows = [[g.get("guide_id"), g.get("AQI_range"), g.get("precautions")] for g in guides]
    print_table(rows, headers=["ID","AQI Range","Precautions"])

def manage_profile(citizen):
    citizens = load_json("citizens")
    found = find_by_id(citizens, "citizen_id", citizen["citizen_id"])
    if not found:
        print("Profile not found.")
        return
    found["name"] = input(f"Name [{found['name']}]: ").strip() or found["name"]
    age = input(f"Age [{found.get('age','')}]: ").strip()
    if age != "":
        found["age"] = age
    found["location"] = input(f"Location [{found.get('location','')}]: ").strip() or found.get("location")
    found["contact"] = input(f"Contact [{found.get('contact','')}]: ").strip() or found.get("contact")
    save_json("citizens", citizens)
    print("Profile updated.")

# Sample data creation
def create_sample_data():
    pollutants = [
        {"pollutant_id":"pol_pm25","name":"PM2.5","description":"Fine particulate matter (µg/m³)","safe_limit":60},
        {"pollutant_id":"pol_pm10","name":"PM10","description":"Coarse particulate matter (µg/m³)","safe_limit":100},
        {"pollutant_id":"pol_no2","name":"NO2","description":"Nitrogen dioxide (µg/m³)","safe_limit":80},
        {"pollutant_id":"pol_co","name":"CO","description":"Carbon monoxide (mg/m³)","safe_limit":10},
        {"pollutant_id":"pol_o3","name":"O3","description":"Ozone (µg/m³)","safe_limit":120},
        {"pollutant_id":"pol_so2","name":"SO2","description":"Sulfur dioxide (µg/m³)","safe_limit":80},
    ]
    save_json("pollutants", pollutants)

    guidelines = [
        {"guide_id":"g1","AQI_range":"0-50","precautions":"Good: No health impacts expected."},
        {"guide_id":"g2","AQI_range":"51-100","precautions":"Moderate: Unusually sensitive people should consider reducing prolonged outdoor exertion."},
        {"guide_id":"g3","AQI_range":"101-200","precautions":"Unhealthy: Sensitive groups should reduce prolonged outdoor exertion."},
        {"guide_id":"g4","AQI_range":"201-300","precautions":"Very Unhealthy: Avoid outdoor activities."},
        {"guide_id":"g5","AQI_range":"301-500","precautions":"Hazardous: Remain indoors and use protective measures."},
    ]
    save_json("guidelines", guidelines)

    citizens = [
        {"citizen_id":"cit_alice","name":"Alice","age":30,"location":"Delhi","contact":"alice@example.com"},
        {"citizen_id":"cit_bob","name":"Bob","age":40,"location":"Mumbai","contact":"bob@example.com"}
    ]
    save_json("citizens", citizens)

    cities = ["Delhi","Mumbai","Kolkata","Chennai","Bengaluru","Hyderabad","Ahmedabad","Pune","Lucknow","Jaipur",
              "Bhopal","Visakhapatnam","Surat","Kanpur","Nagpur","Indore","Thane","Agra","Vadodara","Nashik"]
    air = []
    random.seed(42)
    for city in cities:
        for day in range(1,16):  # Jan 1-15, 2025
            date = datetime.date(2025,1,day).isoformat()
            aqi = random.randint(50,400)
            pm25 = round(aqi * random.uniform(0.3,0.9),1)
            pm10 = round(aqi * random.uniform(0.4,1.0),1)
            no2 = round(aqi * random.uniform(0.05,0.25),1)
            co = round(random.uniform(0.2,5.0) * (aqi/100.0),2)
            o3 = round(random.uniform(10,150) * (aqi/200.0),1)
            so2 = round(random.uniform(5,80) * (aqi/200.0),1)
            rec = {"record_id": gen_id("rec"), "region": city, "date": date, "AQI": aqi,
                   "pollutants": {"PM2.5": pm25, "PM10": pm10, "NO2": no2, "CO": co, "O3": o3, "SO2": so2},
                   "health_risk": ""}
            air.append(rec)
    save_json("air", air)

    alerts = [
        {"alert_id": gen_id("alert"), "region": "Delhi", "AQI_level": "Very Unhealthy", "status": "active", "issue_date": "2025-01-10", "expiry_date": "2025-01-12"},
        {"alert_id": gen_id("alert"), "region": "Kanpur", "AQI_level": "Hazardous", "status": "active", "issue_date": "2025-01-08", "expiry_date": "2025-01-11"},
    ]
    save_json("alerts", alerts)
    print("Sample data created in data/")

def ensure_sample_data():
    ensure_data_dir()
    if not load_json("pollutants"):
        create_sample_data()

def main_menu():
    ensure_sample_data()
    print("=== Air Quality & Pollution Tracking Portal ===")
    while True:
        print("Main Menu:\n1.Admin Login\n2.Citizen Login\n3.Register as New Citizen\n4.Exit")
        ch = input("Choice: ").strip()
        if ch == "1":
            if admin_login():
                admin_menu()
        elif ch == "2":
            cid = input("Enter Citizen ID: ").strip()
            citizens = load_json("citizens")
            c = find_by_id(citizens, "citizen_id", cid)
            if c:
                citizen_menu(c)
            else:
                print("Citizen not found. Register first.")
        elif ch == "3":
            register_citizen()
        elif ch == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\\nExiting...")
        sys.exit(0)
