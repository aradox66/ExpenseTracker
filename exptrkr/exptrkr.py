import pandas as pd
from os.path import exists
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
class Functioner(object):

    def load(self):
        while True:
            infile = input("File name:\n> ")
            if not exists(infile):
                print("File not found. Try again.")
            else:
                break
        return infile
            
    def check_load(self, which, datatype):
        if which == None:
            print(f"Load {datatype} first.")
            return 1
        else:
            return 0
        
    def save_filename(self):
        while True:
            sv_filename = input("Input filename to write:\n> ")
            if exists(sv_filename):
                if input("File already exists. Overwrite? y\\n\n> ") == 'y':
                    break
            else:
                break        
        return sv_filename

    def check_unsaved(self, datatype):
        if self.unsaved == 0:
            print(f"{datatype} has no unsaved changes.")
            return 1
    def int_it(self, inp):
        while True:
            try:
                intp = int(inp)
                return intp
            except:
                print(f"{inp} is not an integer, please correct:")
                inp = input("> ")

class Typedict(Functioner):
    def sort_dict(self):
        dp_sort = pd.concat([self.data[col]
                    .sort_values().reset_index(drop=True)
                             for col in self.data], axis=1, ignore_index=True)
        dp_sort.columns = self.data.columns
        self.data = dp_sort.reindex(sorted(dp_sort.columns), axis=1)

    def __init__(self, option, *infile):
        if option == 0:
            self.new_dict()
            self.name = "New dict"
            self.unsaved = 1
        else:
            self.name = infile[0]
            self.data = pd.read_csv(infile[0])
            self.sort_dict()
            self.unsaved = 0
        
    def save(self):
        sv_filename = self.save_filename()
        self.data.to_csv(sv_filename, index=False)
        self.name = sv_filename
        self.unsaved = 0
        print("Dictionary saved.")

    def add_dict(self):
        #It would be cool to be able to load a second dict and combine it.
        pass
    def new_dict(self):
        self.data = pd.DataFrame()
    def view_typelist(self):
        print("Types are: " + ", ".join(self.data.columns) + ".")
        
    def add_typ(self):
        new_type = input("New type name:\n> ")
        if new_type in self.data.columns:
            print("Type already exists.")
            return
        else:
            self.data[new_type] = None
        self.unsaved = 1
    def rem_typ(self):
        if self.data.empty:
            print("No types to remove!")
            return
        for i in range(len(self.data.columns)):
            print(f"{i}: {self.data.columns[i]}", end=", ")
        rm_type = int(input("\nInput type index to remove: "))
        rm_type_name = self.data.columns[rm_type]
        self.data.drop(rm_type_name, axis=1, inplace=True)
        self.unsaved = 1
        if input("Remove type from transaction data? y/n: ") == 'y':
            return rm_type_name
    def com_typ(self):
        for i in range(len(self.data.columns)):
            print(f"{i}: {self.data.columns[i]}", end=", ")
        type1 = input("\nInput first type index: ")
        type1 = self.data.columns[self.int_it(type1)]
        type2 = input("Input second type index: ")
        type2 = self.data.columns[self.int_it(type2)]
        comb_type = input("New combined type name: ")
        if comb_type in self.data.columns:
            comb_type = comb_type + "2"
        new = (self.data[type1].append(self.data[type2]).
                dropna().sort_values().to_frame().reset_index(drop=True))
        new.columns=[comb_type]
        self.data.drop([type1, type2], axis=1, inplace=True)
        if len(self.data) > len(new):
            how_x = "left"
        else:
            how_x = "right"
        self.data = self.data.merge(new, left_index=True,
                            right_index=True, how=how_x)
        self.sort_dict()
        self.unsaved = 1
    def view_dict(self):
        for i in range(len(self.data.columns)):
            typ = self.data.columns[i]
            print(typ + ": " + ", ".join(
                self.data.loc[self.data[typ].notnull(), typ]))
    def get_type(self, option):
        while True:
            which = input(f"Enter budget type to {option} keywords:\n> ")
            if not which in self.data.columns:
                print(f"{which} is not one of the budget types. Check for typos.")
                self.view_typelist()
            else:
                return which        
    def add_keys(self):
        new_keys = []
        which = self.get_type('add')
        while True:
            print(f"Input new keys for {which}, or ENTER:", end="")
            new = input("> ")
            if new == "":
                break
            else:
                new_keys.append(new)
        if len(new_keys) != 0:
            self.unsaved = 1
            new_tuple = (which, new_keys)
            self.update([new_tuple])
        self.sort_dict()
        print("Keys added.")        
    def rem_keys(self):
        which = self.get_type('remove')
        a = 0
        for k in self.data[which][
            self.data[which].notnull()]:
            print(f"{a}. {k}")
            a += 1
        rems = input("Input indexes separated by spaces:\n> ").split(" ")
        rems_list = []
        for i in rems:
            rems_list.append(self.int_it(i))
        if len(rems_list) > 0:
            self.unsaved = 1
        if len(rems_list) != 0:
            print(f"Removing "
                  + ", ".join(self.data.loc[rems_list, which]),
                  end=".\n")
        new_col = self.data[which].dropna().to_frame()
        new_col.drop(rems_list, inplace=True)
        new_col.reset_index(inplace=True, drop=True)
        self.data.drop(which, axis=1, inplace=True)
        if len(self.data) > len(new_col):
            how_x = "left"
        else:
            how_x = "right"
        self.data = self.data.merge(new_col, left_index=True,
                                    right_index=True, how=how_x)
    def update(self, new_tuples):
        for i in new_tuples:
            i_p = pd.Series(i[1], name=i[0])
            if i[0] in self.data.columns:
                i_p = self.data[i[0]].append(i_p).dropna().to_frame()
                i_p.reset_index(inplace=True, drop=True)
                self.data.drop(i[0], axis=1, inplace=True)
            if len(self.data) > len(i_p):
                how_x = "left"
            else:
                how_x = "right"
            self.data = self.data.merge(i_p, left_index=True,
                                right_index=True, how=how_x)
        self.sort_dict()
        self.unsaved = 1

