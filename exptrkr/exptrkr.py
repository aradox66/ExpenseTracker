import pickle
from os.path import exists
import pandas as pd
import csv_input
import reports

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

class Table(object):

    def __init__(self, datafile, name, type_obj):
        mungeit = csv_input.Munger()
        mungeit.load(datafile)
        self.datatable = mungeit.data_clean
        self.type_dict = type_obj
        self.name = name
        self.unsaved = mungeit.cleaned
        self.typed = 0
        self.typed_cash = 0
        self.tot_cash = 0
        self.man_uns = 0

    def peek_data(self):
        if self.name == "None":
            print("Please load a datafile before attempting to add new data.")
            return
        q = int(input("How many?\n> "))
        print(self.datatable.head(q))

    def add_data(self):
        if self.name == "None":
            print("Please load a datafile before attempting to add new data.")
            return
        while True:
            new_data_filename = input("Input new data filename: ")
            if not exists(new_data_filename):
                print("File does not exist.")
            else:
                break
        new_datatable = pd.read_csv(new_data_filename, names=["date", "memo",
                                        "type", "amount"], header=None)
        self.datatable = self.datatable.merge(new_datatable, how="outer")
        self.unsaved = 1

    def save_data(self):
        if self.unsaved == 0:
            print("File already up to date.")
            return
        while True:
            sv_filename = input("Input data filename to save: ")
            if exists(sv_filename):
                print(f"{sv_filename} already exists. ", end="")
                yn = input(f"Overwrite? y/n\n> ")
                if yn == "y":
                    break
            else:
                break
        self.datatable.to_csv(sv_filename, index=False)
        print("Datafile saved.")
        self.unsaved =  0

    def report(self):
        perc_typ = int((self.typed / len(self.datatable)) * 100)
        print(f"{perc_typ}% of transactions successfully typed.")
        print(f"There are {len(self.datatable) - self.typed} untyped entries.")
        perc_sum = int(((self.tot_cash - self.typed_cash) / self.tot_cash) * 100)
        print(f"{perc_sum}% of total cash spent remains untyped.")
        return perc_sum

    def assign_types(self, reporter, overwriter):
#        if overwriter == 1 and self.man_uns == 1:
#            if input("Overwrite existing types? y/n: ") == "n":
#                overwriter = 0
#            else:
#                self.man_uns = 0
        print("Working...")

        types = list(self.type_dict.typedict.columns)
        for i in range(0, len(self.datatable)):
#            if all([pd.notnull(self.datatable.loc[i, "type"]),
#                    overwriter == 0]):
#                continue
            for j in types:
                if any(match in self.datatable.memo[i] for match in filter(
                        None, self.type_dict.typedict[j].fillna(value=""))):
                    self.datatable.iloc[i, 2] = j

        self.typed = len(self.datatable[self.datatable.type != ""])
        self.typed_cash = self.datatable[self.datatable.type!=""].amount.abs().sum()
        self.tot_cash = self.datatable.amount.abs().sum()

        if reporter == 1:
            self.report()

        self.datatable.type.replace("", "untyped", inplace=True)

        self.unsaved = 1

    def remove_type(self, type_name):
        j = len(self.datatable['type'][self.datatable['type'] == type_name])
        new_type = input("Input replacement type, or ENTER\n> ")
        self.datatable.loc[self.datatable.type == type_name, "type"] = new_type
        q = "s"
        if j == 1:
            q = ""
        print(f"Removed {type_name} from {j} transaction{q}.")
        self.unsaved = 1
        self.type_dict.unsaved = 1

    def fill_untyped(self):
        self.run = 1
        while self.run == 1:
            print(f"Types are: ", end="")
            self.type_dict.view_typelist()

            new_tuples = []
            i = 0
            q = len(self.datatable[self.datatable.type == "untyped"])

            while i < 5 and i < q:
                print(f"For transaction:")
                print(self.datatable[self.datatable.type == "untyped"].iloc[i])
                type_i_keys = []
                type_i = input("Input type: ")
                if type_i != "":
                    self.datatable.loc[i, 'type'] = type_i
                    z = 0
                    while True:
                        print(f"Input new keys for {type_i}, or ENTER:")
                        new = input("> ")
                        if new == "":
                            if z == 0:
                                self.man_uns = 1
                            break
                        else:
                            z = 1
                            self.unsaved = 1
                            type_i_keys.append(new)
                    type_tuple_i = (type_i, type_i_keys)
                    if len(type_tuple_i[1]) != 0:
                        new_tuples.append(type_tuple_i)
                i += 1

            if len(new_tuples) != 0:
                self.type_dict.update_dict(new_tuples)

            self.assign_types(0, 0)

            if self.report() < 10:
                print(f"Untyped transactions now total less than 10% of cash spent.")
                print(f"Continue typing? y/n:\n> ")
                a = input()
                if a == "n":
                    self.run = 0

