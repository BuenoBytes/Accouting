from datetime import datetime
import json
import os

def yes_no(question: str) -> bool:
    while True:
        match input(question).strip().upper():
            case 'Y':
                return True
            case 'N':
                return False
            case _:
                print('Invalid input.')

def inputst(text: str) -> str:
    return input(text).strip()

def inputopt(text: str, options: list[str], upper = False) -> str:
    while True:
        choice = inputst(text).upper() if upper else inputst(text)
        if choice not in options:
            print('Invalid input.')
        else:
            return choice

def inputdt(text: str) -> str:
    while True:
        inp = inputst(text)
        try:
            datetime.fromisoformat(inp)
            return inp
        except:
            print('Invalid input.')

def inputfloat(text: str) -> float:
    while True:
        value = inputst(text)
        try:
            return float(value)
        except:
            print('Invalid input.')

def shell_block() -> None:
    for i in range(5):
        print('\n')

def cancel() -> None:
    print('Operation cancelled.')

def sort_keys(to_sort: dict[str, object]) -> dict[str, object]:
    def helper(key: str) -> list[int]:
        return [int(part) for part in key.split('.')]
    return dict(sorted(to_sort.items(), key=lambda x: helper(x[0])))

class Entity:

    def __init__(self, id_key: str, names: list[str], location: list[str], born_dt: str, death_dt: str, individual: bool, main: bool) -> None:
        id_key_array = id_key.split('$')
        if len(id_key_array) != 2:
            raise ValueError(f"Insufficient or too much data on the following Entity's id_key: {id_key}.\nIt should have 2.")
        
        self.id = [id_key, id_key_array[0], id_key_array[1]] # [id_key complete, id document number/code, id document type]
        self.names = names # [legal, trade]
        self.location = location # [country, state, city]
        self.born_dt = datetime.fromisoformat(born_dt)
        self.death_dt = None if death_dt == '' else datetime.fromisoformat(death_dt)
        self.individual = individual # True for individual, False for legal entity
        self.main = main # True if it is the main entity of the file

    def to_list(self) -> list:
        return [
            self.id[0],
            self.names,
            self.location,
            self.born_dt.isoformat(),
            self.death_dt.isoformat() if self.death_dt else '',
            self.individual,
            self.main
            ]

    def __str__(self) -> str:
        death = self.death_dt.isoformat() if self.death_dt else ''
        return f" [ 1 ] ID: {self.id[0]} \n [ 2 ] Legal name: {self.names[0]} \n [ 3 ] Trade name: {self.names[1]} \n [ 4 ] Country, state, city: {self.location} \n [ 5 ] Born date: {self.born_dt.isoformat()} \n [ 6 ] Death date: {death} \n [ 7 ] Individual: {self.individual} \n [ 8 ] Main: {self.main}"

    @classmethod
    def edit(cls, data: dict[str, 'Entity']) -> None:
        keys = list(data.keys())
        while True:
            key = inputst('Type the desired entity ID [C to cancel]: ')
            if key.upper() == 'C':
                print('Operation cancelled.')
                break
            elif key not in keys:
                print('Invalid input: ID does not exist.')
            else:
                entity = data[key]
                while True:
                    print(entity)
                    try:
                        match inputst('Type the correspondent index of what do you desire to edit [C to cancel]: '):
                            case 'C':
                                print('Operation cancelled.')
                                break
                            case '1':
                                new_key = inputst('New ID: ')
                                if new_key in keys:
                                    print("Invalid input. This ID is already being used.")
                                else:
                                    entity_l = data[key].to_list()
                                    entity_l[0] = new_key
                                    data[new_key] = Entity(*entity_l)
                                    del data[key]
                                    keys.append(new_key)
                                    keys.remove(key)
                                    print("ID changed with success.")
                                    break
                            case '2':
                                data[key].names[0] = inputst('New legal name: ')
                            case '3':
                                if data[key].individual is True:
                                    print("Error: Entities with 'individual' True cannot receive a trade name.")
                                else:
                                    data[key].names[1] = inputst('New trade name: ')
                            case '4':
                                l = inputst("New 'country, state, city': ")
                                l = [p.strip() for p in l.split(',')]
                                if len(l) != 3:
                                    print("Invalid input, insufficient data.")
                                else:
                                    data[key].location = l
                            case '5':
                                data[key].born_dt = datetime.fromisoformat(inputst('New born date [YYYY-MM-DD]: '))
                            case '6':
                                death = inputst("New death date [YYYY-MM-DD or N to None]: ")
                                if death.upper() == 'N':
                                    death = None
                                data[key].death_dt = datetime.fromisoformat(death) if death else None
                            case '7':
                                data[key].individual = not data[key].individual
                            case '8':
                                if data[key].main is True:
                                    data[key].main = False
                                else:
                                    has_main = False
                                    for k,v in data.items():
                                        if v.main is True:
                                            has_main = True
                                            break
                                    if has_main is True:
                                        print("That already is a main entity recorded. That cannot be two main entities.")
                                    else:
                                        v.main = True
                            case _:
                                print('Unknown option.')
                    except Exception as e:
                        print(f"Error editing the entity: {e}")

    @classmethod
    def new(cls, main: bool, data: dict[str, 'Entity']) -> None:
        text = 'Insert data about the main entity that will be recorded on the system.' if main is True else 'Insert data about the new entity that will be recorded on the system.'
        print(text)
        used_keys = list(data.keys())
        while True:
            key = inputst("ID ['document number'$'document type']:\n(Input C to cancel)\n")
            if key in used_keys:
                print("This ID is already being used. Please input another or cancel the operation.")
            elif key.upper() == 'C':
                print('Operation cancelled.')
                break
            elif len(key) <= 3:
                print("Insufficient data for an ID.")
            else:     
                try:
                    test = yes_no('Is it an individual entity?')
                    data[key] = Entity(
                        key,
                        [inputst('Legal name: '), '' if test else inputst('Trade name: ').strip()],
                        [inputst('Country: '), inputst('State: '), inputst('City: ')],
                        inputst('Born date [YYYY-MM-DD]: '),
                        '',
                        test,
                        main
                        )
                except Exception as e:
                    print(f"Error recording the entity: {e}")
                finally:
                    shell_block()
                break

