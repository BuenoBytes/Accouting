from datetime import datetime
from pathlib import Path
from typing import cast
import tools
import classes

# OBS: Note that the '_comp' suffix is to indicate an composed strings splitted by "%"

def search_data_bank(id_comp: str) -> str:
    path = Path("data_bank")/f"{id_comp}.tsv"
    if path.exists():
        return str(path)
    else:
        raise FileNotFoundError(f"File not found: {path}")

def read_file(path: str) -> classes.File_structure:
    data: classes.File_structure = {
        "zero": classes.Zero("Waiting data", "2025-01-01T00:00:00", "", "2025-01-01T00:00:00"),
        "entities": {},
        "accounts": {},
        "cost_centers": {},
        "entries": {}
    }
    with open(path, "r", encoding="utf-8") as raw:
        for item in raw:
            row_array = [field.strip() for field in item.split("\t")]
            try:
                match row_array[0]:
                    case "ZERO":
                        data["zero"] = classes.Zero(*row_array[1:])
                    case "ENTI":
                        class_object = classes.Entity(*row_array[1:])
                        data["entities"][class_object.id[0]+"%"+class_object.id[1]] = class_object
                    case "ACCO":
                        class_object = classes.Account(*row_array[1:])
                        data["accounts"][class_object.id] = class_object
                    case "CCEN":
                        class_object = classes.Cost_center(*row_array[1:])
                        data["cost_centers"][class_object.id] = class_object
                    case "ENTR":
                        class_object = classes.Entry(*row_array[1:])
                        data["entries"][class_object.id] = class_object
                    case _:
                        print(f"****** Processing error [Unknown tag] - {row_array[0]} at row {item} ******")
            except Exception as e:
                print(f"****** Processing error [{type(e).__name__}] - {e} at row {item} ******")
    return data

def save_file_changes(data: classes.File_structure) -> None:
    path = Path("data_bank")/data["zero"].name
    new_file_array: list[str] = []
    data["zero"].last_change = datetime.now()
    new_file_array.append(data["zero"].tsv_string())
    for key in data["entities"]:
        new_file_array.append(data["entities"][key].tsv_string())
    for key in data["accounts"]:
        new_file_array.append(data["accounts"][key].tsv_string())
    for key in data["cost_centers"]:
        new_file_array.append(data["cost_centers"][key].tsv_string())
    for key in data["entries"]:
        new_file_array.append(data["entries"][key].tsv_string())
    with open(path, "w", encoding='utf-8') as f:
        f.write("\n".join(new_file_array))
    print("File changes saved with success.")