# Biggest project: how to start a new typefile.
class BudgetTypes(object):

    def sort_dict(self):
        dp_sort = pd.concat([self.typedict[col]
                    .sort_values().reset_index(drop=True)
                    for col in self.typedict], axis=1, ignore_index=True)
        dp_sort.columns = self.typedict.columns
        self.typedict = dp_sort.reindex(sorted(dp_sort.columns), axis=1)

    def __init__(self, typefile_name, working_table, name):
        self.name = name
        self.typedict = pd.read_csv(typefile_name)
        self.table = working_table
        working_table.type_dict = self
        self.unsaved = 0
        self.sort_dict()

    def view_typelist(self):
        if self.name == "None":
            print("Load typefile first!")
            return
        print("Types are: " + ", ".join(self.typedict.columns) + ".")

    def combine_type(self):
        for i in range(0, len(self.typedict.columns)):
            print(f"{i}: {self.typedict.columns[i]}", end=", ")
        type1 = self.typedict.columns[int(input("\nInput first type index: "))]
        type2 = self.typedict.columns[int(input("Input second type index: "))]
        comb_type = input("New combined type name: ")
        new = (self.typedict[type1].append(self.typedict[type2]).
                dropna().sort_values().to_frame().reset_index(drop=True))
        new.columns=[comb_type]
        self.typedict.drop([type1, type2], axis=1, inplace=True)
        if len(self.typedict) > len(new):
            how_x = "left"
        else:
            how_x = "right"
        self.typedict = self.typedict.merge(new, left_index=True,
                            right_index=True, how=how_x)

    def remove_type(self):
        if self.name == "None":
            print("Load typefile first!")
            return
        for i in range(0, len(self.typedict.columns)):
            print(f"{i}: {self.typedict.columns[i]}", end=", ")
        rm_type = int(input("\nInput type index to remove: "))
        rm_type_name = self.typedict.columns[rm_type]
        self.typedict.drop(rm_type_name, axis=1, inplace=True)
        self.unsaved = 1
        if "y" in input("Remove type from transaction data? y/n: "):
            self.table.remove_type(rm_type_name)

    def add_new_type(self):
        new_type = input("New type name:\n> ")
        if new_type in self.typedict.columns:
            print("Type already exists.")
            return
        else:
            self.typedict[new_type] = None
        self.unsaved = 1

    def update_dict(self, new_tuples):
        for i in new_tuples:
            i_p = pd.Series(i[1], name=i[0])
            if i[0] in self.typedict.columns:
                i_p = self.typedict[i[0]].append(i_p).dropna().to_frame()
                i_p.reset_index(inplace=True, drop=True)
                self.typedict.drop(i[0], axis=1, inplace=True)
            if len(self.typedict) > len(i_p):
                how_x = "left"
            else:
                how_x = "right"
            self.typedict = self.typedict.merge(i_p, left_index=True,
                                right_index=True, how=how_x)
        self.sort_dict()
        self.unsaved = 1

    def key_edit(self):
        if self.name == "None":
            print("Load typefile first!")
            return
        print("Entering budget-type keyword editor.")
        def ke_menu():
            print("""You can:           0. View this menu
                    1. View typelist    2. View full dictionary
                    3. Edit dictionary entries  4. Exit editor
                """)
        ke_menu()

        def editor():
            self.view_typelist()
            which = input("Enter dict entry to edit: ")
            def ke_ar_menu():
                print(f"{which}: " + ", ".join(filter(None,
                        self.typedict[which].fillna(value=""))))
                print("1. Add keywords  2. Remove keywords  3. Return")

            while True:
                ke_ar_menu()
                effect = int(input("> "))
                if effect == 1:
                    new_keys = []
                    while True:
                        print(f"Input new keys for {which}, or ENTER:", end="")
                        new = input("> ")
                        if new == "":
                            break
                        else:
                            self.unsaved = 1
                            new_keys.append(new)
                    if len(new_keys) != 0:
                        new_tuple = (which, new_keys)
                        self.update_dict([new_tuple])
                    print("Keys added.")
                elif effect == 2:
                    a = 0
                    for k in self.typedict[which][
                                self.typedict[which].notnull()]:
                        if k != "":
                            print(f"{a}. {k}")
                            a += 1
                    rems = input("Input indexes separated by spaces:\n> ")
                    rems = list(map(int, rems.split(" ")))
                    if len(rems) > 0:
                        self.unsaved = 1
                    if len(rems) != 0:
                        print(f"Removing "
                            + ", ".join(self.typedict.loc[rems, which]),
                            end=".\n")
                    new_col = self.typedict[which].dropna().to_frame()
                    new_col.drop(rems, inplace=True)
                    new_col.reset_index(inplace=True, drop=True)
                    self.typedict.drop(which, axis=1, inplace=True)
                    if len(self.typedict) > len(new_col):
                        how_x = "left"
                    else:
                        how_x = "right"
                    self.typedict = self.typedict.merge(new_col,
                            left_index=True, right_index=True, how=how_x)
                    print(".")
                elif effect == 3:
                    ke_menu()
                    return
                else:
                    print("Try again.")

        while True:
            action = input("> ")
            if action == "4":
                start_program.show_menu()
                return
            elif action == "0":
                ke_menu()
            elif action == "1":
                self.view_typelist()
            elif action == "2":
                j = 0
                for i in self.typedict.columns:
                    print(f"{j}. " + i + ": "
                        + ", ".join(self.typedict[i][
                        self.typedict[i].notnull()]))
                    j += 1
            elif action == "3":
                editor()

    def save_typefile(self):
        if self.unsaved == 0:
            print("File already up to date.")
            return
        while True:
            sv_filename = input("Input data filename to save: ")
            if exists(sv_filename):
                print(f"{sv_filename} already exists. ", end="")
                yn = input(f"Overwrite? y/n\n> ")
                if yn == "y":
                    break
            else:
                break
        self.typedict.to_csv(sv_filename, index=False)
        print("Dictionary saved.")
        self.unsaved = 0

