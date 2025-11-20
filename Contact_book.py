#!/usr/bin/env python3
# Name: Gaurav Kumar
# Roll No: 2501940033
# Project: Contact Book Manager
# Date: 2025-11-14
# Note: Handles contacts with CSV/JSON support, backups, and duplicate checking.

import csv
import json
import os
import re
import shutil
import sys
from datetime import datetime
from difflib import SequenceMatcher, get_close_matches

# Global settings and filenames
db_file = "contacts.csv"
json_db = "contacts.json"
log_file = "error_log.txt"
backup_folder = "backups"
temp_file = ".temp_data.json"
headers = ["name", "phone", "email", "tags", "favorite"]

# Helper to write errors to a file so the program doesn't just crash
def save_error(action, err_msg):
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    
    try:
        with open(log_file, "a") as f:
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{time_now}] Error in {action}: {str(err_msg)}\n")
            f.write("-" * 50 + "\n")
    except:
        print("Error: Could not save to log file.")

# Simple function to make sure folders exist
def check_folder(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        save_error("check_folder", e)

# Save a temp copy of data for the Undo feature
def save_temp_snapshot(data):
    try:
        with open(temp_file, "w") as f:
            json.dump(data, f)
    except Exception as e:
        save_error("save_temp_snapshot", e)

# Load the temp copy
def get_last_snapshot():
    try:
        if os.path.exists(temp_file):
            with open(temp_file, "r") as f:
                return json.load(f)
    except Exception as e:
        save_error("get_last_snapshot", e)
    return None

# Cleaning up phone numbers
def clean_phone(number):
    if not number: return ""
    number = number.strip()
    # Keep the plus sign if it's there
    has_plus = number.startswith("+")
    # Remove everything that isn't a number
    cleaned = re.sub(r"\D", "", number)
    
    if has_plus and cleaned:
        return "+" + cleaned
    return cleaned

def check_phone(number):
    # Validates length
    p = clean_phone(number)
    digits = p.replace("+", "")
    if len(digits) >= 7 and len(digits) <= 15:
        return True
    return False

def check_email(email):
    # Regex for email validation
    pattern = r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]{2,}$"
    if email and re.match(pattern, email.strip()):
        return True
    return False

