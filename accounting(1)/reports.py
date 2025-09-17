from datetime import datetime
import tools
import classes

# OBS: Lenghts for documents in portrait/landscape = 95/141

# BALANCE MATH
def generate_balances(data: classes.File_structure, open_date: str, close_date: str, rep_type: bool, entity: str) -> None:
            # rep_type = True -> Consolidated
            # rep_type = False -> Of an specific entity
    open_date_obj = datetime.strptime(open_date, tools.iso_date)
    close_date_obj = datetime.strptime(close_date, tools.iso_date)

    valid_ccens_keys: list[str] = []
    for key in data["cost_centers"]:
        selected_ccen = data["cost_centers"][key]
        if selected_ccen.open_date <= open_date_obj and (selected_ccen.close_date is None or selected_ccen.close_date>= open_date_obj):
            valid_ccens_keys.append(key)
            
    # CLEANING PRE-RUN
    for key in data["accounts"]:
        selected_account = data["accounts"][key]
        selected_account.sons_IDs = []
        for k in selected_account.balances:
            selected_account.balances[k] = {
                    "open": 0.0,
                    "debits": 0.0,
                    "credits": 0.0,
                    "close": 0.0
                }
    
    for key in data["accounts"]:
        selected_account = data["accounts"][key]
        if selected_account.parent_ID() != "":
            data["accounts"][selected_account.parent_ID()].sons_IDs.append(key)
        if len(valid_ccens_keys) > 0 and selected_account.id[0] == "5":
            for ccen in valid_ccens_keys:
                selected_account.balances[ccen] = {
                    "open": 0.0,
                    "debits": 0.0,
                    "credits": 0.0,
                    "close": 0.0
                }
                
    # NOTE: The open balance for result accounts isnt calculated to make view easier.
    keys = list(data["entries"].keys()) if rep_type is True else [k for k,v in data["entries"].items() if v.entity == entity]
    for key in keys:
        selected_entry = data["entries"][key]
        if selected_entry.date < open_date_obj:
            if selected_entry.dr_acc[0] in ["1", "2", "3"]:
                data["accounts"][selected_entry.dr_acc].balances["main"]["open"] += selected_entry.value
            if selected_entry.cr_acc[0] in ["1", "2", "3"]:
                data["accounts"][selected_entry.cr_acc].balances["main"]["open"] -= selected_entry.value
        elif selected_entry.date <= close_date_obj:
            data["accounts"][selected_entry.dr_acc].balances["main"]["debits"] += selected_entry.value
            data["accounts"][selected_entry.cr_acc].balances["main"]["credits"] += selected_entry.value
            if selected_entry.dr_ccen != "":
                data["accounts"][selected_entry.dr_acc].balances[selected_entry.dr_ccen]["debits"] += selected_entry.value
            if selected_entry.cr_ccen != "":
                data["accounts"][selected_entry.cr_acc].balances[selected_entry.cr_ccen]["credits"] += selected_entry.value
    
    def propagate_balances(account_key: str) -> None:
        selected_account = data["accounts"][account_key]
        if len(selected_account.sons_IDs) > 0:
            for key in selected_account.sons_IDs:
                propagate_balances(key)
        if selected_account.parent_ID() in data["accounts"]:
            for key in selected_account.balances:
                data["accounts"][selected_account.parent_ID()].balances[key]["open"] += data["accounts"][selected_account.id].balances[key]["open"]
                data["accounts"][selected_account.parent_ID()].balances[key]["debits"] += data["accounts"][selected_account.id].balances[key]["debits"]
                data["accounts"][selected_account.parent_ID()].balances[key]["credits"] += data["accounts"][selected_account.id].balances[key]["credits"]
    roots = [1,2,3,4,5,6]
    for item in roots:
        propagate_balances(str(item))
    
    for key in data["accounts"]:
        for k in data["accounts"][key].balances:
            selected = data["accounts"][key].balances[k]
            selected["close"] = selected["open"] + selected["debits"] - selected["credits"]

