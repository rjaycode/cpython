import random
import re
from datetime import datetime, timedelta

# Global Reference Date
SYSTEM_DATE_STR = "04/15/2026"
SYSTEM_NOW = datetime.strptime(SYSTEM_DATE_STR, "%m/%d/%Y")

def get_input(prompt):
    val = input(f"{prompt} (or type 'back' to cancel): ").strip()
    if val is None or val.lower() == 'back':
        return None
    return val

def get_full_name(prompt, existing_names):
    while True:
        val = get_input(f"{prompt} (e.g., Jaso, Jherwin S.)")
        if val is None: return None
        
        # Regex for: Last Name, First Name M.I.
        pattern = r"^[a-zA-Z\s]+,\s[a-zA-Z\s]+\s[A-Z]\.$"
        
        if re.match(pattern, val):
            if val.lower() in [n.lower() for n in existing_names]:
                print(f"Error: The name '{val}' already exists in our records.")
                continue
            return val
        print("Error: Use format 'Last Name, First Name M.I.' (e.g., Jaso, Jherwin S.)")

def get_valid_contact():
    while True:
        contact = get_input("Enter Contact Number (09xxxxxxxxx)")
        if contact is None: return None
        if re.match(r"^09\d{9}$", contact):
            return contact
        print("Error: Must start with 09 and be 11 digits.")

def get_valid_date(prompt):
    while True:
        date_in = get_input(f"{prompt} (MM/DD/YYYY or 'unknown')")
        if date_in is None: return None
        if date_in.lower() == 'unknown':
            return SYSTEM_DATE_STR
        
        if re.match(r"^(0[1-9]|1[0-2])/(0[1-9]|[0-9]|3)/\d{4}$", date_in):
            try:
                input_date = datetime.strptime(date_in, "%m/%d/%Y")
                if input_date > SYSTEM_NOW:
                    print(f"Error: Date cannot be beyond system date ({SYSTEM_DATE_STR}).")
                    continue
                return date_in
            except ValueError:
                print("Error: Invalid calendar date.")
                continue
        print("Error: Use format MM/DD/YYYY or 'unknown'.")

def get_valid_time(prompt, input_date_str):
    while True:
        time_in = get_input(f"{prompt} (HH:MM AM/PM or 'unknown')")
        if time_in is None: return None
        if time_in.lower() == 'unknown':
            return "UNKNOWN"
        
        pattern = r"^(0[1-9]|1[0-2]):([0-5][0-9])\s?(AM|PM)$"
        if re.match(pattern, time_in.upper()):
            return time_in.upper()
        print("Error: Use format HH:MM AM/PM (e.g., 10:30 AM) or 'unknown'.")

def print_vertical(item, type_label):
    print(f"\n--- [{type_label}] DETAILS ---")
    print(f"ID         : {item.get('id')}")
    print(f"Item Name  : {item.get('name')}")
    print(f"Status     : {type_label}")
    print(f"Date       : {item.get('date')}")
    print(f"Time       : {item.get('time')}")
    print(f"Location   : {item.get('loc')}")
    if type_label == "LOST ITEM":
        print(f"Description: {item.get('desc')}")
        print(f"Owner      : {item.get('owner')}")
    else:
        print(f"Target Owner: {item.get('owner', 'Unknown')}")
        print(f"Finder      : {item.get('finder')}")
    print(f"Contact    : {item.get('contact')}")
    print("-" * 25)

def clean_old_items(items):
    cutoff = SYSTEM_NOW - timedelta(days=150)
    return [i for i in items if datetime.strptime(i['date'], "%m/%d/%Y") >= cutoff]