class Reports(object):

    def __init__(self, table):
        self.table = table
        self.reporter = reports.Reporter(self.table)
        self.unsaved = 0
        self.name = ""
        self.active = pd.DataFrame()

    def check_load(self):
        if self.table.name == "None":
            print("Load sorted transaction data first.")
            return 1
        else:
            return 0

    def gen_year_report(self):
        if self.check_load():
            return
        year = int(input("Input year:\n> "))
        self.reporter.year_sum(year)
        self.active = self.reporter.year_report
        print(self.active)
        self.name = str(year) + " summary."
        self.unsaved =1

    def gen_full_report(self):
        if self.check_load():
            return
        self.name = "Full report."
        self.reporter.full_maker()
        self.active = self.reporter.full
        print(self.active)
        self.unsaved = 1

    def save_active(self):
        if self.active.empty:
            print("No active report loaded.")
            return
        elif self.unsaved == 0: #also generalize this function
            print("Active report already saved.")
            return
        while True: #Make a "saver" parent class with only this function
            sv_filename = input("Input filename to write:\n> ")
            if exists(sv_filename):
                if input("File already exists. Overwrite? y\n\n> ") == 'y':
                    break
            else:
                break
        self.active.to_csv(sv_filename)
        print("Report saved.")
        self.unsaved = 0