def trial_balance(data: classes.File_structure, open_date: str, close_date: str) -> None:
    rep_type = tools.input_with_options("Do you desire what type of report? [C - Consolidated, S - Specific]", ["C", "S"], True)
    rep_type = True if rep_type == "C" else False
    entity = "" if rep_type is True else tools.input_with_options("Type the desired entity for the report [doc_code%doc_type]: ", list(data["entities"].keys()))
    generate_balances(data, open_date, close_date, rep_type, entity)
    txt: list[str]= []
    line = "=" * 141
    line2 = "-" * 141
    line3 = "_" * 141

    row = f"From {open_date} to {close_date}".center(141)
    txt.append("\n".join([line, row, line]))

    row = f"{'ENTITY NAME':<71}{'ENTITY ID':>70}"
    txt.append(row)
    
    if rep_type is True:
        for key in data["entities"]:
            row = f"{data['entities'][key].name[0]:<71}{data['entities'][key].id[0] + " - " + data['entities'][key].id[1]:>70}"
            txt.append(row)
        row = "C O N S O L I D A T E D   T R I A L   B A L A N C E".center(141)
        txt.append("\n".join([line3, "", row, line3, ""]))
    else:
        array = entity.split("%")
        row = f"{data['entities'][entity].name[0]:<71}{array[0] + '-' + array[1]:>70}"
        txt.append(row)
        row = "T R I A L   B A L A N C E".center(141)
        txt.append("\n".join([line3, "", row, line3, ""]))
        
    row = f"{'ACCOUNT ID':<19}{'ACCOUNT NAME':<38}{'OPEN BALANCE':>20}{'DEBITS':>18}{'CREDITS':>18}{'CLOSE BALANCE':>20}"
    txt.append(row)
    warnings = ["!!! W A R N I N G S !!!".center(141)]
    for key in data["accounts"]:
        selected = data["accounts"][key]
        if selected.balances["main"]["debits"] != 0 or selected.balances["main"]["credits"] != 0 or selected.balances["main"]["close"] != 0:
            if selected.id.startswith('4') or selected.id.startswith('5') or selected.id.startswith('6'):
                row = f"{(selected.hierarchy-1)*"  "}{selected.id:<19}{selected.name:<38}{' ':>20}{selected.balances['main']['debits']:>18,.2f}{selected.balances['main']['credits']:>18,.2f}{selected.balances['main']['close']:>20,.2f}"
            else:
                row = f"{(selected.hierarchy-1)*"  "}{selected.id:<19}{selected.name:<38}{selected.balances['main']['open']:>20,.2f}{selected.balances['main']['debits']:>18,.2f}{selected.balances['main']['credits']:>18,.2f}{selected.balances['main']['close']:>20,.2f}"
            txt.append(row)
            if selected.id[0] == "1" and selected.balances["main"]["close"] < 0:
                warnings.append(f"Assets account {selected.id} - {selected.name} with close balance at credit.")
            elif selected.id[0] == "2" and selected.balances["main"]["close"] > 0:
                warnings.append(f"Liabilities account {selected.id} - {selected.name} with close balance at debit.")
            elif selected.id[0] == "4" and selected.balances["main"]["close"] > 0 and selected.name[0:3] != "Less":
                warnings.append(f"Revenue account {selected.id} - {selected.name} with close balance at debit.")
            elif selected.id[0] == "4" and selected.balances["main"]["close"] < 0 and selected.name[0:3] == "Less":
                warnings.append(f"Revenue reducing account {selected.id} - {selected.name} with close balance at credit.")
            elif selected.id[0] == "5" and selected.balances["main"]["close"] < 0:
                warnings.append(f"Expenses account {selected.id} - {selected.name} with close balance at credit.")
    
    assets_dif = data["accounts"]["1"].balances["main"]["close"] + data["accounts"]["2"].balances["main"]["close"] + data["accounts"]["3"].balances["main"]["close"]
    results = data["accounts"]["4"].balances["main"]["close"] + data["accounts"]["5"].balances["main"]["close"] + data["accounts"]["6"].balances["main"]["close"]
    inconsistency = assets_dif + results
    txt.append("\n".join([line2, f"{'Assets difference: '}{assets_dif:,.2f}", f"{'Result difference: '}{results:,.2f}", f"{'Inconsistency: '}{inconsistency:,.2f}"]))
    if len(warnings) > 1:
        warnings.append(line2)
        txt.append("\n".join(warnings))

    # KPI
    closing = data["accounts"]["6"].balances["main"]["close"]
    revenue = data["accounts"]["4"].balances["main"]["close"]
    expenses = data["accounts"]["5"].balances["main"]["close"]
    if closing < 0:
        row = f"{'Profit':<10}: {closing} | {(-closing/revenue)*100:.2f}%"
    elif closing > 0:
        row = f"{'Profit':<10}: {-closing} | {(closing/(-revenue))*100:.2f}%"
    else:
        row = "{'Profit':<10}: Null"
    array = [
        line2,
        "K E Y   P E R F O R M A N C E   I N D I C A T O R S".center(141),
        row,
        f"{'EBIT':<10}: {-data['accounts']['4.1'].balances['main']['close'] - data['accounts']['5.1'].balances['main']['close']:,.2f} | {(-data['accounts']['4.1'].balances['main']['close'] - data['accounts']['5.1'].balances['main']['close'])/(-data['accounts']['4.1'].balances['main']['close'])*100:,.2f}%",
        f"{'EBITDA':<10}: {-data['accounts']['4.1'].balances['main']['close'] - data['accounts']['5.1'].balances['main']['close'] + data['accounts']['5.1.7'].balances['main']['close']:,.2f} | {(-data['accounts']['4.1'].balances['main']['close'] - data['accounts']['5.1'].balances['main']['close'] + data['accounts']['5.1.7'].balances['main']['close'])/(-data['accounts']['4.1'].balances['main']['close'])*100:,.2f}%",
        f"{'ROI(%)':<10}: {((-revenue)-expenses)/expenses*100:,.2f}%",
        f"{'ROA(%)':<10}: {closing/data['accounts']['1'].balances['main']['close']*100:,.2f}%",
        f"{'Debt ratio':<10}: {(-data['accounts']['2.1'].balances['main']['close'] / data['accounts']['1.1'].balances['main']['close'])*100:,.2f}%",
        f"{'Cash flow':<10}: {data['accounts']['1.1.1'].balances['main']['close'] - data['accounts']['1.1.1'].balances['main']['open']:,.2f} | {(data['accounts']['1.1.1'].balances['main']['close'] - data['accounts']['1.1.1'].balances['main']['open'])/data['accounts']['1.1.1'].balances['main']['open']:,.2f}%"
        ]
    txt.append("\n".join(array))
        
    # END OF THE REPORT
    txt.append("\n".join([line, "End of the report".center(141), line]))

    with open('input_output/output.txt', "w", encoding="utf-8") as file:
        file.write("\n".join(txt))

