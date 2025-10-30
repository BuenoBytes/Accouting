import root

ls = 141

def trial_balance(entities: dict[str, root.Entity], accounts: dict[str, root.Account]) -> str:
    doc = []
    open_dt = root.inputdt('Open date [ISO]: ')
    close_dt = root.inputdt('Close date [ISO]: ')
    doc += ['='*ls, f"From {open_dt} to {close_dt}".center(ls), '='*ls, f"{'ENTITY NAME':<71}{'ENTITY ID':>70}"]
    data = root.BalanceData.process(open_dt, close_dt)
    data = data.propagate(accounts)
    if root.yes_no('Do you desire a report of of a specific entity [Y] or a consolidated report of all entities [N]?'):
        entity = root.inputopt("Type the desired entity' ID: ", list(entities.keys()))
        select = entities[entity]
        doc += [f"{select.names[0]:<71}{select.id[1] + ' - ' + select.id[2]:>70}"]
        assets = data.consolidate_ccen(entity, '1')[3] + data.consolidate_ccen(entity, '2')[3] + data.consolidate_ccen(entity, '3')[3]
        results = data.consolidate_ccen(entity, '4')[3] + data.consolidate_ccen(entity, '5')[3] + data.consolidate_ccen(entity, '6')[3]
        oprev = -data.consolidate_ccen(entity, '4.1')[3]
        opexp = -data.consolidate_ccen(entity, '5.1')[3]
        depr = -data.consolidate_ccen(entity, '5.1.7')[3]
        re = -data.consolidate_ccen(entity, '4')[3]
        ex = -data.consolidate_ccen(entity, '5')[3]
        ass = data.consolidate_ccen(entity, '1')[3]
        debit = -data.consolidate_ccen(entity, '2.1')[3] / data.consolidate_ccen(entity, '1.1')[3]
        cash = data.consolidate_ccen(entity, '1.1.1')
    else:
        entity = None
        for k,v in entities.items():
            doc += [f"{v.names[0]:<71}{v.id[1] + ' - ' + v.id[2]:>70}"]
        assets = data.consolidate_all('1')[3] + data.consolidate_all('2')[3] + data.consolidate_all('3')[3]
        results = data.consolidate_all('4')[3] + data.consolidate_all('5')[3] + data.consolidate_all('6')[3]
        oprev = -data.consolidate_all('4.1')[3]
        opexp = -data.consolidate_all('5.1')[3]
        depr = -data.consolidate_all('5.1.7')[3]
        re = -data.consolidate_all('4')[3]
        ex = -data.consolidate_all('5')[3]
        ass = data.consolidate_all('1')[3]
        debit = -data.consolidate_all('2.1')[3] / data.consolidate_all('1.1')[3]
        cash = data.consolidate_all('1.1.1')
    inconsistency = assets + results
    text = 'C O N S O L I D A T E D   T R I A L   B A L A N C E' if entity is None and len(list(entities.keys())) > 1 else 'T R I A L   B A L A N C E'
    doc += ['_'*ls, '', text.center(ls), '_'*ls, '', f"{'ACCOUNT ID':<19}{'ACCOUNT NAME':<38}{'OPEN BALANCE':>20}{'DEBITS':>18}{'CREDITS':>18}{'CLOSE BALANCE':>20}", '']
    warnings = ['-'*ls, '!!! W A R N I N G S !!!'.center(ls)]
    for acc_key, acc_obj in accounts.items():
        b = data.consolidate_all(acc_key) if entity is None else data.consolidate_ccen(entity, acc_key)
        if b[0]!= 0 or b[1]!=0 or b[2]!= 0:
            test = b[0] if str(acc_key).startswith(('1', '2', '3')) else None
            if test:
                test = f"{test:>20,.2f}"
            else:
                test = f"{'':>20}"
            doc += [f"{'  ' * (acc_obj.hierarchy-1)}{acc_key:<19}{acc_obj.name:<38}{test}{b[1]:>18,.2f}{b[2]:>18,.2f}{b[3]:>20,.2f}"]
            if str(acc_key).startswith('1') and b[3] < 0 and not (str(acc_key).startswith('1.2.6.02') or str(acc_key).startswith('1.2.7.02')):
                warnings += [f"ASSETS account [{acc_key} - {acc_obj.name}] with a credit closing balance."]
            elif str(acc_key).startswith('2') and b[3] > 0:
                warnings += [f"LIABILITIES account [{acc_key} - {acc_obj.name}] with a debit closing balance."]
            elif str(acc_key).startswith('4') and b[3] > 0 and not acc_obj.name.startswith('Less:'):
                warnings += [f"REVENUE account [{acc_key} - {acc_obj.name}] with a debit closing balance."]
            elif str(acc_key).startswith('5') and b[3] < 0:
                warnings += [f"EXPENSES account [{acc_key} - {acc_obj.name}] with a credit closing balance."]
    doc += ['-'*ls, f"Assets difference: {assets:,.2f}", f"Results difference: {results:,.2f}", f"Inconsistency: {inconsistency:,.2f}"]
    fi = re + ex
    test = 'Loss' if fi < 0 else 'Profit'
    doc += ['-'*ls,
            'K E Y   P E R F O R M A N C E   I N D I C A T O R'.center(ls),
            f"{test:<12}: {fi:,.2f} | {(fi/re)*100:.2f}",
            f"{'EBIT':<12}: {oprev+opexp:,.2f} | {((oprev+opexp)/oprev)*100:.2f}",
            f"{'EBITDA':<12}: {oprev+opexp+depr:,.2f} | {((oprev+opexp+depr)/oprev)*100:.2f}",
            f"{'ROI (%)':<12}: {(fi/(-ex))*100:.2f}",
            f"{'ROA (%)':<12}: {(fi/ass)*100:.2f}",
            f"{'Debit ratio':<12}: {debit*100:.2f}",
            f"{'Cash flow':<12}: {cash[3]-cash[0]:,.2f} | {((cash[3]-cash[0])/cash[0])*100:.2f}"
            ]
    if len(warnings) > 2:
        doc += warnings
    doc += ['='*ls, f"E N D   O F   T H E   R E P O R T".center(ls), '='*ls]
    return '\n'.join(doc)