class Account:

    def __init__(self, id_key: str, name: str, cash_index: str) -> None:
        self.id = id_key
        self.name = name
        self.cash_index = cash_index
        self.hierarchy = id_key.count(".") + 1
        self.analytic = True if name.upper() != name else False
        array = id_key.split('.')
        self.parent_ID = '' if self.hierarchy == 1 else ".".join(array[:(len(array)-1)])
        
        if len(self.id) > 11:
            raise ValueError(f"{self.id} invalid as ID code, lenght higher than 11.")
        if len(self.name) > 37:
            raise ValueError(f"{self.name} invalid as account name, lenght higher than 37.")
        if self.cash_index not in ['', 'op', 'fi', 'in']:
            raise ValueError(f"{self.cash_index} invalid as index for the cash flow statment. It can has to be in ['', 'op', 'fi', 'in'].")

    def __str__(self) -> str:
        return f" [ 1 ] ID: {self.id} \n [ 2 ] Name: {self.name} \n [ 3 ] Cash index for the cash flow statement: {self.cash_index} \n"

    def to_list(self):
        return [
            self.id,
            self.name,
            self.cash_index,
            ]

    @classmethod
    def edit(cls, data: dict[str, 'Account']) -> None:
        used_keys = list(data.keys())
        while True:
            key = inputst("ID of the account that you desire to edit [C to cancel]: ")
            if key.upper() == "C":
                print('Operation cancelled.')
                break
            elif key not in used_keys:
                print("Invalid input. That isn't any account with that ID.")
            else:
                account = data[key]
                while True:
                    print(account)
                    try:
                        match inputst("Type the corresponding index of what do you desire to edit [C to cancel]: ").upper():
                            case 'C':
                                print('Operation cancelled.')
                                break
                            case '1':
                                print("!!!ALERT!!!\nChanging a account ID can seriously break the overall ballance calcullations and report generation.\nIf this account or its sons already were used in a entry, please, do not change the ID.\nIf you still want to edit the ID, change the entries were it was used.")
                                if inputst("Do you desire to continue? [Type CONFIRM to continue]\n").upper() != "CONFIRM":
                                    print("Operation cancelled.")
                                    break
                                else:
                                    new = inputst("Type the new ID: ")
                                    array = new.split('.')
                                    if new in used_keys:
                                        print("Invalid input. That ID is already begin used.")
                                    elif new.count(".") + 1 > 1 and ".".join(array[:(len(array)-1)]) not in used_keys:
                                        print("Invalid input. That ID doesn't have a valid parent.")
                                    else:
                                        accountl = account.to_list()
                                        accountl[0] = new
                                        data[new] = Account(*accountl)
                                        del data[key]
                                        used_keys.append(new)
                                        used_keys.remove(key)
                            case '2':
                                print('Remember that synthetic accounts are written in caps only.\nChanging the type of an account that already was used in a entry will break the system.')
                                new = inputst('New name: ')
                                if len(new) > 37:
                                    raise ValueError('Name lenght higher than 37.')
                                else:
                                    account.name = new
                            case '3':
                                new = inputst("New cash index for the cash flow statement ['', 'op', 'fi', 'in']: ")
                                if new in ['', 'op', 'fi', 'in']:
                                    account.cash_index = new
                                else:
                                    print("Invalid input. It should be in ['', 'op', 'fi', 'in']")
                            case _:
                                print("Invalid input.")
                    except Exception as e:
                        print(f"Error recording the entity: {e}")
                    finally:
                        shell_block()

    @classmethod
    def new(cls, data: dict[str, 'Account']) -> None:
        used_keys = list(data.keys())
        print("Insert data about the account that you desire to record.")
        while True:
            key = inputst('ID [C to cancel]: ')
            array = key.split('.')
            if key.upper() == "C":
                print('Operaton cancellerd.')
                break
            elif key in used_keys:
                print("Invalid input. This ID is already begin used.")
            elif isinstance(array, list) and len(array) > 1 and ".".join(array[:-1]) not in used_keys:
                print("Invalid input. This ID hasn't a valid parent recorded.")
            else:
                try:
                    data[key] = Account(
                        key,
                        inputst('Name: '),
                        inputst("Cash index for the cash flow statment ['', 'op', 'fi', 'in']")
                        )
                    print('Account recorded with success.')
                    break
                except Exception as e:
                    print(f"Error recording the entity: {e}")
                finally:
                    shell_block()
                