# FORMAL REPORTS

def format_values(value: str) -> str:
    if value < 0:
        return f"{-value:,.2f}"
    else:
        return f"{value:,.2f}"

def type_of_report(entities) -> tuple[bool, str]:
        # Returns a tuple (bool, str), with the first value begin True if it is an Consolidated report, and the str an empty if bool=True else the referent entity ID.
    rep_type = tools.input_with_options("Do you desire what type of report? [C - Consolidated, S - Specific]", ["C", "S"], True)
    rep_type = True if rep_type == "C" else False
    entity = "" if rep_type is True else tools.input_with_options("Type the desired entity for the report [doc_code%doc_type]: ", entities)
    return rep_type, entity

def balance_sheet(data: classes.File_structure, open_date: str, close_date: str) -> None:
    test = type_of_report(list(data["entities"].keys()))
    generate_balances(data, open_date, close_date, test[0], test[1])
    level = int(tools.input_with_options("Type the most detailed level that you desire to show on the report [3 to 5]: ", ["3", "4", "5"]))
    line = "=" * 95
    line_ = "_" * 95
    txt = [
        line,
        f"From {open_date} to {close_date}".center(95),
        line,
        f"{'ENTITY NAME':<48}{'ENTITY ID':>47}"
        ]
    if test[0] is True:
        for key in data["entities"]:
            row = f"{data['entities'][key].name[0]:<48}{data['entities'][key].id[0] + " - " + data['entities'][key].id[1]:>47}"
            txt.append(row)
        row = "C O N S O L I D A T E D   B A L A N C E   S H E E T".center(95)
    else:
        row = f"{data['entities'][test[1]].name[0]:<48}{array[0] + '-' + array[1]:>47}"
        txt.append(row)
        row = "B A L A N C E   S H E E T".center(95)
    txt.append("\n".join([line_, "", row, line_, ""]))

    # REPORT BODY

    def body_function(root: str)->None:
        selected = data["accounts"][root]
        space = f"{(selected.hierarchy)*"  "}" if selected.id[0] in ["2", "3"] else f"{(selected.hierarchy-1)*"  "}"
        if selected.id == "1":
            array = ["", f"{selected.name}".ljust(95, ".")]
            txt.append("\n".join(array))
            for key in selected.sons_IDs:
                body_function(key)
            txt.append(f"{'=Total of ASSETS: ':<38}{'=' + format_values(selected.balances['main']['close']):>20}{'=' + format_values(selected.balances['main']['open']):>20}")
        elif selected.id == "2":
            array = ["", "LIABILITIES AND EQUITY".ljust(95, "."), "  LIABILITIES"]
            txt.append("\n".join(array))
            for key in selected.sons_IDs:
                body_function(key)
            txt.append(f"{'  =Total of LIABILITIES: ':<38}{'=' + format_values(selected.balances['main']['close']):>20}{'=' + format_values(selected.balances['main']['open']):>20}")
        elif selected.id in ["1.1", "1.2", "2.1", "2.2", "3"]:
            txt.append(f"{space}{selected.name}")
            for key in selected.sons_IDs:
                body_function(key)
            txt.append(f"{space}{'=Total of ' + selected.name + ': ':<38}{'=' + format_values(selected.balances['main']['close']):>20}{'=' + format_values(selected.balances['main']['open']):>20}")
        elif (selected.balances['main']['open'] != 0 or selected.balances['main']['close'] != 0) and selected.hierarchy <= level:
            txt.append(f"{space}{selected.name:<38}{format_values(selected.balances['main']['close']):>20}{format_values(selected.balances['main']['open']):>20}")      
            for key in selected.sons_IDs:
                body_function(key)
                
    txt.append(f"{' ':<38}{'CURRENT BALANCE':>20}{'PRIOR BALANCE':>20}")
    for item in ["1", "2", "3"]:
        body_function(item)
    value_c = -(data['accounts']['2'].balances['main']['close'] + data['accounts']['3'].balances['main']['close'])
    value_o = -(data['accounts']['2'].balances['main']['open'] + data['accounts']['3'].balances['main']['open'])
    key = data['zero'].name.split('.')[0]
    entity = data['entities'][key]
    array = [
        f"{'=Total of LIABILITIES AND EQUITY: ':<38}{'='+format_values(value_c):>20}{'='+format_values(value_o):>20}",
        "",
        line.replace("=", "-"),
        f"{entity.city[0]}, {entity.state[0]}, {entity.country[0]}, {close_date}.",
        "",
        "",
        "",
        f"{'_'*35:^47}{'_'*35:^48}",
        f"{'Accountant':^47}{'Administrator':^48}",
        ]
    txt.append("\n".join(array))

    # ENDING
    
    array = [
        line,
        f"End of the report".center(95),
        line,
        ]
    txt.append("\n".join(array))
    with open('input_output/output.txt', "w", encoding="utf-8") as file:
        file.write("\n".join(txt))

