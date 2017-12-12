from liab.covers.decrements import Decrements
from liab.covers.economic import Economic
from liab.covers.premium import Premium
from liab.covers.fund import Fund
from liab.covers.benefits import Benefits
from liab.covers.expenses import Expenses
from liab.covers.cashflows import Cfs
from liab.covers.discounted_cashflows import DiscountedCfs
import pandas as pd


class LiabilityCalculations:
    def __init__(self, policies, policy_number, assumptions, valuation_date, step_until=50):
        self.policies = policies
        self.policy_number = policy_number
        self.assumptions = assumptions
        self.valuation_date = valuation_date
        self.step_until = step_until

        self.decrements = self.add_decrements()
        self.val_decrements = self.add_decrements(val='val ')
        self.premium = self.add_premium()
        self.economic = self.add_economic()
        self.fund = self.add_fund()
        self.benefits = self.add_benefits()
        self.expenses = self.add_expenses()
        self.val_expenses = self.add_expenses(val=True)
        self.cfs = self.add_cfs()
        self.val_cfs = self.add_cfs(val=True, val_decrements=self.val_decrements)
        self.discounted_cfs = self.add_discounted_cfs()

    def add_decrements(self, val=''):
        """
        Create decrements calculations
        :param val: Prepend column titles with the parameter, if not default (empty)
        E.g. 'val ' -> 'val tbl mort key'
        :return: Decrements object with calculation results
        """
        column_titles = [val + 'tbl mort key', val + '%tbl mort', val + 'lps ass key', val + 'tbl ci key',
                         val + '%tbl ci']
        obj = Decrements(self.valuation_date, self.policies, self.policy_number, self.assumptions, column_titles,
                         step_until=self.step_until)
        return obj

    def add_premium(self):
        obj = Premium(self.valuation_date, self.policies, self.policy_number, step_until=self.step_until)
        return obj

    def add_benefits(self):
        obj = Benefits(self.valuation_date, self.policies, self.policy_number, self.assumptions, self.fund,
                       step_until=self.step_until)
        return obj

    def add_economic(self):
        obj = Economic(self.valuation_date, self.policies, self.policy_number, self.assumptions,
                       step_until=self.step_until)
        return obj

    def add_expenses(self, val=False):
        obj = Expenses(self.valuation_date, self.policies, self.policy_number, self.assumptions, self.premium,
                       self.economic, step_until=self.step_until, val=val)
        return obj

    def add_fund(self):
        obj = Fund(self.valuation_date, self.policies, self.policy_number, self.assumptions, self.premium,
                   self.economic, step_until=self.step_until)
        return obj

    def add_cfs(self, val=False, val_decrements=None):
        """ passing val_decrements as parameter, so it's passed only when it's called for, else it's None """
        obj = Cfs(self.valuation_date, self.policies, self.policy_number, self.decrements, self.premium, self.benefits,
                  self.expenses, self.assumptions.chargescommission, step_until=self.step_until, val=val,
                  val_decrements=val_decrements)
        return obj

    def add_discounted_cfs(self):
        obj = DiscountedCfs(self.valuation_date, self.policies, self.policy_number, self.economic, self.cfs,
                            step_until=self.step_until)
        return obj

    def all_to_excel(self, filename='liabality calculations'):
        """ write multiple sheets into an excel file """
        writer = pd.ExcelWriter('results/' + filename + '.xlsx')
        self.decrements.df.to_excel(writer, 'Decrements', na_rep='-')
        self.premium.df.to_excel(writer, 'Premium')
        self.economic.df.to_excel(writer, 'Economic')
        self.fund.df.to_excel(writer, 'Fund')
        self.benefits.df.to_excel(writer, 'Benefits')
        self.expenses.df.to_excel(writer, 'Exp&Comm')
        self.cfs.df.to_excel(writer, 'CFs')
        self.discounted_cfs.df.to_excel(writer, 'Discounted CFs')
        self.val_decrements.df.to_excel(writer, 'Val Decrements', na_rep='-')
        writer.save()