class CostCenter:
    
    def __init__(self, id_key: str, name: str, open_dt: str, close_dt: str) -> None:
        self.id = id_key
        self.name = name
        self.open_dt = datetime.fromisoformat(open_dt)
        self.close_dt = None if close_dt == '' else datetime.fromisoformat(close_dt)

    def __str__(self) -> str:
        close = self.close_dt.isoformat() if self.close_dt else '' 
        return f" [ 1 ] ID: {self.id} \n [ 2 ] Name: {self.name} \n [ 3 ] Open date: {self.open_dt.isoformat()} \n [ 4 ] Close date: {close}"

    def to_list(self):
        return [
            self.id,
            self.name,
            self.open_dt.isoformat(),
            self.close_dt.isoformat() if self.close_dt else ''
            ]
    
    @classmethod
    def edit(cls, data: dict[str, 'CostCenter']) -> None:
        while True:
            used_keys = list(data.keys())
            key = inputst("ID of the cost center that you desire to edit [C to cancel]: ")
            if key.upper() == 'C':
                cancel()
                break
            elif key not in used_keys:
                print("Invalid input. That isn't a cost center with that ID.")
            else:
                selected = data[key]
                while True:
                    print(selected)
                    try:
                        match inputst('Type the corresponding index of what do you desire to edit [C to cancel]: '):
                            case 'C':
                                cancel()
                                break
                            case '1':
                                print("!!!ALLERT!!!\nChanging a cost center ID can seriously break the overall ballance calcullations and report generation.\nIf this cost center already was used in a entry, please, do not change the ID.\nIf you still want to edit the ID, change the entries were it was used.")
                                if inputst('Do you desire to continue? [Type CONFIRM if yes] ').upper() != 'CONFIRM':
                                    cancel()
                                    break
                                else:
                                    new = inputst('Type the new ID: ')
                                    if new in used_keys:
                                        print('Invalid input. This ID is already being used.')
                                    else:
                                        ccen = selected.to_list()
                                        ccen[0] = new
                                        data[new] = CostCenter(*ccen)
                                        del selected
                                        print("Cost center ID edited with success.")
                                        break
                            case '2':
                                selected.name = inputst('New cost centr name: ')
                            case '3':
                                selected.open_dt = datetime.fromisoformat(inputst('New open date [YYYY-MM-DD]: '))
                            case '4':
                                close = inputst('New close date ['' or YYYY-MM-DD]: ')
                                close = datetime.fromisoformat(close) if close else None
                                selected.close_dt = close
                            case _:
                                print("Inavalid input.")
                    except Exception as e:
                        print(f"Error: {e}")
                    finally:
                        shell_block()

    @classmethod
    def new(cls, data: dict[str, 'CostCenter']) -> None:
        used_keys = list(data.keys())
        print('Type data about the new cost center that you desire to record.')
        key = inputst('ID [C to cancel]: ')
        if key == 'C':
            cancel()
        elif key in used_keys:
            print('Invalid input. That ID is already beign used.')
        else:
            try:
                data[key] = CostCenter(
                    key,
                    inputst('Name: '),
                    datetime.fromisoformat(inputst('Open date [YYYY-MM-DD]: ')),
                    ''
                    )
                print("Cost center recorded with success.")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                shell_block()