def income_statement(data: classes.File_structure, open_date: str, close_date: str, by_function: bool) -> None:
    test = type_of_report(list(data["entities"].keys()))
    generate_balances(data, open_date, close_date, test[0], test[1])
    line = "=" * 95
    line_ = "_" * 95
    lineMinus = "." * 95
    txt = [
        line,
        f"From {open_date} to {close_date}".center(95),
        line,
        f"{'ENTITY NAME':<48}{'ENTITY ID':>47}"
        ]
    if test[0] is True:
        for key in data["entities"]:
            row = f"{data['entities'][key].name[0]:<48}{data['entities'][key].id[0] + " - " + data['entities'][key].id[1]:>47}"
            txt.append(row)
        row = "C O N S O L I D A T E D   P & L   S T A T E M E N T".center(95)
    else:
        row = f"{data['entities'][test[1]].name[0]:<48}{array[0] + '-' + array[1]:>47}"
        txt.append(row)
        row = "P & L   S T A T E M E N T".center(95)
    txt.append("\n".join([line_, "", row, line_, ""]))

    # BALANCES OF THE PREVIOUS PERIOD

    import copy
    pd = copy.deepcopy(data)
    op = tools.input_date_checker('Open date of the comparable period [ISO]: ')
    cl = tools.input_date_checker('Close date of the comparable period [ISO]: ')
    generate_balances(pd, op, cl, test[0], test[1])

    # REPORT BODY
    
    txt.append(f"{' ':<38}{close_date:>20}{cl:>20}")
    def body_function(root: str, bal_key: str)->None:
        selected = data["accounts"][root]
        p_sel = pd['accounts'][root]
        space = f"{(selected.hierarchy-2)*"  "}"
        if len(selected.id) <= 3:
            txt.append("")
            txt.append(f"{space}{selected.name}")
            for key in selected.sons_IDs:
                body_function(key, bal_key)
            txt.append(f"{space}{'=Total of ' + selected.name + ': ':<38}{'=' + format_values(selected.balances[bal_key]['close']):>20}{'=' + format_values(p_sel.balances[bal_key]['close']):>20}")
        elif (p_sel.balances[bal_key]['close'] != 0 or selected.balances[bal_key]['close'] != 0) and selected.hierarchy <= 3:
            txt.append(f"{space}{selected.name:<38}{format_values(selected.balances[bal_key]['close']):>20}{format_values(p_sel.balances[bal_key]['close']):>20}")      
            for key in selected.sons_IDs:
                body_function(key, bal_key)
                
    body_function("4.1", "main")
    if by_function is False:
        body_function("5.1", "main")
    else:
        valid_keys: list[str] = list(data["accounts"]["5"].balances.keys())
        valid_keys.remove("main")
        if len(valid_keys) == 0:
            print("That aren't active cost centers on that period, so its impossible to generate an by function P&L. Generating by nature instead.")
            body_function("5.1", "main")
        else:
            for item in valid_keys:
                txt.append(f" {data['cost_centers'][item].name}")
                for son in list(data['accounts']['5.1'].sons_IDs):
                    body_function(son, item)
                selected = data['accounts']['5.1']
                txt.append(f" {'Total of '+data['cost_centers'][item].name:<38}{format_values(selected.balances[item]['close']):>20}{format_values(pd.balances[item]['close']):>20}")
    array = [
        lineMinus,
        f"{'Earnings Before Interest and Taxes':<38}{-(data['accounts']['4.1'].balances['main']['close']+data['accounts']['5.1'].balances['main']['close']):>20,.2f}{-(pd['accounts']['4.1'].balances['main']['close']+pd['accounts']['5.1'].balances['main']['close']):>20,.2f}",
        lineMinus
        ]
    txt.append('\n'.join(array))
    body_function("4.2", "main")
    body_function("5.2", "main")
    array = [
        lineMinus,
        f"{'Net Profit or Loss':<38}{data['accounts']['6.1'].balances['main']['close']:>20,.2f}{pd['accounts']['6.1'].balances['main']['close']:>20,.2f}",
        lineMinus
        ]
    txt.append("\n".join(array))
        
    key = data['zero'].name.split('.')[0]
    entity = data['entities'][key]
    array = [
        "",
        f"{entity.city[0]}, {entity.state[0]}, {entity.country[0]}, {close_date}.",
        "",
        "",
        "",
        f"{'_'*35:^47}{'_'*35:^48}",
        f"{'Accountant':^47}{'Administrator':^48}",
        ]
    txt.append("\n".join(array))

    # ENDING
    
    array = [
        line,
        f"End of the report".center(95),
        line,
        ]
    txt.append("\n".join(array))
    with open('input_output/output.txt', "w", encoding="utf-8") as file:
        file.write("\n".join(txt))