# Initialize CSV if missing
def init_db():
    if not os.path.isfile(db_file):
        try:
            with open(db_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
        except Exception as e:
            save_error("init_db", e)
            print("Could not create database file.")

# Load data from CSV
def load_data():
    data_list = []
    try:
        with open(db_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row: continue
                
                # Clean up None values just in case
                clean_row = {}
                for k in headers:
                    val = row.get(k, "")
                    if val is None: val = ""
                    clean_row[k] = val.strip()
                
                # Fix boolean for favorite
                is_fav = str(clean_row.get("favorite", "")).lower()
                clean_row["favorite"] = is_fav in ["1", "true", "yes", "y"]
                
                if clean_row["name"]:
                    data_list.append(clean_row)
    except FileNotFoundError:
        return [] # Return empty if file doesn't exist yet
    except Exception as e:
        save_error("load_data", e)
        print("Error loading contacts.")
    return data_list

# Save data to CSV
def save_data(contacts, do_backup=True, save_undo=True):
    try:
        check_folder(backup_folder)

        # Save undo snapshot
        if save_undo:
            old_data = load_data()
            save_temp_snapshot(old_data)

        # Daily Backup Logic
        if do_backup and os.path.exists(db_file):
            date_str = datetime.now().strftime("%Y%m%d")
            # Check if we already made a backup today to save space
            already_backed_up = False
            try:
                for f in os.listdir(backup_folder):
                    if f.startswith(f"backup_{date_str}"):
                        already_backed_up = True
                        break
            except: pass

            if not already_backed_up:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                shutil.copy2(db_file, os.path.join(backup_folder, f"backup_{ts}.csv"))

        # Write actual file
        with open(db_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for c in contacts:
                # Convert boolean back to string for CSV
                row = c.copy()
                row["favorite"] = "1" if c.get("favorite") else "0"
                writer.writerow(row)
                
    except Exception as e:
        save_error("save_data", e)
        print("Failed to save data.")

def show_list(contacts, sort_key="name"):
    if not contacts:
        print("\nList is empty.\n")
        return

    # Sort logic
    if sort_key == "favorite":
        contacts.sort(key=lambda x: not x.get("favorite"))
    else:
        contacts.sort(key=lambda x: x.get(sort_key, "").lower())

    # Formatting table
    print("\n" + "-" * 60)
    print(f"{'Fav':<4} {'Name':<20} {'Phone':<15} {'Tags'}")
    print("-" * 60)
    
    for c in contacts:
        star = "*" if c.get("favorite") else " "
        n = c.get("name", "")
        p = c.get("phone", "")
        t = c.get("tags", "")
        print(f"{star:<4} {n:<20} {p:<15} {t}")
    print("-" * 60 + "\n")

def get_contact(name, contacts):
    for c in contacts:
        if c["name"].lower() == name.lower():
            return c
    return None

# Feature 1: Add
def add_new():
    try:
        print("--- Add New Contact ---")
        name = input("Name: ").strip()
        if not name:
            print("Name is required.")
            return

        phone = input("Phone: ").strip()
        email = input("Email: ").strip()
        tags = input("Tags (comma separated): ").strip()
        f_input = input("Favorite? (y/n): ").strip().lower()
        is_fav = f_input == "y" or f_input == "yes"

        # Validate
        final_phone = clean_phone(phone)
        if phone and not check_phone(phone):
            print("Note: Phone number looks weird, but saved anyway.")
        if email and not check_email(email):
            print("Note: Email format looks wrong.")

        current_list = load_data()
        
        # check duplicates/similar names
        all_names = [x["name"] for x in current_list]
        similar = get_close_matches(name, all_names, n=1, cutoff=0.8)
        
        if similar:
            print(f"Found similar name: {similar[0]}")
            ans = input("Merge with existing? (M) or Add New (A)? ").upper()
            if ans == "M":
                # Merge logic
                target = get_contact(similar[0], current_list)
                if target:
                    if not target["phone"]: target["phone"] = final_phone
                    if not target["email"]: target["email"] = email
                    # merge tags
                    old_tags = target["tags"].split(",")
                    new_tags = tags.split(",")
                    combined = set([t.strip() for t in old_tags + new_tags if t.strip()])
                    target["tags"] = ",".join(combined)
                    save_data(current_list)
                    print("Merged successfully.")
                    return

        new_c = {
            "name": name,
            "phone": final_phone,
            "email": email,
            "tags": tags,
            "favorite": is_fav
        }
        current_list.append(new_c)
        save_data(current_list)
        print("Saved.")

    except Exception as e:
        save_error("add_new", e)

# Feature 3: Search
def search_db():
    query = input("Search (Name, Phone, Tag) or /regex/: ").strip()
    if not query: return

    data = load_data()
    results = []

    # Regex search
    if query.startswith("/") and query.endswith("/"):
        pattern = query[1:-1]
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            for c in data:
                # Check all fields
                blob = f"{c['name']} {c['phone']} {c['email']} {c['tags']}"
                if regex.search(blob):
                    results.append(c)
        except:
            print("Invalid Regex.")
    else:
        # Normal search
        q = query.lower()
        for c in data:
            blob = f"{c['name']} {c['phone']} {c['email']} {c['tags']}".lower()
            if q in blob:
                results.append(c)
    
    show_list(results)

# Feature 4: Update
def update_existing():
    name = input("Enter exact name to edit: ").strip()
    data = load_data()
    target = get_contact(name, data)
    
    if not target:
        print("Not found.")
        return
    
    print(f"Editing {target['name']} (Press Enter to keep current value)")
    
    p = input(f"Phone [{target['phone']}]: ").strip()
    e = input(f"Email [{target['email']}]: ").strip()
    t = input(f"Tags [{target['tags']}]: ").strip()
    f = input(f"Fav (y/n) [current: {target['favorite']}]: ").strip().lower()

    if p: target["phone"] = clean_phone(p)
    if e: target["email"] = e
    if t: target["tags"] = t
    if f in ["y", "yes"]: target["favorite"] = True
    elif f in ["n", "no"]: target["favorite"] = False
    
    save_data(data)
    print("Updated.")

# Feature 5: Delete
def delete_one():
    name = input("Enter name to delete: ").strip()
    data = load_data()
    
    # Filter out the one we want to delete
    new_list = [c for c in data if c["name"].lower() != name.lower()]
    
    if len(new_list) == len(data):
        print("Contact not found.")
    else:
        save_data(new_list)
        print("Deleted.")

# Features 8 & 13: Import CSV / Merge Duplicates
def import_csv_bulk():
    fname = input("CSV Filename to import: ").strip()
    if not os.path.exists(fname):
        print("File doesn't exist.")
        return
    
    try:
        with open(fname, "r") as f:
            reader = csv.DictReader(f)
            new_items = []
            for r in reader:
                # Basic mapping
                item = {
                    "name": r.get("name", "").strip(),
                    "phone": clean_phone(r.get("phone", "")),
                    "email": r.get("email", "").strip(),
                    "tags": r.get("tags", ""),
                    "favorite": r.get("favorite", "").lower() in ["1", "true", "y"]
                }
                if item["name"]:
                    new_items.append(item)
        
        current = load_data()
        current.extend(new_items)
        save_data(current)
        print(f"Imported {len(new_items)} contacts.")
    except Exception as e:
        save_error("import_csv", e)
        print("Import failed.")

def auto_merge():
    data = load_data()
    print("Checking for duplicates...")
    to_remove = []
    
    # Compare every contact with every other contact
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            c1 = data[i]
            c2 = data[j]
            
            # Check similarity
            ratio = SequenceMatcher(None, c1["name"].lower(), c2["name"].lower()).ratio()
            if ratio > 0.9: # 90% match
                print(f"\nMatch: {c1['name']} <--> {c2['name']}")
                choice = input("Merge into one? (y/n): ").lower()
                if choice == 'y':
                    # Combine data into c1
                    if not c1['phone']: c1['phone'] = c2['phone']
                    c1['tags'] = c1['tags'] + "," + c2['tags']
                    to_remove.append(j)
    
    # Create clean list
    final_list = [data[i] for i in range(len(data)) if i not in to_remove]
    if len(final_list) != len(data):
        save_data(final_list)
        print("Duplicates merged.")
    else:
        print("No duplicates merged.")

# Export features
def export_json():
    data = load_data()
    with open(json_db, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved to {json_db}")

def export_vcard():
    name = input("Name for vCard: ").strip()
    data = load_data()
    c = get_contact(name, data)
    if not c:
        print("Not found.")
        return
    
    fname = c["name"].replace(" ", "_") + ".vcf"
    with open(fname, "w") as f:
        f.write("BEGIN:VCARD\nVERSION:3.0\n")
        f.write(f"N:{c['name']}\n")
        if c['phone']: f.write(f"TEL:{c['phone']}\n")
        if c['email']: f.write(f"EMAIL:{c['email']}\n")
        f.write("END:VCARD\n")
    print(f"Created {fname}")

# Backup Ops
def manual_backup():
    try:
        check_folder(backup_folder)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(backup_folder, f"manual_backup_{ts}.csv")
        shutil.copy2(db_file, dst)
        print(f"Backup saved: {dst}")
    except Exception as e:
        print(f"Backup failed: {e}")

def restore_backup():
    check_folder(backup_folder)
    files = sorted(os.listdir(backup_folder))
    csvs = [x for x in files if x.endswith(".csv")]
    
    if not csvs:
        print("No backups found.")
        return

    print("Backups available:")
    for idx, f in enumerate(csvs):
        print(f"{idx+1}. {f}")
    
    try:
        sel = int(input("Select number: ")) - 1
        target = csvs[sel]
        shutil.copy2(os.path.join(backup_folder, target), db_file)
        print("Restored.")
    except:
        print("Invalid selection.")

def undo_change():
    prev = get_last_snapshot()
    if prev is None:
        print("Nothing to undo.")
        return
    
    # Write without creating a new snapshot loop
    save_data(prev, do_backup=False, save_undo=False)
    print("Undo complete.")

def main():
    init_db()
    while True:
        print("\n--- Gaurav Contact Manager ---")
        print("1. Add Contact")
        print("2. View List")
        print("3. Search")
        print("4. Update")
        print("5. Delete")
        print("6. Export JSON")
        print("7. Import JSON")
        print("8. Import CSV")
        print("9. Export vCard")
        print("10. Backup")
        print("11. Restore")
        print("12. Undo")
        print("13. Merge Duplicates")
        print("14. Quit")
        
        ch = input("Choice: ").strip()
        
        if ch == "1": add_new()
        elif ch == "2": 
            k = input("Sort by (name/favorite): ").strip() or "name"
            show_list(load_data(), k)
        elif ch == "3": search_db()
        elif ch == "4": update_existing()
        elif ch == "5": delete_one()
        elif ch == "6": export_json()
        elif ch == "7": 
            # Simple JSON import wrapper
            try:
                with open(json_db) as f:
                    d = json.load(f)
                    save_data(d)
                    print("Imported.")
            except: print("Failed.")
        elif ch == "8": import_csv_bulk()
        elif ch == "9": export_vcard()
        elif ch == "10": manual_backup()
        elif ch == "11": restore_backup()
        elif ch == "12": undo_change()
        elif ch == "13": auto_merge()
        elif ch == "14": break
        else: print("Invalid option.")

if __name__ == "__main__":
    main()