def new_file() -> None:
    file_array: list[str] = []

    # ZERO

    file_date = datetime.now()
    file_date_iso = datetime.strftime(file_date, tools.iso_datetime)
    id_comp =  input("Write an document number and its type of the main entity that will be recorded on the file [number%type]: ")
    try:
        search_data_bank(id_comp)
    except:
        print("New ID identified, please continue with the file creation.")
    else:
        raise ValueError(f"A file with the ID {id_comp} already exists!")
    row = classes.Zero(id_comp+".tsv", file_date_iso, "", file_date_iso)
    file_array.append(row.tsv_string())

    # ENTITIES

    print("Provide more data about the main entity of the file.")
    type = tools.input_with_options("Type of entity (Just press ENTER if it is an individual, type '1' if it is an legal entity):\n", ["", "1"])
    legal_name = input("Legal name: ").strip()
    trade_name = input("Trade name: ").strip() if type else ""
    country_comp = input("Country and its code [country%code]: ").strip()
    state_comp = input("State and its code [state%code]: ").strip()
    city_comp = input("City and its code [city%code]: ").strip()
    open_date = tools.input_date_checker("Entity born/open date [ISO]: ")
    close_date = tools.input_date_checker("Entity death/close date [ISO]: ", False)
    row = classes.Entity(id_comp, type, legal_name+"%"+trade_name, country_comp, state_comp, city_comp, open_date, close_date).tsv_string()
    file_array.append(row)
    if bool(type):
        used_IDs: list[str] = []
        used_IDs.append(id_comp)
        while True:
            if tools.input_with_options("That are a new branch to report? [Y/N] ", ["Y", "N"], True) == "Y":
                print("Provide data about the branch that you desire to record.")
                id_comp = input("Document number and its type [number%type]: ")
                if id_comp in used_IDs:
                    print("That already is an recorded entry with that ID!")
                else:
                    legal_name = input("Legal name: ").strip()
                    trade_name = input("Trade name: ").strip() if type else ""
                    country_comp = input("Country and its code [country%code]: ").strip()
                    state_comp = input("State and its code [state%code]: ").strip()
                    city_comp = input("City and its code [city%code]: ").strip()
                    open_date = tools.input_date_checker("Entity born/open date [ISO]: ")
                    close_date = tools.input_date_checker("Entity death/close date [ISO]: ", False)
                    row = classes.Entity(id_comp, type, legal_name+"%"+trade_name, country_comp, state_comp, city_comp, open_date, close_date).tsv_string()
                    file_array.append(row)
                    used_IDs.append(id_comp)
            else:
                break
    
    # CHART OF ACCOUNTS

    print("By standard, will be recorded on the file the hard coded (probably)IFRS compliant Chart of Accounts, with Expenses by Nature. Costs can be measured with Cost Centers.")
    chart = tools.chart_of_accounts
    for item in chart:
        class_obj = classes.Account(item[0], item[1], datetime.strftime(file_date, tools.iso_date))
        file_array.append(class_obj.tsv_string())

    # COST CENTERS
    used_IDs: list[str] = []
    print("In this system Cost Centers are used to generate reports with expenses by funtion.")
    while True:
        if tools.input_with_options("Do you want to record a new Cost Center? ", ["Y", "N"], True) == "Y":
            print("Provide data for the new Cost Center.")
            id = input("ID: ").strip()
            if id in used_IDs:
                print("That already is an Cost Center with that ID recorded.")
            else:
                name = input("Name: ")
                open_date = tools.input_date_checker("Open date [ISO]]: ")
                row = classes.Cost_center(id, name, open_date, "").tsv_string()
                file_array.append(row)
                used_IDs.append(id)
        else:
            break
    
    # FILE RECORDING

    with open(Path("data_bank")/file_array[0].split("\t")[1], "w", encoding="utf-8") as f:
        f.write("\n".join(file_array))
    print("File created with success.")

def new_entity(data: classes.File_structure) -> None:
    while True:
        used_IDs = data["entities"].keys()
        print("Provide data about the entity that you want to record.")
        id_comp = input("Legal document number and type [number%type] [X to return]: ").strip()
        if id_comp in used_IDs:
            print("That already is an entity with that ID recorded on the file!")
        elif id_comp == "X":
            print("New entity record cancelled.")
            break
        else:
            legal_name = input("Legal name: ").strip()
            trade_name = input("Trade name: ").strip()
            country_comp = input("Country and its code [country%code]: ").strip()
            state_comp = input("State and its code [state%code]: ").strip()
            city_comp = input("City and its code [city%code]: ").strip()
            open_date = tools.input_date_checker("Entity born/open date [ISO]: ")
            close_date = tools.input_date_checker("Entity death/close date [ISO]: ", False)
            entity = classes.Entity(id_comp, "1", legal_name+"%"+trade_name, country_comp, state_comp, city_comp, open_date, close_date)
            data["entities"][id_comp] = entity

