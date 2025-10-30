from datetime import datetime
import root
import json
import os

print('Welcome to my accounting and finnancing admnistration system INSTALLER. A study project.')
while True:
    print('Choose a action:')
    match root.inputopt(' [ 1 ] First run and inital system set up. \n [ C ] Close. \n', ['1', 'C'], True):
        case 'C':
            print('Bye!')
            break
        case '1':
            entities = {}
            accounts = {}
            cost_centers = {}
            criteria = {
                'lock': None,
                'last_entry': 0}
            root.Entity.new(True, entities)
            while True:
                if root.yes_no('Do you desire to record another entity? [Y/N]\n'):
                    root.Entity.new(False, entities)
                else:
                    break
            print('By standart, it is recorded on the system the standart chart of accounts (coa.txt). You can edit it latter on a normal run.')
            with open("coa.txt", "r", encoding="utf-8") as file:
                lines = file.read().split('\n')
                for row in lines:
                    acc = row.split('\t')
                    accounts[acc[0]] = root.Account(acc[0], acc[1], '')
            while True:
                if root.yes_no('Do you desire to add a new cost center? [Y/N]\n'):
                    root.CostCenter.new(cost_centers)
                else:
                    break
            entities = {k: entities[k].to_list() for k in entities.keys()}
            accounts = {k: accounts[k].to_list() for k in accounts.keys()}
            cost_centers = {k: cost_centers[k].to_list() for k in cost_centers.keys()}
            with open("_entities.json", "w", encoding="utf-8") as f:
                json.dump(entities, f, indent=4, ensure_ascii=False)
            with open("_accounts.json", "w", encoding="utf-8") as f:
                json.dump(accounts, f, indent=4, ensure_ascii=False)
            with open("_costcenters.json", "w", encoding="utf-8") as f:
                json.dump(cost_centers, f, indent=4, ensure_ascii=False)
            with open("_criteria.json", "w", encoding="utf-8") as f:
                json.dump(criteria, f, indent=4, ensure_ascii=False)
            os.makedirs('entries')
            os.makedirs('input_output')
            os.makedirs('balances')
            print('System installed with success.')