class RunTracker(object):

    def start_table(self):
        while True:
            infile = input("Data file name: ")
            if not exists(infile):
                print("File not found. Try again.")
            else:
                break
        tablename = infile #redundant, track down references and remove.
        table = Table(infile, tablename, self.types)
        self.table = table
        reports = Reports(self.table)
        self.reports = reports

    def load_typefile(self):
        while True:
            infile = input("Budget typefile name: ")
            if not exists(infile):
                print("File not found. Try again.")
            else:
                break
        self.types = BudgetTypes(infile, self.table, infile)

    def show_menu(self):

        if self.table.unsaved == 1:
            self.table_unsaved = "(unsaved)"
        elif self.table.unsaved == 0:
            self.table_unsaved = ""
        if self.types.unsaved == 1:
            self.types_unsaved = "(unsaved)"
        elif self.types.unsaved == 0:
            self.types_unsaved = ""
        if self.reports.unsaved == 1:
            self.reports_unsaved = "(unsaved)"
        elif self.reports.unsaved == 0:
            self.reports_unsaved = ""

        menu = f'''
                Menu:
                    0. Show this menu
                Transaction data:
                    1. Load transaction data   2. Add new transaction data
                    3. Peek data               4. Save data
                Budget types:
                    5. Load budget typefile    6. View budget types
                    7. Add new budget type     8. Combine 2 budget types
                    9. Remove budget type      10. Enter keyword editor
                    11. Save updated typefile
                Using the expense tracker:
                    12. Auto-assign types to untyped transactions
                    13. Manually assign types to untyped transactions
                Reports:
                    14. Generate a specific annual summary
                    15. Generate a complete summary by years
                    16. Save active report as csv.
Active data: {self.table.name} {self.table_unsaved}
Active types: {self.types.name} {self.types_unsaved}
Active report: {self.reports.name} {self.reports_unsaved}'''
        print(menu)

    def __init__(self, start_table, start_budget, start_reports):
        self.table = start_table
        self.types = start_budget
        self.reports = start_reports
        self.table_unsaved = ""
        self.types_unsaved = ""
        self.reports_unsaved = ""
        self.menu_dict = [ #I'm using these lambdas to keep menu up to date
            self.show_menu, #but I ought replace act() with if statements.
            self.start_table,
            lambda: self.table.add_data(),
            lambda: self.table.peek_data(),
            lambda: self.table.save_data(),
            self.load_typefile,
            lambda: self.types.view_typelist(),
            lambda: self.types.add_new_type(),
            lambda: self.types.combine_type(),
            lambda: self.types.remove_type(),
            lambda: self.types.key_edit(),
            lambda: self.types.save_typefile(),
            lambda: self.table.assign_types(1, 1),
            lambda: self.table.fill_untyped(),
            lambda: self.reports.gen_year_report(),
            lambda: self.reports.gen_full_report(),
            lambda: self.reports.save_active()
       ]

    def act(self, input):
        self.menu_dict[int(input)]()

blanktable = Table("data/init/t0", "None", None)
blankbudget = BudgetTypes("data/init/d0", blanktable, "None")
blankreports = Reports(blanktable)
start_program = RunTracker(blanktable, blankbudget, blankreports)
start_program.show_menu()

while True:
    next_action = input("> ")
    try:
        if int(next_action) in range(17):
            start_program.act(int(next_action))
    except ValueError:
        print(ValueError)
        print("Command not understood.")
        if next_action == "save_report":
            start_program.reports.save_active()
##        if next_action == "test_assign":
##            start_program.table.assign_types(1, 1)
#        if next_action == "test_fill":
#            start_program.table.fill_untyped()
        if next_action == "exit":
            exit()
        if next_action == "quit":
            quit()
##        if next_action == "sort_dict":
##            start_program.types.sort_dict()
#        if next_action == "assign":
#            start_program.table.assign_types(1, 1)
#        if next_action == "view":
##            print(start_program.table.datatable.head(30))
        else:
            print("Command not understood.")
