from typedict import Typedict
from ledger import Ledger
from parents import Functioner

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
