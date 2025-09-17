import tools
import base
import reports

print("Welcome to my prototype accounting system, an study project.")
while True:
    match tools.input_with_options("Choose an action:\n 1 - Search and select an entity file\n 2 - Create a new entity file\n C - Close program\n", ["1", "2", "C"], True):
        case "1":
            try:
                selected_file = base.search_data_bank(input("Type the ID of the main entity recorded on the desired file: "))
            except FileNotFoundError:
                print("****** File not found!")
            else:
                print("File found!")
                data = base.read_file(selected_file)
                while True:
                    match tools.input_with_options("Choose an action\n 1 - New entity\n 2 - Edit entity\n 3 - New account\n 4 - Edit account\n 5 - New cost center\n 6 - Edit cost center\n 7 - New entry\n 8 - Import entries\n 9 - Edit entry\n 10 - Trial balance\n 11 - Balance sheet\n 12 - Income statement\n S - Save changes\n B - Back\n", ["B", "S", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], True):
                        case "B":
                            break
                        case "S":
                            base.save_file_changes(data)
                        case "1":
                            base.new_entity(data)
                        case "2":
                            base.edit_entity(data)
                        case "3":
                            base.new_account(data)
                        case "4":
                            base.edit_account(data)
                        case "5":
                            base.new_cost_center(data)
                        case "6":
                            base.edit_cost_center(data)
                        case "7":
                            base.new_entry(data)
                        case "8":
                            base.import_entries(data)
                        case "9":
                            base.edit_entry(data)
                        case "10":
                            print("Provide data about the desired report.")
                            reports.trial_balance(data, tools.input_date_checker("Open date [ISO]: "), tools.input_date_checker("Close date [ISO]: "))
                            print("Report genereted with success in the input_output folder as output.txt.")
                            print("If you desire to save it as pdf, open the file with an web browser and select the landscape format or use an scale of 68%.")
                        case "11":
                            print("Provide data about the desired report.")
                            reports.balance_sheet(data, tools.input_date_checker("Open date [ISO]: "), tools.input_date_checker("Close date [ISO]: "))
                            print("Report genereted with success in the input_output folder as output.txt.")
                        case "12":
                            print("Provide data about the desired report.")
                            test = tools.input_with_options("Do you desire an report with 'by function' expenses? [Y/N]\n", ["Y", "N"], True)
                            test = True if test == "Y" else False
                            reports.income_statement(data, tools.input_date_checker("Open date [ISO]: "), tools.input_date_checker("Close date [ISO]: "), test)
                            print("Report genereted with success in the input_output folder as output.txt.")
                        case _:
                            print("Invalid input.")
        case "2":
            base.new_file()
        case "C":
            print("Bye!")
            break
        case _:
            print("Invalid input.")
