import pandas as pd
from parents import Functioner

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
