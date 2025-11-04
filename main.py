import json
import os
from tabulate import tabulate
from datetime import datetime

DATA_FILES = {
    "air_quality": "air_quality.json",
    "citizens": "citizens.json",
    "pollutants": "pollutants.json",
    "alerts": "alerts.json",
    "guidelines": "guidelines.json"
}

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. Add Air Quality Record")
        print("2. Update/Delete Record")
        print("3. Manage Pollutants")
        print("4. Upload Bulk Data (JSON)")
        print("5. Generate Reports")
        print("6. Manage Alerts")
        print("7. Logout")
        choice = input("Enter choice: ")

        if choice == "1":
            add_air_quality()
        elif choice == "2":
            update_delete_record()
        elif choice == "3":
            manage_pollutants()
        elif choice == "4":
            upload_bulk_data()
        elif choice == "5":
            generate_reports()
        elif choice == "6":
            manage_alerts()
        elif choice == "7":
            break
        else:
            print("Invalid choice.")

def citizen_menu(citizen_id):
    while True:
        print("\n--- Citizen Menu ---")
        print("1. View Current Air Quality")
        print("2. Search Historical AQI Data")
        print("3. View Pollution Trends")
        print("4. Access Health Guidelines")
        print("5. Manage Profile")
        print("6. Logout")
        choice = input("Enter choice: ")

        if choice == "1":
            view_current_air_quality()
        elif choice == "2":
            search_historical_data()
        elif choice == "3":
            view_pollution_trends()
        elif choice == "4":
            access_guidelines()
        elif choice == "5":
            manage_profile(citizen_id)
        elif choice == "6":
            break
        else:
            print("Invalid choice.")

# === CRUD operations ===

def add_air_quality():
    data = load_data(DATA_FILES["air_quality"])
    record = {
        "record_id": len(data) + 1,
        "region": input("Enter region: "),
        "date": str(datetime.now().date()),
        "AQI": int(input("Enter AQI: ")),
        "pollutants": input("Enter pollutants (comma separated): ").split(","),
        "health_risk": input("Enter health risk: ")
    }
    data.append(record)
    save_data(DATA_FILES["air_quality"], data)
    print("✅ Record added successfully.")

def update_delete_record():
    data = load_data(DATA_FILES["air_quality"])
    print(tabulate(data, headers="keys"))
    record_id = int(input("Enter record_id to modify/delete: "))
    for rec in data:
        if rec["record_id"] == record_id:
            action = input("Type 'u' to update or 'd' to delete: ")
            if action == "u":
                rec["AQI"] = int(input("Enter new AQI: "))
                rec["health_risk"] = input("Enter new health risk: ")
                print("✅ Record updated.")
            elif action == "d":
                data.remove(rec)
                print("🗑️ Record deleted.")
            break
    save_data(DATA_FILES["air_quality"], data)

def manage_pollutants():
    data = load_data(DATA_FILES["pollutants"])
    print("Current pollutants:")
    print(tabulate(data, headers="keys"))
    choice = input("Add new pollutant? (y/n): ")
    if choice.lower() == "y":
        p = {
            "pollutant_id": len(data) + 1,
            "name": input("Name: "),
            "description": input("Description: "),
            "safe_limit": input("Safe limit: ")
        }
        data.append(p)
        save_data(DATA_FILES["pollutants"], data)
        print("✅ Pollutant added.")

def upload_bulk_data():
    path = input("Enter JSON file path to upload: ")
    if os.path.exists(path):
        data = load_data(DATA_FILES["air_quality"])
        with open(path, "r") as f:
            bulk = json.load(f)
        data.extend(bulk)
        save_data(DATA_FILES["air_quality"], data)
        print("✅ Bulk data uploaded.")
    else:
        print("❌ File not found.")

def generate_reports():
    data = load_data(DATA_FILES["air_quality"])
    if not data:
        print("No data available.")
        return
    print("=== Report: Top Polluted Regions ===")
    sorted_data = sorted(data, key=lambda x: x["AQI"], reverse=True)[:5]
    print(tabulate(sorted_data, headers="keys"))

def manage_alerts():
    alerts = load_data(DATA_FILES["alerts"])
    choice = input("Issue new alert? (y/n): ")
    if choice.lower() == "y":
        a = {
            "alert_id": len(alerts) + 1,
            "region": input("Region: "),
            "AQI_level": input("AQI level: "),
            "status": "Active",
            "issue_date": str(datetime.now().date()),
            "expiry_date": input("Expiry date (YYYY-MM-DD): ")
        }
        alerts.append(a)
        save_data(DATA_FILES["alerts"], alerts)
        print("🚨 Alert issued.")

def register_citizen():
    data = load_data(DATA_FILES["citizens"])
    c = {
        "citizen_id": len(data) + 1,
        "name": input("Name: "),
        "age": input("Age: "),
        "location": input("Location: "),
        "contact": input("Contact: ")
    }
    data.append(c)
    save_data(DATA_FILES["citizens"], data)
    print("✅ Registered successfully! Your ID:", c["citizen_id"])

def view_current_air_quality():
    region = input("Enter your region: ")
    data = load_data(DATA_FILES["air_quality"])
    results = [r for r in data if r["region"].lower() == region.lower()]
    if results:
        print(tabulate(results[-5:], headers="keys"))
    else:
        print("No records for this region.")

def search_historical_data():
    region = input("Enter region: ")
    data = load_data(DATA_FILES["air_quality"])
    results = [r for r in data if r["region"].lower() == region.lower()]
    print(tabulate(results, headers="keys"))

def view_pollution_trends():
    print("Feature: View pollution trends (visualization optional).")
    print("Use pandas/matplotlib for graph generation.")

def access_guidelines():
    data = load_data(DATA_FILES["guidelines"])
    print(tabulate(data, headers="keys"))

def manage_profile(cid):
    print(f"Profile management for Citizen {cid} not implemented yet.")

def main():
    while True:
        print("\n=== Air Quality & Pollution Tracking Portal ===")
        print("1. Admin Login")
        print("2. Citizen Login")
        print("3. Register as New Citizen")
        print("4. Exit")
        ch = input("Enter your choice: ")

        if ch == "1":
            admin_menu()
        elif ch == "2":
            cid = input("Enter Citizen ID: ")
            citizen_menu(cid)
        elif ch == "3":
            register_citizen()
        elif ch == "4":
            print("Exiting...")
            break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    main()
