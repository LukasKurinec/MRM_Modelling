from liab.assumptions.economic import Economic
from liab.assumptions.expense import Expense
from liab.assumptions.mortality import Mortality
from liab.assumptions.persistency import Persistency
from liab.policies.chargescommission import ChargesCommission
from liab.policies.surrpenalties import SurrPenalties
from liab.products.product_features import ProductFeatures
from liab.products.product_assumptions import ProductAssumptions


class Assumptions:
    # TODO: inputs: named inputs for each modul + one input for all (Dict?)
    def __init__(self, mortality=None, economic=None, expense=None, persistency=None, surrpenalties=None,
                 chargescommision=None, productfeatures=None, productassumptions=None, input_dict=None):
        if input_dict:
            self.input_dict = input_dict
            self.mortality \
                , self.economic \
                , self.expense \
                , self.persistency \
                , self.surrpenalties \
                , self.chargescommission \
                , self.product_features \
                , self.product_assumptions \
                = self.add_all()
        else:
            self.mortality = self.add_mortality(mortality)
            self.economic = self.add_economic(economic)
            self.expense = self.add_expense(expense)
            self.persistency = self.add_persistency(persistency)
            self.surrpenalties = self.add_surrpenalties(surrpenalties)
            self.chargescommission = self.add_charges(chargescommision)
            self.product_features = self.add_product_features(productfeatures)
            self.product_assumptions = self.add_product_assumptions(productassumptions)
            # self.ageband = self.age_band(age)

    def age_band(self, age):
        if age <= 50:
            return 1
        elif age <= 55:
            return 2
        elif age <= 60:
            return 3
        elif age <= 65:
            return 4
        elif age <= 70:
            return 5
        else:
            return 6

    def add_all(self):
        mortality = None
        for key, value in self.input_dict.items():
            if key.lower() == 'mortality':
                mortality = value.keys()
        return mortality  # , economic, expense, persistency, surrpenelties, charges

    def add_mortality(self, filename):
        if filename:
            obj = Mortality(filename=filename)
        else:
            obj = Mortality()
        return obj

    def add_economic(self, filename):
        if filename:
            obj = Economic(filename=filename)
        else:
            obj = Economic()
        return obj

    def add_expense(self, filename):
        if filename:
            obj = Expense(filename=filename, index_col=0)
        else:
            obj = Expense(index_col=0)
        return obj

    def add_persistency(self, filename):
        if filename:
            obj = Persistency(filename=filename, index_col=(0, 1))
        else:
            obj = Persistency(index_col=(0, 1))
        return obj

    def add_surrpenalties(self, filename):
        if filename:
            obj = SurrPenalties(filename=filename, index_col=0)
        else:
            obj = SurrPenalties(index_col=0)
        return obj

    def add_charges(self, filename):
        if filename:
            obj = ChargesCommission(filename=filename, index_col=0)
        else:
            obj = ChargesCommission(index_col=0)
        return obj

    def add_product_features(self, filename):
        if filename:
            obj = ProductFeatures(filename=filename, index_col=0)
        else:
            obj = ProductFeatures(index_col=0)
        return obj

    def add_product_assumptions(self, filename):
        if filename:
            obj = ProductAssumptions(filename=filename, index_col=0)
        else:
            obj = ProductAssumptions(index_col=0)
        return obj