class Entry:

    def __init__(self, id_key: str,  entity: str, date: str, history: str, document: str, dr: list[list[float, str, str]], cr: list[list[float, str, str]]) -> None:
        # Structure of a dr/cr argument:
            # It is a list of lists, all the items on the dr list are a dr entry while all the items on the cr list are a cr entry.
                # The first element of the list is the value of the entry, the second is the referent account id and the third is the cost center.
        self.id = id_key
        self.entity = entity
        self.date = datetime.fromisoformat(date)
        self.history = history
        self.document = document
        self.dr = dr
        self.cr = cr

        dr_sum = 0.0
        cr_sum = 0.0
        for item in dr:
            dr_sum += item[0]
            if item[2] != '' and not item[1].startswith('5'):
                raise ValueError(f"Entry {id_key} with non expense account ({item[1]}) associated with a cost center ({item[2]}).")
        for item in cr:
            cr_sum += item[0]
            if item[2] != '' and not item[1].startswith('5'):
                raise ValueError(f"Entry {id_key} with non expense account ({item[1]}) associated with a cost center ({item[2]}).")
        if round(dr_sum, 2) != round(cr_sum, 2):
            raise ValueError(f"Entry {id_key} with residual value: {dr_sum - cr_sum}")

    def __str__(self) -> str:
        header = f"\n    {'Value':<20} | {'Account':<19} | {'Cost center':<10}"
        text = f" [ 1 ] ID: {self.id} \n [ 2 ] Entity: {self.entity} \n [ 3 ] Date: {self.date.isoformat()} \n [ 4 ] History: {self.history} \n [ 5 ] Document: {self.document} \n [ 6 ] Debits:{header}"
        i = 0
        for item in self.dr:
            text = "\n".join([text,f"({i}) {item[0]:<20,.2f} | {item[1]:<19} | {item[2]:<10}"])
            i += 1
        text = '\n'.join([text, f" [ 7 ] Credits:{header}"])
        i = 0
        for item in self.cr:
            text = "\n".join([text, f"({i}) {item[0]:<20,.2f} | {item[1]:<19} | {item[2]:<10}"])
            i += 1
        text = '\n'.join([text, f"  Residual value: {self.residual():,.2f}"])
        return text

    def residual(self) -> float:
        dr_sum = 0.0
        cr_sum = 0.0
        for item in self.dr:
            dr_sum += item[0]
        for item in self.cr:
            cr_sum += item[0]
        return round(dr_sum - cr_sum, 2)
        
    def to_list(self):
        return [
            self.id,
            self.entity,
            self.date.isoformat(),
            self.history,
            self.document,
            self.dr,
            self.cr
            ]
    
    @classmethod
    def edit(cls, data: dict[str, 'Entry'], ent: dict[str, Entity], acc: dict[str, Account], ccen : dict[str, CostCenter], lock: str) -> None:
        keys = list(data.keys())
        entk = list(ent.keys())
        acck = list(acc.keys())
        acck = [k for k in acck if acc[k].analytic]
        ccenk = list(ccen.keys())
        while True:
            key = inputst('Type the ID of the entry that you desire to edit [C to cancel]: ')
            if key.upper() == 'C':
                cancel()
                break
            elif key not in keys:
                print("Invalid input. That isn't a entry with that ID.")
            elif isinstance(lock, str) and data[key].date <= datetime.fromisoformat(lock):
                print("The entries until {lock} are locked.")
            else:
                while True:
                    print(data[key])
                    try:
                        match inputst('Type the corresponding index of what you desire to edit [C to cancel]: ').upper():
                            case 'C':
                                cancel()
                                break
                            case '1':
                                print("A entry's ID isn't editable.")
                            case '2':
                                data[key].entity = inputopt('New entity ID: ', entk)
                            case '3':
                                data[key].date = datetime.fromisoformat(inputst('New date [YYYY-MM-DD]: '))
                            case '4':
                                data[key].history = inputst('New history: ')
                            case '5':
                                data[key].document = inputst('New document: ')
                            case '6':
                                i = -1
                                options = []
                                for item in data[key].dr:
                                    i+= 1
                                    options.append(str(i))
                                c = inputopt('Type the corresponding index of the dr. entry that you desire to edit [C to cancel]: ', ['C', *options], True)
                                if c == 'C':
                                    cancel()
                                else:
                                    sel = data[key].dr[int(c)]
                                    match inputopt('Type the corresponding index of what you desire to edit: \n [ 1 ] Value. \n [ 2 ] Account. \n [ 3 ] Cost center. \n [ R ] Return.', ['R', '1', '2', '3'], True):
                                        case 'R':
                                            cancel()
                                        case '1':
                                            sel[0] = float(inputst('New value: '))
                                        case '2':
                                            new = inputopt('New dr. account: ', acck)
                                            if sel[1] != '' and not new.startswith('5'):
                                                raise ValueError('The entry has a cost center, and a cost center cannot be assigned to non expense account.')
                                            sel[1] = new                                            
                                        case '3':
                                            new = inputopt('New dr. cost center: ', ccenk)
                                            if new != '' and not sel[1].startswith('5'):
                                                raise ValueError('A cost center cannot be assigned to non expense account.')
                                            sel[2] = new
                            case '7':
                                i = -1
                                options = []
                                for item in data[key].cr:
                                    i+= 1
                                    options.append(str(i))
                                c = inputopt('Type the corresponding index of the cr. entry that you desire to edit [C to cancel]: ', ['C', *options], True)
                                if c == 'C':
                                    cancel()
                                else:
                                    sel = data[key].cr[int(c)]
                                    match inputopt('Type the corresponding index of what you desire to edit [C to cancel]', ['C', '1', '2', '3'], True):
                                        case 'C':
                                            cancel()
                                        case '1':
                                            sel[0] = float(inputst('New value: '))
                                        case '2':
                                            new = inputopt('New cr. account: ', acck)
                                            if sel[1] != '' and not new.startswith('5'):
                                                raise ValueError('The entry has a cost center, and a cost center cannot be assigned to non expense account.')
                                            sel[1] = new                                            
                                        case '3':
                                            new = inputopt('New cr. cost center: ', ccenk)
                                            if new != '' and not sel[1].startswith('5'):
                                                raise ValueError('A cost center cannot be assigned to non expense account.')
                                            sel[2] = new
                    except Exception as e:
                        print(f"Error: {e}")
                    finally:
                        shell_block()

    @classmethod
    def new(cls, data: dict[str, 'Entry'],ent: dict[str, Entity], acc: dict[str, Account], ccen : dict[str, CostCenter], last: int, lock: str) -> None:
        entk = list(ent.keys())
        acck = list(acc.keys())
        acck = [k for k in acck if acc[k].analytic]
        ccenk = list(ccen.keys())
        key = last + 1
        print("Type data about the entry that you desire to record [C to cancel].")
        entity = inputopt('Referent entity: ', ['C', *entk])
        if entity.upper() == 'C':
            cancel()
        else:
            try:
                key = str(key)
                dt = inputdt('Date [YYYY-MM-DD]: ')
                if lock:
                    if datetime.fromisoformat(dt) <= datetime.fromisoformat(lock):
                        raise ValueError(f"The entries are locked until {lock}.")
                ht = inputst('History: ')
                dc = inputst('Document: ')
                dr = []
                cr = []
                residual = 0.0
                while True:
                    if yes_no('Add a debit entry? [Y/N] '):
                        val = inputfloat('Value [0.00]: ')
                        acc = inputopt('Account: ', acck)
                        ccen = '' if not acc.startswith('5') else inputopt('Cost center: ', ['', *ccenk])
                        dr.append([val, acc, ccen])
                        residual += val
                        print(f"Residual value: {residual:,.2f}")
                    else:
                        break
                while True:
                    if yes_no('Add a credit entry? [Y/N] '):
                        val = inputfloat('Value [0.00]: ')
                        acc = inputopt('Account: ', acck)
                        ccen = '' if not acc.startswith('5') else inputopt('Cost center: ', ['', *ccenk])
                        cr.append([val, acc, ccen])
                        residual -= val
                        print(f"Residual value: {residual:,.2f}")
                    elif round(residual, 2) == 0.00:
                        break
                    else:
                        print("You cannot record a entry with residual value.")
                entry = Entry(key, entity, dt, ht, dc, dr, cr)
                print(entry)
                if yes_no('Confrim entry? [Y/N]'):
                    data[key] = entry
            except Exception as e:
                print(f"Error: {e}")
            finally:
                shell_block()

    @classmethod
    def importf(cls, data: dict[str, 'Entry'], ent: dict[str, Entity], acc: dict[str, Account], ccen : dict[str, CostCenter], last: int, entries: str, lock: str, year: int) -> int:
        entries = [line.split('\t') for line in entries.split('\n') if line.strip()]
        entk = list(ent.keys())
        acck = list(acc.keys())
        acck = [k for k in acck if acc[k].analytic]
        ccenk = list(ccen.keys()) + ['']
        temp = {}
        try:
            for item in entries:
                last += 1
                key = str(last)
                if len(item) < 9:
                    item += [''] * (9 - len(item))
                ob = cls(key, item[0], item[1], item[2], item[3], [[float(item[4]), item[5], item[6]]], [[float(item[4]), item[7], item[8]]])
                errors = []
                if ob.entity not in entk:
                    errors.append(f"{ob.entity} is an invalid entity.")
                if lock:
                    if ob.date <= datetime.fromisoformat(lock):
                        errors.append(f"The entries are locked until {lock}")
                if ob.date.year != year:
                    errors.append(f"Entry with an year different than {year}.")
                if ob.dr[0][1] not in acck:
                    errors.append(f"{ob.dr[0][1]} is an invalid account.")
                if ob.cr[0][1] not in acck:
                    errors.append(f"{ob.cr[0][1]} is an invalid account.")
                if ob.dr[0][2] not in ccenk:
                    errors.append(f"{ob.dr[0][2]} is an invalid cost center.")
                if ob.cr[0][2] not in ccenk:
                    errors.append(f"{ob.cr[0][2]} is an invalid cost center.")
                if len(errors) > 0:
                    raise ValueError(f"Errors processing the following entry:\n{ob}\n{'\n'.join(errors)}\nRecording cancelled.")
                temp[key] = ob
        except Exception as e:
            print(f"Error: {e}")
            return last
        data.update(temp)
        print('Entries imported with success.')
        return last