def edit_entity(data: classes.File_structure) -> None:

    def check_composed(string: str) -> str:
        while True:
            if string.count("%") == 1:
                return string
            else:
                print("Invalid input. That wasn't detected the split identifier '%'.")

    while True:
        key = input("Key of the entity that you desire to edit [document_number%document_type] [B to return]: ").strip()
        used_IDs = list(data["entities"].keys())
        if key in used_IDs:
            while True:
                match input("Choose what you desire to change:\n 1 - ID [document_number%document_type]\n 2 - Legal name\n 3 - Trade name\n 4 - Country [name%code]\n 5 - State [name%code]\n 6 - City [name%code]\n 7 - Born/open date\n 8 - Death/close date\n B - Back").strip():
                    case "1":
                        id_comp = check_composed(input("Write the new ID: ").strip())
                        if id_comp in used_IDs:
                            print("That ID is already begin used on the file.")
                        elif key == used_IDs[0]:
                            data["zero"].name = id_comp + ".tsv"
                            data["entities"][key] = data['entities'].pop(id_comp)
                            for entry in data["entries"]:
                                if data["entries"][entry].entity == key:
                                    data["entries"][entry].entity = id_comp
                            print("ID changed with success. Returning because the key changed.")
                            break
                    case "2":
                        print(f"Current legal name: {data['entities'][key].name[0]}")
                        legal_name = input("New legal name: ").strip()
                        data["entities"][key].name[0] = legal_name
                        print("Legal name changed with success.")
                    case "3":
                        print(f"Current trade name: {data['entities'][key].name[1]}")
                        trade_name = input("New trade name: ").strip()
                        data["entities"][key].name[1] = trade_name
                        print("Trade name changed with success.")
                    case "4":
                        print(f"Current country name%code: {data['entities'][key].country}")
                        country_comp = input("New name%code: ").strip().split("%")
                        data["entities"][key].country = country_comp
                        print("Country name%code changed with success.")
                    case "5":
                        print(f"Current state name%code: {data['entities'][key].state}")
                        state_comp = input("New name%code: ").strip().split("%")
                        data["entities"][key].state = state_comp
                        print("State name%code changed with success.")
                    case "6":
                        print(f"Current city name%code: {data['entities'][key].city}")
                        city_comp = input("New name%code: ").strip().split("%")
                        data["entities"][key].city = city_comp
                        print("City name%code changed with success.")
                    case "7":
                        print(f"Current born/open date: {data["entities"][key].born_date}")
                        new_date_str = tools.input_date_checker("New born/open date: ")
                        new_date_obj = datetime.strptime(new_date_str, tools.iso_date)
                        data["entities"][key].born_date = new_date_obj
                        print("Born/open date changed with success.")
                    case "8":
                        print(f"Current death/close date: {data["entities"][key].death_date}")
                        new_date_str = tools.input_date_checker("New death/close date: ")
                        new_date_obj = datetime.strptime(new_date_str, tools.iso_date)
                        data["entities"][key].death_date = new_date_obj
                        print("Death/close date changed with success.")
                    case "B":
                        print("Returning.")
                        break
                    case _:
                        print("Invalid input.")
        elif key == "B":
            break
        else:
            print("Invalid input.")

def new_account(data: classes.File_structure) -> None:
    while True:
        used_IDs = list(data["accounts"].keys())
        id = input("Type an unused ID of the new account that you desire to record: [Type B to return]").strip()
        if id == "B":
            break
        test = classes.Account(id, "TEST", "2025-01-01")
        if id in used_IDs:
            print("That already is an account with that ID!")
        elif len(id) > 11:
            print("Invalid ID! Lenght higher than 11.")
        elif test.parent_ID() in used_IDs:
            if data["accounts"][test.parent_ID()].type == "A":
                print("The upper account for that ID can't be a parent!")
            else:
                name = input("Type a name for the new account (Only upper if it is a synthetic): ").strip()
                if len(name) > 37:
                    print("Invalid name! Lenght higher than 37.")
                else:
                    question = tools.input_with_options(f"Confirm new record? [Y/N]\n {id} - {name}\n Parent: {test.parent_ID()} - {data['accounts'][test.parent_ID()].name}\n", ["Y", "N"], True)
                    if question == "Y":
                        data["accounts"][id] = classes.Account(id, name, datetime.strftime(datetime.now(), tools.iso_date))
                        print("New account recorded with success.")
                    else:
                        print("New account recording cancelled.")               
        else:
            print("That isnt a parent account for that ID yet!")