class Munger(Functioner):
    def intake(self, infile):
        self.data = pd.read_csv(infile, header=None).fillna("")

    def check_clean(self):
        if list(self.data.iloc[0]) == ["date", "memo", "type", "amount"]:
            print("Already cleaned data! Great.")
            self.data.columns = list(self.data.loc[0])
            self.data.drop(0, axis=0, inplace=True)
            self.data_clean = self.data.reset_index(drop=True)
            self.data_clean.amount = self.data_clean.amount.astype('float')
            self.clean = 1
            self.cleaned = 0
        else:
            print("Let's proceed with cleanup.\n")
            self.clean = 0
            self.cleaned = 1

    def header(self):
        if self.clean == 1:
            return
        print(self.data.head(2))
        if input("\nDoes this data have a header? y/n\n> ") == "y":
            self.header = 1
            self.data.columns = self.data.loc[0]
            self.data.drop(0, axis=0, inplace=True)
        else:
            self.header = 0

    def classify(self):
        if self.clean == 1:
            return
        print("Aight we gonna classify these columns.")
        print("Take a good luck and press ENTER when ready.\n")
        print(self.data.head(5))
        input("> ")
        print("\nThere are only 3 or 4 columns that matter - ")
        print("Date, Memo, & Amount OR Date, Memo, Credit & Debit\n")
        for i in range(0, len(self.data.columns)):
            print(f"{i}. {self.data.columns[i]}, ", end="")
        print("\nPlease input column index: ")
        date_c = int(input("Date: "))
        memo_c = int(input("Memo: "))
        deb_c = int(input("Debit/Amount: "))
        cred_c = int(input("Credit, or amount if same: "))
        date_s = self.data.iloc[:, date_c]
        memo_s = self.data.iloc[:, memo_c]
        if deb_c == cred_c:
            amount_s = self.data.iloc[:, cred_c].astype(float)

        else:
            amount_s = self.data.iloc[:, deb_c].astype(float).subtract(
                self.data.iloc[:, cred_c].astype(float))

        print(pd.DataFrame([memo_s, amount_s]).transpose().iloc[0:10])
        print("Debits should be POSITIVE, credits should be NEGATIVE.")
        if input("Is it correct, y/n?\n> ") == 'n':
            amount_s = amount_s.apply(lambda x: -x)

        data_clean = pd.DataFrame(zip(date_s, memo_s,amount_s),
                        columns=["date", "memo", "amount"])
        input("Data cleaned. ENTER to proceed.")
        self.data_clean = data_clean

    def add_type(self):
        if self.clean == 1:
            return
        self.data_clean['type'] = 'untyped'
        self.data_clean = self.data_clean[["date", "memo", "type", "amount"]]

    def save(self):
        sv_filename = self.save_filename()
        self.data_clean.to_csv(sv_filename, index=False)

    def load(self, infile):
        self.intake(infile)
        self.check_clean()
        self.header()
        self.classify()
        self.add_type()

