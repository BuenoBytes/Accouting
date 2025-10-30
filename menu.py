from datetime import datetime
import root
import reports
import json
import os

def loadjson(path: str, obj: object) -> object:
    with open(path, "r", encoding="utf-8") as f:
        x = json.load(f)
    return {k: obj(*v) for k, v in x.items()}
    
def savejson(path: str, obj: object, data: object) -> None:
    data = {k: v.to_list() for k, v in data.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def joinpath(paths: list[str]) -> str:
    return os.path.join(*paths)

print('Welcome to my accounting and finnancing admnistration system. A study project.')
e = '_entities.json'
a = '_accounts.json'
cc = '_costcenters.json'
while True:
    print('Choose a module:')
    match root.inputopt(' [ 1 ] Entities. \n [ 2 ] Accounts. \n [ 3 ] Cost centers. \n [ 4 ] Entries. \n [ 5 ] Invoices. \n [ 6 ] Reports \n [ C ] Close. \n', ['1', '2', '3', '4', '5', '6','C'], True):
        case 'C':
            print('Bye!')
            break
        case '1':
            ef = loadjson(e, root.Entity)
            while True:
                match root.inputopt('Choose an action: \n [ 1 ] New. \n [ 2 ] Edit. \n [ S ] Save and return. \n', ['S', '1', '2'], True):
                    case 'S':
                        ef = {k: v.to_list() for k, v in ef.items()}
                        savejson(e, root.Entity, ef)
                        root.shell_block()
                        break
                    case '1':
                        root.Entity.new(False, ef)
                    case '2':
                        root.Entity.edit(ef)
        case '2':
            af = loadjson(a, root.Account)
            while True:
                match root.inputopt('Choose an action: \n [ 1 ] New. \n [ 2 ] Edit. \n [ S ] Save and return. \n', ['S', '1', '2'], True):
                    case 'S':
                        af = root.sort_keys(af)
                        savejson(a, root.Account, af)
                        root.shell_block()
                        break
                    case '1':
                        root.Account.new(af)
                    case '2':
                        root.Account.edit(af)
        case '3':
            ccf = loadjson(cc, root.CostCenter)
            while True:
                match root.inputopt('Choose an action: \n [ 1 ] New. \n [ 2 ] Edit. \n [ S ] Save and return. \n', ['S', '1', '2'], True):
                    case 'S':
                        savejson(cc, root.CostCenter, ccf)
                        root.shell_block()
                        break
                    case '1':
                        root.CostCenter.new(ccf)
                    case '2':
                        root.CostCenter.edit(ccf)
        case '4':
            year = root.inputst('On this system, the entries are organized by year. Type the year that you want to manipulate. ')
            check = False
            with open('_criteria.json', "r", encoding="utf-8") as f:
                criteria = json.load(f)
            last = criteria['last_entry']
            lock = criteria['lock']
            try:
                yearint = int(year)
            except:
                print('Invalid year input.')
                check = True
            if not check:
                etr = joinpath(['entries', f"{year}.json"])
                ef = loadjson(e, root.Entity)
                af = loadjson(a, root.Account)
                ccf = loadjson(cc, root.CostCenter)
                if os.path.exists(etr):
                    etrf = loadjson(etr, root.Entry)
                else:
                    etrf = {}
                while True:
                    match root.inputopt('Choose an action: \n [ 1 ] New. \n [ 2 ] Edit. \n [ 3 ] Import from a tsv file. \n [ 4 ] Close the year. \n [ S ] Save and retunr. \n', ['S', '1', '2', '3', '4'], True):
                        case 'S':
                            savejson(etr, root.Entry, etrf)
                            root.shell_block()
                            criteria['last_entry'] = last
                            with open('_criteria.json', "w", encoding="utf-8") as f:
                                json.dump(criteria, f, ensure_ascii=False, indent=4)
                            break
                        case '1':
                            root.Entry.new(etrf, ef, af, ccf, last, lock)
                            last += 1
                        case '2':
                            root.Entry.edit(etrf, ef, af, ccf, lock)
                        case '3':
                            print('That has to be saved on the input_output file a tsv file named input.tsv on wich each row is an entry, following this format: \n [entity , date(ISO), history, document, value, dr. account, dr. cost center, cr. account, cr. cost center]')
                            if root.yes_no('Do you want to continue? [Y/N]'):
                                path = joinpath(['input_output', 'input.tsv'])
                                if os.path.exists(path):
                                    print("File found.")
                                with open(path, "r", encoding="utf-8") as f:
                                    file = f.read()
                                last = root.Entry.importf(etrf, ef, af, ccf, last, file, lock, yearint)
                            else:
                                print('Operation cancelled.')
                        case '4':
                            b = joinpath(['balances', f"{year}.json"])
                            dt = datetime(yearint, 12, 31)
                            if datetime.fromisoformat(lock) <  dt:
                                balances = root.BalanceData.process(datetime(yearint, 1, 1), dt)
                                savejson(b, root.BalanceData, balances)
                                criteria['lock'] = dt.isoformat()
                                with open('_criteria.json', "w", encoding="utf-8") as f:
                                    json.dump(criteria, f, ensure_ascii=False, indent=4)
                                print(f"Year of {year} closed with success.")
                            else:
                                print("The year of {year} is already closed.")
        case '6':
            ef = loadjson(e, root.Entity)
            af = loadjson(a, root.Account)
            ccf = loadjson(cc, root.CostCenter)
            match root.inputopt('Choose a report: \n [ 1 ] Trial balance. \n [ R ] Return to main menu. \n', ['1', 'R'], True):
                case '1':
                    file = reports.trial_balance(ef, af)
                    path = os.path.join('input_output', 'output.txt')
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(file)
        case _:
            print("Function don't added yet.")