def edit_account(data: classes.File_structure) -> None:
    while True:
        used_IDs = list(data["accounts"].keys())
        key = input("Type the ID of the account that you desire to edit: [B - Back]").strip()
        if key in used_IDs:
            selected_account = data["accounts"][key]
            print(f"Account selected: {key} - {selected_account.name}")
            if selected_account.type == "A":
                invalid_keys = []
                for k in data["entries"]:
                    if data["entries"][k].dr_acc not in invalid_keys:
                        invalid_keys.append(data["entries"][k].dr_acc)
                    if data["entries"][k].cr_acc not in invalid_keys:
                        invalid_keys.append(data["entries"][k].cr_acc)
                if selected_account.id in invalid_keys:
                    print("That account is begin usued on an entry, so it cannot be edited.")
                else:
                    new_name = input("Type a new name for the account, use caps only if it will be an parent: ").strip()
                    selected_account.name = new_name
                    selected_account.date = datetime.now()
                    if new_name == new_name.upper():
                        selected_account.type = "S"
                    else:
                        selected_account.type = "A"
            else:
                can_be_edited: bool = True
                for k in data["accounts"]:
                    if selected_account.id == data["accounts"][k].parent_ID():
                        print("The selected account has sons, therefore cannot be edited.")
                        can_be_edited = False
                        break
                if can_be_edited is True and selected_account.parent_ID() != "":
                    new_name = input("Type a new name for the account, use caps only if it will be an parent: ").strip()
                    selected_account.name = new_name
                    selected_account.date = datetime.now()
                    if new_name == new_name.upper():
                        selected_account.type = "S"
                    else:
                        selected_account.type = "A"
                elif can_be_edited is True:
                    print("The selected account is an root account, therefore cannot be edited.")
        elif key.upper() == "B":
            break
        else:
            print(f"Account {key} not found!")

def new_cost_center(data: classes.File_structure) -> None:
    while True:
        used_IDs = list(data["cost_centers"].keys())
        key = input("Type an ID for the cost center that you desire to record [B - Back]: ").strip()
        if key == "B":
            break
        elif key in used_IDs:
            print("That already is a cost center with that ID!")
        else:
            name = input("Type a name for the new cost center: ").strip()
            new_cost_center = classes.Cost_center(key, name, datetime.strftime(datetime.now(), tools.iso_date), "")
            data["cost_centers"][key] = new_cost_center

def edit_cost_center(data: classes.File_structure) -> None:
    print("Until now, is only possible to edit an cost center name or its closing.")
    while True:
        used_IDs = list(data["cost_centers"].keys())
        key = input("Type an ID for the cost center that you desire to edit [B - Back]: ").strip()
        if key in used_IDs:
            print(f"{data['cost_centers'][key].id} - {data['cost_centers'][key].name}")
            question = tools.input_with_options("What do you want to edit?\n 1 - Name\n 2 - Close it\n 3 - Cancel closing\n B - Back", ["1", "2", "3","B"], True)
            match question:
                case "1":
                    name = input("Type a new name for the selected cost center: ").strip()
                    data["cost_centers"][key].name = name
                    print("Cost center name updated with success.")
                case "2":
                    data["cost_centers"][key].close_date = datetime.now()
                case "3":
                    data["cost_centers"][key].close_date = None
                case "B":
                    break
                case _:
                    print("Invalid option!")
        elif key == "B":
            break
        else:
            print(f"Cost center {key} not found!")

