import pandas as pd
from os.path import exists
from parents import Functioner

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

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


