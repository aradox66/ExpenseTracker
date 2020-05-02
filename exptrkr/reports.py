import pandas as pd
#data = pd.read_csv("../data/typed/BSB19_typed.csv")
#                    names=["date","memo","type","amount"])
###

class Reporter(object):

    def __init__(self, data):
        self.data = data.datatable
#        self.data = data

    def sorter(self):
        self.data.date = pd.to_datetime(self.data.date)
        self.data['year'] = self.data.date.dt.year
        self.data['month'] = self.data.date.dt.month

    def round_25(self, x):
        return (x // 25) * 25

    def neg_income(self, table):
        if 'income' in table.columns:
            table = table.transpose()
            a=1
        elif 'income' in table.index:
            a=0
        else:
            return
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
        self.sorter()
        self.year_report = pd.DataFrame(index=self.data.type.unique())
        self.year_report = self.year_report.merge(
                    self.year_avg(year).rename(columns={'amount':'Avg'}),
                    left_index=True, right_index=True)
        for i in range(1, 13):
            self.year_report = self.year_report.merge(
                    self.data[(self.data.year == year) & (self.data.month == i)]
                    .drop(['year','month'], axis=1).groupby('type').sum()
                    .rename(columns={'amount':i}), left_index=True,
                    right_index=True, how='left').fillna(value=0)
        self.data.drop(['year', 'month'], axis=1, inplace=True)
        self.year_report = self.add_space(self.surplus(
                            self.neg_income(self.year_report)))

    def full_maker(self):
        self.sorter()
        self.full = pd.DataFrame(index=self.data.type.unique())
        for i in self.data.year.unique():
            self.full = self.full.merge(self.year_avg(i).
                rename(columns={'amount':i}),
                left_index=True,right_index=True)
        self.data.drop(['year', 'month'], axis=1, inplace=True)
        self.full = self.add_space(self.surplus(self.neg_income(self.full)))

#reports = Reporter(data)
#reports.sorter()