def new_entry(data: classes.File_structure) -> None:
    print("Type data of the entry that you desire to record.")

    valid_entities = list(data['entities'].keys())
    valid_accounts_keys: list[str] = [] 
    for key in list(data["accounts"].keys()):
        account_obj = data["accounts"][key]
        if account_obj.type == "A":
            valid_accounts_keys.append(key)

    entity = tools.input_with_options("Referent entity ID [doc_code%doc_type]: ", valid_entities)
    date_str = tools.input_date_checker("Date [ISO]: ")
    date_obj = datetime.strptime(date_str, tools.iso_date)
    active_ccen_keys: list[str] =[]
    for key in  list(data["cost_centers"].keys()):
        cost_center_obj = data["cost_centers"][key]
        if cost_center_obj.open_date <= date_obj and (cost_center_obj.close_date is None or date_obj <= cost_center_obj.close_date):
            active_ccen_keys.append(key)
    year_entries_amount = 0
    for key in list(data["entries"].keys()):
        entry_date_obj = data["entries"][key].date
        if date_obj.year == entry_date_obj.year:
            year_entries_amount += 1
    id = f"{date_obj.year}{year_entries_amount + 1:06d}"

    value = input("Value: ").strip()
    dr_acc = tools.input_with_options("Debit account: ", valid_accounts_keys)
    cr_acc = tools.input_with_options("Credit account: ", valid_accounts_keys)
    history = input("Histoy: ").strip()
    document = input("Document: ").strip()
    if len(active_ccen_keys) > 0:
        dr_cost_center = tools.input_with_options("Debit cost center: ", active_ccen_keys) if dr_acc[0:2] == "5.1" else ""
        cr_cost_center = tools.input_with_options("Credit cost center: ", active_ccen_keys) if cr_acc[0:2] == "5.1" else ""
    else:
        dr_cost_center = cr_cost_center = ""
    print(f"Check the entry data:\n ID: {id}\n Referent entity: {entity}\nDate: {date_str}\n Value: {value}\n Debit account: {dr_acc}\n Credit account: {cr_acc}\n History: {history}\n Document: {document}\n Debit cost center: {dr_cost_center}\n Credit cost center: {cr_cost_center}\n")
    question = tools.input_with_options("Confirm entry recording? [Y/N] ", ["Y", "N"], True)
    if question == "Y":
        data["entries"][id] = classes.Entry(id, entity, "N", date_str, value, dr_acc, cr_acc, history, document, dr_cost_center, cr_cost_center)
        print("Entry recorded with success.")
    else:
        print("Recording cancelled.")

def import_entries(data: classes.File_structure) -> None:
    print("To import entries, they should be saved on a tsv file named input.tsv, on the input_output folder. Each row should have the following format:\n [Entity ID [doc_code%doc_type], Date[ISO], Value, Debit acc., Credit acc., History, Document, Debit cost cen., Credit cost cen.]")
    match tools.input_with_options("Is the file ready and do you want to continue? [Y/N]\n", ["Y", "N"], True):
        case "Y":
            year_counter: dict[int, int] = {}
            with open(Path('input_output/input.tsv'), "r", encoding="utf-8") as file:
                for row in file:
                    array = row.strip().split("\t")
                    try:

                        # VERIFICATIONS
                        date_obj = datetime.strptime(array[1], tools.iso_date)
                        ent_keys = list(data['entities'].keys())
                        if array[0] not in ent_keys:
                            raise ValueError(f"{array[0]} is not an valid entity_ID !!!")
                        acc_keys = list(data['accounts'].keys())
                        acc_keys = [k for k in acc_keys if data['accounts'][k].type == 'A']
                        if array[3] not in acc_keys:
                            raise ValueError(f"{array[3]} is not an valid account ID !!!")
                        if array[4] not in acc_keys:
                            raise ValueError(f"{array[4]} is not an valid account ID !!!")
                        ccen_keys = list(data['cost_centers'].keys())
                        ccen_keys = [k for k in ccen_keys if data['cost_centers'][k].open_date <= date_obj and (data['cost_centers'][k].close_date is None or data['cost_centers'][k].close_date >= date_obj)]
                        if len(ccen_keys) > 0:
                            if array[3].startswith("5.1") and array[7] not in ccen_keys:
                                raise ValueError(f"Cost center is required for the account {array[3]} but it wasn't informad or it is invalid.")
                            if array[4].startswith("5.1") and array[8] not in ccen_keys:
                                raise ValueError(f"Cost center is required for the account {array[4]} but it wasn't informad or it is invalid.")
                        
                        year = date_obj.year
                        if year not in year_counter:
                            year_counter[year] = sum(
                                1 for entry in data["entries"].values() if entry.date and entry.date.year == year)
                        year_entries = year_counter[year]
                        entry_id = f"{year}{year_entries + 1:06d}"
                        data["entries"][entry_id] = classes.Entry(entry_id, "N", *array)
                        year_counter[year] += 1
                    except (ValueError, IndexError, TypeError) as e:
                        print(f"****** Error processing row {array}: {str(e)}")
                    except Exception as e:
                        print(f"****** Critical error in row {array}: {str(e)}")
        case "N":
            print("Action cancelled.")