def check(entity: str, acc: str, ccen: str, d: 'BalanceData') -> None:
    d.setdefault(entity, {}).setdefault(acc, {}).setdefault(ccen, [0.0, 0.0, 0.0])
            
class BalanceData:
    
    def __init__(self, data: dict[str, dict[str, dict[str, list[float]]]]) -> None:
        # format : {entity, {account, {costcenter: [open, debits, credits]}}}
        self.data = data

    def close_bal(self, entity: str, acc: str, ccen: str) -> float:
        select = self.data[entity][acc][ccen]
        return float(select[0] + select[1] - select[2])

    def consolidate_all(self, acc: str) -> list[float]:
        op = 0.0
        dr = 0.0
        cr = 0.0
        for entity_key, entity_obj in self.data.items():
            acc_obj = entity_obj[acc]
            for k,v in acc_obj.items():
                op += v[0]
                dr += v[1]
                cr += v[2]
        return [op, dr, cr, op + dr - cr]

    def consolidate_ccen(self, entity: str, acc: str) -> list[float]:
        op = 0.0
        dr = 0.0
        cr = 0.0
        select = self.data[entity][acc]
        for k,v in select.items():
            op += v[0]
            dr += v[1]
            cr += v[2]
        return [op, dr, cr, op + dr - cr]

    @classmethod
    def process(cls, open_dt: str, close_dt: str) -> 'BalanceData':

        def loadjson(path: str, obj: object) -> object:
            with open(path, "r", encoding="utf-8") as f:
                x = json.load(f)
            return {k: obj(*v) for k, v in x.items()}

        def loadbalfile(path: str) -> 'BalanceData':
            with open(path, 'r', encoding="utf-8") as f:
                x = json.load(f)
            return cls(x)

        bal = {}
        open_dt = datetime.fromisoformat(open_dt)
        close_dt = datetime.fromisoformat(close_dt)
        path = os.path.join("balances", f"{open_dt.year-1}.json")
        if os.path.exists(path):
            pre_bal = loadbalfile(path)
            for entity_key, entity_obj in pre_bal.data.items():
                for account_key, account_obj in entity_obj.items():
                    if account_key.startswith(('1', '2', '3')):
                        for k,v in account_obj.items():
                            check(entity_key, account_key, k, bal)
                            bal[entity_key][account_key][k][0] += pre_bal.close_bal(entity_key, account_key, k)
        p = close_dt.year - open_dt.year
        entries = {}
        for i in range(p + 1):
            path = os.path.join("entries", f"{close_dt.year - i}.json")
            if os.path.exists(path):
                entries.update(loadjson(path, Entry))
        for k,v in entries.items():
            entity_key = v.entity
            if v.date < open_dt:
                for item in v.dr:
                    acc_key = item[1]
                    if acc_key.startswith(('1', '2', '3')):
                        ccen_key = item[2]
                        check(entity_key, acc_key, ccen_key, bal)
                        bal[entity_key][acc_key][ccen_key][0] += item[0]
                for item in v.cr:
                    acc_key = item[1]
                    if acc_key.startswith(('1', '2', '3')):
                        ccen_key = item[2]
                        check(entity_key, acc_key, ccen_key, bal)
                        bal[entity_key][acc_key][ccen_key][0] -= item[0]
            if v.date >= open_dt and v.date <= close_dt:
                for item in v.dr:
                    acc_key = item[1]
                    ccen_key = item[2]
                    check(entity_key, acc_key, ccen_key, bal)
                    bal[entity_key][acc_key][ccen_key][1] += item[0]
                for item in v.cr:
                    acc_key = item[1]
                    ccen_key = item[2]
                    check(entity_key, acc_key, ccen_key, bal)
                    bal[entity_key][acc_key][ccen_key][2] += item[0]
        return cls(bal)

    def propagate(self, accs: dict[str, Account]) -> 'BalanceData':
        bal = self.data
        roots = []
        for k, v in accs.items():
            parent = v.parent_ID
            if parent == '':
                roots.append(k)
            if parent in accs:
                parent = accs[parent]
                children = getattr(parent, 'children', [])
                children.append(k)
                parent.children = children
                
        def x(acc: str, entity: str) -> None:
            acc_obj = accs[acc]
            if hasattr(acc_obj, 'children'):
                for item in acc_obj.children:
                    x(item, entity)
            parent_key = acc_obj.parent_ID
            if parent_key != '':
                check(entity, acc, '', bal)
                for ccen in bal[entity][acc].keys():
                    check(entity, parent_key, ccen, bal)
                    son_bal = bal[entity][acc][ccen]
                    parent_bal = bal[entity][parent_key][ccen]
                    parent_bal[0] += son_bal[0]
                    parent_bal[1] += son_bal[1]
                    parent_bal[2] += son_bal[2]
            elif acc == '6':
                check(entity, acc, '', bal)

        for key in bal:
            for item in roots:
                x(item, key)        
        return self
            
