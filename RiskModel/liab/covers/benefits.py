from liab.covers.frame import Frame
from liab.general import look_for_in_df
import math


class Benefits(Frame):
    def __init__(self, valuation_date, policies, policy_number, assumptions, fund, step_until=50, step_size=1):
        self.month = policies.look_for('durationif_m', line=policy_number)
        self.age_at_entry = policies.look_for('age_at_entry', line=policy_number)
        self.policies = policies
        self.product_assumptions = assumptions.product_assumptions
        self.product_features = assumptions.product_features
        super().__init__(step_until=step_until, step_size=step_size, month=self.month, age_x=self.age_at_entry,
                         valuation_date=valuation_date)
        self.typeof_product = policies.look_for('product', line=policy_number)
        self.death_value(policy_number, fund)
        self.critical_illness_value(policy_number, fund)
        self.ibnr_reserve_value(assumptions.product_assumptions, fund)
        self.surr_value(policy_number, assumptions.surrpenalties, fund)
        self.maturity_value(policy_number, fund)
        self.annuity_value(policy_number)
        self.benefit_from_fund(fund)

    def death_value(self, policy_number, fund):
        if self.product_features.look_for('death value  (y/n)',
                                          label=self.policies.look_for('product', line=policy_number)) == 0:
            pass
        elif self.product_features.look_for('death value  (y/n)',
                                            label=self.policies.look_for('product',
                                                                         line=policy_number)).lower() == 'sum_assured':
            values = []
            for step in range(self.step_size - 1, self.step_until, self.step_size):
                values.append(self.policies.look_for('sum_assured', line=policy_number))
            self.df['death_value'] = values
        else:
            values = []
            for step in range(self.step_size - 1, self.step_until, self.step_size):
                values.append(max(self.policies.look_for('sum_assured', line=policy_number), fund.df['capital_fund_value'][step]
                                  + max(0, fund.df['accumulation_account'][step])))
            self.df['death_value'] = values

    def critical_illness_value(self, policy_number, fund):
        if self.product_features.look_for('critical illness (y/n)',
                                          label=self.policies.look_for('product', line=policy_number)) == 0:
            pass
        elif str(self.product_features.look_for('critical illness (y/n)',
                                            label=self.policies.look_for('product',
                                                                         line=policy_number))).lower() == 'sum_assured':
            values = []
            for step in range(self.step_size - 1, self.step_until, self.step_size):
                values.append(self.policies.look_for('sum_assured_ci', line=policy_number)
                              - self.policies.look_for('sum_assured', line=policy_number))
            self.df['critical_illness_value'] = values
        else:
            values = []
            for step in range(self.step_size - 1, self.step_until, self.step_size):
                values.append(max(self.policies.look_for('sum_assured_ci', line=policy_number), fund.df['capital_fund_value'][step]
                                  + max(0, fund.df['accumulation_account'][step]))
                              - max(self.policies.look_for('sum_assured_ci', line=policy_number), fund.df['capital_fund_value'][step]
                                  + max(0, fund.df['accumulation_account'][step])))
            self.df['critical_illness_value'] = values

    def ibnr_reserve_value(self, productassumptions, fund):
        values = [(self.df['death_value'][0] - fund.df['capital_fund_value'][0] - fund.df['accumulation_account'][0])
                  * productassumptions.look_for(label=self.typeof_product, category='ibnr_pc') / 100]
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(values[step-1])

        self.df['ibnr_reserve_value'] = values

    def surr_value(self, policy_number, surrpenalties, fund):
        if self.product_features.look_for('surr value (y/n)',
                                          label=self.policies.look_for('product', line=policy_number)) == 0:
            pass
        else:
            values = []
            for step in range(self.step_size - 1, self.step_until, self.step_size):
                values.append(1 - surrpenalties.look_for(str(math.floor(look_for_in_df(self.df, 'month', step) / 12)),
                                                         label=
                                                             self.policies.look_for('product', line=policy_number),
                                                            )
                              / 100 * (fund.df['capital_fund_value'][step] + fund.df['accumulation_account'][step]))
            self.df['surr_percent'] = values

    def maturity_value(self, policy_number, fund):
        if self.product_features.look_for('maturity value (y/n)',
                                          label=self.policies.look_for('product', line=policy_number)) == 0:
            pass
        else:
            values = []
            for step in range(self.step_size - 1, self.step_until, self.step_size):
                values.append(fund.df['capital_fund_value'][step] + fund.df['accumulation_account'][step])
            self.df['maturity_value'] = values

    def annuity_value(self, policy_number):
        if self.product_features.look_for('imm annuity (y/n)',
                                          label=self.policies.look_for('product', line=policy_number)) == 0:
            pass
        else:
            values = ['']
            for step in range(self.step_size, self.step_until, self.step_size):
                values.append(
                    self.policies.look_for('annuity_payment_annual', line=policy_number) / self.policies.look_for(
                        'annuity_freq', line=policy_number))
            self.df['annuity_value'] = values

    def benefit_from_fund(self, fund):
        self.df['death_value_pre_dedn'] = fund.death_value_pre_dedn
        self.df['critical_illness_value_pre_dedn'] = fund.critical_illness_value_pre_dedn
        self.df['death_sar_pre_dedn'] = fund.death_sar_pre_dedn