def edit_entry(data: classes.File_structure) -> None:
    entries = list(data["entries"].keys())
    question = tools.input_with_options("Type the ID of the entry that you desire to edit [B - Back]: ", [*entries, "B"], True)
    if question == "B":
        print("Returning.")
    elif question in entries:
        while True:
            selected_entry = data["entries"][question]
            valid_accounts = [k for k in list(data["accounts"].keys()) if data["accounts"][k].type == "A"]
            valid_ccens = [k for k in list(data["cost_centers"].keys()) if
                           data["cost_centers"][k].open_date <= selected_entry.date and (
                               data["cost_centers"][k].close_date is None or
                                    cast(datetime , data["cost_centers"][k].close_date) >= selected_entry.date)
                           ]
            valid_entities = list(data['entities'].keys())
            print(f"Current entry data:\n Referent entity: {selected_entry.entity} \n Date: {datetime.strftime(selected_entry.date, tools.iso_date)}\n Value: {selected_entry.value:,.2f}\n Dr.Account: {selected_entry.dr_acc}\n Cr.Account: {selected_entry.cr_acc}\n History: {selected_entry.history}\n Document: {selected_entry.document}\n Dr.Cost center: {selected_entry.dr_ccen}\n Cr.Cost center: {selected_entry.cr_ccen}\n")
            match tools.input_with_options("What do you desire to edit:\n 1 - Referent entity\n 2 - Date\n 3 - Value\n 4 - Debit account\n 5 - Credit account\n 6 - History\n 7 - Document\n 8 - Debit cost center\n 9 - Credit cost center\n B - Back\n", ["1", "2", "3", "4", "5", "6", "7", "8", "B"], True):
                case "1":
                    selected_entry.entity = tools.input_with_options("New referent entity [doc_code%doc_type]: ", valid_entities)
                case "2":
                    date_str = tools.input_date_checker("New date [ISO]: ")
                    selected_entry.date = datetime.strptime(date_str, tools.iso_date)
                case "3":
                    selected_entry.value = float(input("New value [0.00]: ").strip())
                case "4":
                    selected_entry.dr_acc = tools.input_with_options("New debit account: ", valid_accounts)
                case "5":
                    selected_entry.cr_acc = tools.input_with_options("New credit account: ", valid_accounts)
                case "6":
                    selected_entry.history = input("New history: ").strip()
                case "7":
                    selected_entry.document = input("New document: ").strip()
                case "8":
                    if selected_entry.dr_acc[0] == "5" and len(valid_ccens) > 0:
                        selected_entry.dr_ccen = tools.input_with_options("New debit cost center: ", valid_ccens)
                    else:
                        if selected_entry.dr_acc[0] != "5":
                            print(f"****** The debit account {selected_entry.dr_acc} cannot receive a cost center.")
                        if len(valid_ccens) == 0:
                            print("****** That isn't active cost centers on that date.")
                case "9":
                    if selected_entry.cr_acc[0] == "5" and len(valid_ccens) > 0:
                        selected_entry.cr_acc = tools.input_with_options("New credit cost center: ", valid_ccens)
                    else:
                        if selected_entry.cr_acc[0] != "5":
                            print(f"****** The credit account {selected_entry.cr_acc} cannot receive a cost center.")
                        if len(valid_ccens) == 0:
                            print("****** That isn't active cost centers on that date.")
                case "B":
                    break
                case _:
                    print("Invalid input.")