class Ledger(Functioner):    
    def __init__(self, infile):
        self.mungeit = Munger()
        self.mungeit.load(infile)
        self.data = self.mungeit.data_clean
        self.unsaved = self.mungeit.cleaned
        self.counts()
        self.name = infile
        self.r_name = ""
        self.unsaved_r = 0
        self.active = None
    def counts(self):
        typed = self.data[(self.data.type != "untyped") & (self.data.type != "")]
        self.typed = len(typed)
        self.typed_cash = typed.amount.abs().sum()
        self.tot_cash = self.data.amount.abs().sum()
        self.perc_typ = int((self.typed / len(self.data)) * 100)
        self.perc_sum = int((self.typed_cash / self.data.amount.abs().sum()) * 100)

    def typ_report(self):
        self.counts()
        print(f"{self.perc_typ}% of transactions successfully typed.")
        print(f"There are {len(self.data) - self.typed} untyped entries.")
        perc_sum = int(((self.tot_cash - self.typed_cash) / self.tot_cash) * 100)
        print(f"{self.perc_sum}% of total cash spent remains untyped.")
        return self.perc_sum
        
    def save(self):
        if self.check_unsaved('Ledger'):
            return
        sv_filename = self.save_filename()
        self.data.to_csv(sv_filename, index=False)
        
    def add(self):
        infile = self.load()
        self.mungeit.load(infile)
        new_data = self.mungeit.data_clean
        self.data = self.data.merge(new_data, how="outer")
        self.unsaved = 1

    def rem(self, rem):
        self.data.loc[self.data.type == rem, 'type'] = 'untyped'
        self.unsaved = 1
    def peek(self):
        print(self.data.head(int(input("How many?\n> "))))


    def sorter(self):
        self.data.date = pd.to_datetime(self.data.date)
        self.data['year'] = self.data.date.dt.year
        self.data['month'] = self.data.date.dt.month
    def drop_sort(self):
        self.data.drop(['year', 'month'], axis=1, inplace=True)
    def round_25(self, x):
        return (x // 25) * 25

    def neg_income(self, table):
        if 'income' in table.columns:
            table = table.transpose()
            a=1
        elif 'income' in table.index:
            a=0
        else:
            return table
        table.loc['income'] = (
                table.loc['income'].apply(lambda x: -x))
        if a==1:
            table = table.transpose()
        return table

    def surplus(self, table):
        if not 'income' in table.index:
            return table
        surp = table.transpose()
        summers = surp.columns.to_list()
        summers.remove('income')
        surp['surplus'] = surp.income - surp[summers].sum(axis=1)
        return surp.transpose()

    def year_avg(self, year):
        year_avg = (self.data[self.data.year == year]
                    .drop('year', axis=1)
                    .groupby(['month','type']).sum()
                    .groupby(['type']).mean().fillna(value=0)
                    .apply(lambda x: self.round_25(x))
                    .astype(int))
        return self.surplus(year_avg)

    def add_space(self, report):
        report = report.transpose()
        r_list = report.columns.to_list()
        r_list_hold = r_list.pop(-1)
        r_list.extend(['', r_list_hold])
        report[''] = ''
        report = report.reindex(columns=r_list)
        return report.transpose()

    def year_sum(self, year):
        self.year_report = pd.DataFrame(index=self.data.type.unique())
        self.year_report = self.year_report.merge(
                    self.year_avg(year).rename(columns={'amount':'Avg'}),
                    left_index=True, right_index=True)
        for i in self.data.month.sort_values().unique():
            self.year_report = self.year_report.merge(
                    self.data[(self.data.year == year) & (self.data.month == i)]
                    .drop(['year','month'], axis=1).groupby('type').sum()
                    .rename(columns={'amount':i}), left_index=True,
                    right_index=True, how='left').fillna(value=0)
        self.year_report = self.add_space(self.surplus(
                            self.neg_income(self.year_report)))
        self.drop_sort()

    def full_maker(self):
        self.sorter()
        self.full = pd.DataFrame(index=self.data.type.unique())
        for i in self.data.year.unique():
            self.full = self.full.merge(self.year_avg(i)
                                        .rename(columns={'amount':i}),
                                        left_index=True,right_index=True,
                                        how='left').fillna(value=0)
        self.drop_sort()
        self.full = self.add_space(self.surplus(self.neg_income(self.full)))
        
    def report(self, option):
        if option == 0: # year report
            if self.check_load('da', 'sorted transaction data'):
                return
            year = self.int_it(input("Input year:\n> "))
            self.sorter()
            if not year in self.data.year.unique():
                print("Year not included in data.")
                self.drop_sort()
                return
            self.year_sum(year)
            self.active = self.year_report
            print(self.year_report)
            self.r_name = str(year) + " summary."
            self.unsaved_r = 1
        if option == 1: # full report
            if self.check_load('da', 'sorted transaction data'):
                return
            self.r_name = "Full report."
            self.full_maker()
            self.active = self.full
            print(self.full)
            self.unsaved_r = 1
        if option == 2: #save report
            if self.r_name == "":
                print("No active report loaded.")
                return
            elif self.unsaved_r == 0:
                print(f"Report already saved.")
            sv_filename = self.save_filename()
            self.active.to_csv(sv_filename)
            print("Report saved.")
            self.unsaved_r = 0
            
class ExpenseTracker(Functioner):
    def __init__(self):
        self.ledger = None
        self.dict = None
        self.sub = 0
    def new_dict(self):
        self.dict = Typedict(0)
    def ready_check(self, *which):
        if ('da' in which) & (self.ledger == None):
            if not 1 in which:
                print("Load data first!")
            return 1
        elif ('di' in which) & (self.dict == None):
            if not 1 in which:
                print("Load type dictionary first!")
            return 1

    def load_dict(self):
        infile = self.load()
        self.dict = Typedict(1, infile)
        print("Dictionary loaded.")

    def load_data(self):
        infile = self.load()
        self.ledger = Ledger(infile)

    def auto_type(self, overwriter):
        if self.ready_check('da', 'di'):
            return
        if overwriter == 1:
            if input("Overwrite existing types? y/n:\n> ") != 'y':
                overwriter = 0
        print("Working...")
        types = list(self.dict.data.columns)
        for i in range(len(self.ledger.data)):
            if ((self.ledger.data.iloc[i, 2] != "untyped")
                & (self.ledger.data.iloc[i, 2] != "") & (overwriter == 0)):
                continue
            for j in types:
                # I have to learn more about how this algorithm functions.
                if any(match in self.ledger.data.memo[i] for match in filter(
                        None, self.dict.data[j].fillna(value=""))):
                    self.ledger.data.iloc[i, 2] = j
                    break
            perc_done = int((i/len(self.ledger.data))*100)
            print(f"\r{perc_done}%", end="")
        print()

        self.ledger.typ_report()
        self.ledger.unsaved = 1
        
    def man_type(self):
        if self.ready_check('da'):
            return
        if self.ready_check('di', 1):
            self.new_dict()

        while True:
            print(f"Types are: ", end="") #Is this redundant?
            self.dict.view_typelist()
            new_tuples = []
            i = 0
            q = len(self.ledger.data[self.ledger.data.type == "untyped"])
            while i < 5 and i < q:
                print(f"For transaction:")
                trans = self.ledger.data[self.ledger.data.type == "untyped"].iloc[i]
                print(trans)
                type_i_keys = []
                type_i = input("Input type: ")
                if type_i != "":
                    self.ledger.data.iloc[trans.name, 2] = type_i
                    while True:
                        print(f"Input new keys for {type_i}, or ENTER:")
                        new = input("> ")
                        if new == "":
                            break
                        else:
                            self.ledger.unsaved = 1
                            type_i_keys.append(new)
                    type_tuple_i = (type_i, type_i_keys)
                    if len(type_tuple_i[1]) != 0:
                        new_tuples.append(type_tuple_i)
                i += 1

            if len(new_tuples) != 0:
                self.dict.update(new_tuples)

            self.auto_type(0)
            
            if input("Continue typing? y/n:\n> ") == "n":
                print("Exiting manual typing.")
                return
        self.ledger.unsaved = 1
    def dict_funct(self, option):
        if self.ready_check('di'):
            return
        if option == 0:
            self.dict.save()

    def data_funct(self, option, *suboption):
        if self.ready_check('da'):
            return
        if option == 0: #Save data
            self.ledger.save()
        elif option == 1: #Add data
            self.ledger.add()
        elif option == 2: #Peek data
            self.ledger.peek()
        elif option == 3: #View report
            if self.ledger.active == None:
                print("Load report first!")
                return
            print(self.ledger.active)
        elif option == 4: #Reports
            self.ledger.report(suboption[0])

    def d_ed_menu(self):
        menu = '''
                  0. Show this menu     1. Return to main menu
              Edit budget types: 
                  2. View   3. Add new   4. Remove   5. Combine
              Edit keywords:
                  6. View full dictionary 7. Add new 8. Remove'''
        print(menu)
        self.sub = 1

    def d_ed_actor(self, inp):
        if inp == 0: #Show menu
            self.d_ed_menu()
        elif inp == 1: #Return to main menu
            self.sub = 0
            return
        elif inp == 2: #View typelist
            if self.ready_check('di'):
                return
            self.dict.view_typelist()
        elif inp == 3: #Add type
            if self.ready_check('di', 1):
                self.new_dict()
            self.dict.add_typ()
        elif inp == 4: #Remove type
            if self.ready_check('di'):
                return
            rem = self.dict.rem_typ()
            if rem:
                self.ledger.rem(rem)
        elif inp == 5: #Combine types
            if self.ready_check('di'):
                return
            self.dict.com_typ()
        elif inp == 6: #View dictionary
            if self.ready_check('di'):
                return
            self.dict.view_dict()
        elif inp == 7: #Add keywords
            if self.ready_check('di'):
                return
            self.dict.add_keys()
        elif inp == 8: #Remove keywords
            if self.ready_check('di'):
                return
            self.dict.rem_keys()

    def menu_footer(self):
        def check(value):
            if value == 1:
                return "(unsaved)"
            else:
                return ""
        if not self.ready_check('da', 1):
            da_name = self.ledger.name
            da_saved = check(self.ledger.unsaved)
            r_name = self.ledger.r_name
            r_saved = check(self.ledger.unsaved_r)
        else:
            da_name = da_saved = r_name = r_saved = ""
        if not self.ready_check('di', 1):
            di_name = self.dict.name
            di_saved = check(self.dict.unsaved)
        else:
            di_name = di_saved = ""
        menu_footer = f'''
           Active data: {da_name} {da_saved}
           Active types: {di_name} {di_saved}
           Active report: {r_name} {r_saved}'''
        return menu_footer
    def main_menu(self):
        menu = f'''
                Menu:
                    0. Show this menu
                Budget type dictionary:
                    1. Start new type dictionary
                    2. Load dict    3. Edit dict   4. Save dict
                Transaction data:
                    5. Load data    6. Save data
                    7. Add data     8. Peek data
                Using the expense tracker:
                    9. Auto-assign types to untyped transactions
                    10. Manually assign types to untyped transactions
                Reports:
                    11. Generate a specific annual summary
                    12. Generate a complete summary by years
                    13. View active report.
                    14. Save active report as csv.
{self.menu_footer()}'''
        print(menu)

    def main_actor(self, inp):
        if inp == 0: #Show main menu
            self.main_menu()
        elif inp == 1: #New type dic
            self.new_dict()
        elif inp == 2: #Load dic
            self.load_dict()
        elif inp == 3: #Edit dic
            self.d_ed_menu()
        elif inp == 4: #Save dic
            self.dict_funct(0)
        elif inp == 5: #Load data
            self.load_data()
        elif inp == 6: #Save data
            self.data_funct(0)
        elif inp == 7: #Add data
            self.data_funct(1)
        elif inp == 8: #Peek data
            self.data_funct(2)
        elif inp == 9: #Auto-assign
            self.auto_type(1)
        elif inp == 10: #Man-assign
            self.man_type()
        elif inp == 11: #Year report
            self.data_funct(4,0)
        elif inp == 12: #Full report
            self.data_funct(4,1)
        elif inp == 13: #view report
            self.data_funct(3)
        elif inp == 14: #Save report
            self.data_funct(4,2)
        
    def actor(self):
        inp = input("> ")
        try:
            inp = int(inp)
        except:
            if (inp == "exit") | (inp == "quit"):
                exit()
            else:
                print("Error.")
            return
        if self.sub == 0:
            self.main_actor(inp)
        elif self.sub == 1:
            self.d_ed_actor(inp)

et = ExpenseTracker()
et.main_menu()

while True:
    et.actor()