def lost_and_found_system():
    global SYSTEM_DATE_STR, SYSTEM_NOW
    users = {} 
    lost_items = []
    found_items = []
    claimed_items = []

    while True:
        lost_items = clean_old_items(lost_items)
        found_items = clean_old_items(found_items)

        # Helper lists for duplicate checking
        current_owners = [i['owner'] for i in lost_items]
        current_finders = [i['finder'] for i in found_items]

        print(f"\n--- Welcome to Lost and Found System | Date: {SYSTEM_DATE_STR} ---")
        print("1. Register\n2. Log In\n3. Update System Date\n4. Exit")
        choice = input("Select option: ")

        if choice == '1':
            name = get_full_name("Register Full Name", users.keys())
            if name is None: continue
            pw = get_input("Enter Password")
            if pw is None: continue
            users[name] = pw
            print("Registration successful!")

        elif choice == '2':
            # Use blank list for login so it doesn't block the existing user
            name = get_input("Login Name (Last Name, First Name M.I.)")
            pw = get_input("Password")
            if name in users and users[name] == pw:
                while True:
                    print(f"\n--- User Menu: Welcome {name} ---")
                    print("1. Search Item\n2. Enter Lost Item\n3. Report Found Item")
                    print("4. Display Lost Items\n5. Display Found Items\n6. Mark Claimed\n7. Logout")
                    u_choice = input("Choice: ")

                    if u_choice == '1':
                        q = get_input("Search Name/ID/Owner")
                        if q:
                            q_low = q.lower()
                            for i in lost_items: 
                                if q_low in i['name'].lower() or q == str(i['id']) or q_low in i['owner'].lower(): 
                                    print_vertical(i, "LOST ITEM")
                            for i in found_items: 
                                if q_low in i['name'].lower() or q == str(i['id']): 
                                    print_vertical(i, "FOUND ITEM")

                    elif u_choice == '2':
                        i_name = get_input("Item Name")
                        loc = get_input("Location")
                        desc = get_input("Description")
                        owner = get_full_name("Owner's Full Name", current_owners)
                        contact = get_valid_contact()
                        date = get_valid_date("Date Lost")
                        time = get_valid_time("Time Lost", date)
                        if all([i_name, loc, desc, owner, contact, date, time]):
                            lost_items.append({'id': random.randint(1000, 9999), 'name': i_name, 'loc': loc, 'desc': desc, 'owner': owner, 'contact': contact, 'date': date, 'time': time})
                            print(f"Recorded! ID: {lost_items[-1]['id']}")

                    elif u_choice == '3':
                        print("\n1. Link to Lost ID\n2. New Found Report")
                        sub = input("Choice: ")
                        if sub == '1':
                            tid = get_input("Enter Lost ID")
                            ref = next((i for i in lost_items if str(i['id']) == tid), None)
                            if ref:
                                f_loc = get_input("Found Where?")
                                f_date = get_valid_date("Date Found")
                                f_time = get_valid_time("Time Found", f_date)
                                finder = get_full_name("Finder's Full Name", current_finders)
                                f_con = get_valid_contact()
                                if all([f_loc, f_date, f_time, finder, f_con]):
                                    found_items.append({'id': ref['id'], 'name': ref['name'], 'owner': ref['owner'], 'loc': f_loc, 'date': f_date, 'time': f_time, 'finder': finder, 'contact': f_con})
                                    lost_items.remove(ref)
                                    print("Status updated to FOUND!")
                        elif sub == '2':
                            i_name = get_input("Item Name")
                            f_loc = get_input("Found Where?")
                            f_date = get_valid_date("Date Found")
                            f_time = get_valid_time("Time Found", f_date)
                            finder = get_full_name("Finder's Full Name", current_finders)
                            f_con = get_valid_contact()
                            if all([i_name, f_loc, f_date, f_time, finder, f_con]):
                                found_items.append({'id': random.randint(1000, 9999), 'name': i_name, 'owner': 'Unknown', 'loc': f_loc, 'date': f_date, 'time': f_time, 'finder': finder, 'contact': f_con})
                                print(f"New Found Record created! ID: {found_items[-1]['id']}")

                    elif u_choice == '4':
                        if not lost_items: print("No lost items.")
                        else: [print_vertical(i, "LOST ITEM") for i in lost_items]

                    elif u_choice == '5':
                        if not found_items: print("No found items.")
                        else: [print_vertical(i, "FOUND ITEM") for i in found_items]

                    elif u_choice == '6':
                        tid = get_input("Enter ID to claim")
                        found_in_list = False
                        for l in [lost_items, found_items]:
                            item = next((i for i in l if str(i['id']) == tid), None)
                            if item:
                                claimed_items.append(l.pop(l.index(item)))
                                print("Item marked as Claimed!")
                                found_in_list = True
                                break
                        if not found_in_list: print("ID not found.")

                    elif u_choice == '7':
                        break
            else:
                print("Login Failed.")

        elif choice == '3':
            new_date = get_input("Enter New System Date (MM/DD/YYYY)")
            if new_date:
                try:
                    SYSTEM_NOW = datetime.strptime(new_date, "%m/%d/%Y")
                    SYSTEM_DATE_STR = new_date
                    print(f"System date updated to {SYSTEM_DATE_STR}.")
                except ValueError: print("Invalid format.")

        elif choice == '4':
            print("Exiting...")
            break

if __name__ == "__main__":
    lost_and_found_system()
