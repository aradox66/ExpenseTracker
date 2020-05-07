import pandas as pd
from parents import Functioner

class Ledger(Functioner):    
    def __init__(self, infile):
        from csv_input import Munger
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
            
