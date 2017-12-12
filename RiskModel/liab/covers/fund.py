from liab.covers.frame import Frame
from liab.covers.calculations import fund_and_benefits_circle


class Fund(Frame):
    def __init__(self, valuation_date, policies, policy_number, assumptions, premiums, economic, step_until=50,
                 step_size=1):
        self.month = policies.look_for('durationif_m', line=policy_number)
        self.age_at_entry = policies.look_for('age_at_entry', line=policy_number)
        self.product_assumptions = assumptions.product_assumptions
        super().__init__(step_until=step_until, step_size=step_size, month=self.month, age_x=self.age_at_entry,
                         valuation_date=valuation_date)
        self.typeof_charges = self.product_assumptions.look_for('charges&comm key',
                                                                label=policies.look_for('product', line=policy_number))
        self.allocation_charge(assumptions.chargescommission, premiums)
        self.term_cap_y = policies.look_for('term_cap_y', line=policy_number)
        self.fund_value_cap_init = policies.look_for('fund_value_cap_init', line=policy_number)
        self.capital_account_premium(premiums)
        self.capital_fund_value(assumptions.chargescommission)
        self.accumulation_allocation_premium(premiums)
        self.fix_admin_exp_charge(assumptions.chargescommission, economic)
        self.death_value_pre_dedn, self.critical_illness_value_pre_dedn, self.death_sar_pre_dedn \
            = self.fund_benefits_circle(assumptions.chargescommission, assumptions.product_features,
                                        assumptions.product_assumptions, policies, policy_number, economic)

    def allocation_charge(self, chargescommission, premiums):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(premiums.df['premium_value'][step] / 100 *
                          chargescommission.look_for(label=self.typeof_charges, category='init_chga_pc'))
        self.df = self.df.assign(allocation_charge=values)

    def capital_account_premium(self, premiums):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            if self.month + step <= self.term_cap_y * 12:
                values.append(premiums.df['premium_value'][step] - self.df['allocation_charge'][step])
            else:
                values.append(0)
        self.df = self.df.assign(capital_account_premium=values)

    def capital_fund_value(self, chargescommission):
        capital_fund_value = [self.fund_value_cap_init]
        inv_return_on_capital_account = ['']
        capital_charge = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            inv_return_on_capital_account.append(
                capital_fund_value[step - 1] + self.df['capital_account_premium'][step])
            capital_charge.append(capital_fund_value[step - 1]
                                  * chargescommission.look_for(label=self.typeof_charges,
                                                               category='charge_assetmng') / 1200)
            capital_fund_value.append(capital_fund_value[step - 1] + capital_charge[step]
                                      + inv_return_on_capital_account[step] + self.df['capital_account_premium'][step])
        self.df = self.df.assign(capital_fund_value=capital_fund_value)
        self.df = self.df.assign(inv_return_on_capital_account=inv_return_on_capital_account)
        self.df = self.df.assign(capital_charge=capital_charge)

    def accumulation_allocation_premium(self, premiums):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            if self.month + step > self.term_cap_y * 12:
                values.append(premiums.df['premium_value'][step] - self.df['allocation_charge'][step])
            else:
                values.append(0)
        self.df = self.df.assign(accumulation_allocation_premium=values)

    def fix_admin_exp_charge(self, chargescommission, economic):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(chargescommission.look_for(label=self.typeof_charges, category='fixed_dedn_y') / 12
                          * economic.df['index_infl_m_exp_dedn'][step])
        self.df = self.df.assign(fix_admin_exp_charge=values)

    def fund_benefits_circle(self, chargescommission, product_features, product_assumptions, policies, policy_number,
                             economic):
        death_value_pre_dedn, critical_illness_value_pre_dedn, death_sar_pre_dedn, accumulation_account_pre_dedn, \
        risk_charge, accumulation_account_post_dedn, return_on_accumulation_account, asset_management_charge, \
        accumulation_account = fund_and_benefits_circle(self, chargescommission, product_features, product_assumptions,
                                                        policies, policy_number, economic)
        self.df = self.df.assign(accumulation_account_pre_dedn=accumulation_account_pre_dedn)
        self.df = self.df.assign(risk_charge=risk_charge)
        self.df = self.df.assign(accumulation_account_post_dedn=accumulation_account_post_dedn)
        self.df = self.df.assign(return_on_accumulation_account=return_on_accumulation_account)
        self.df = self.df.assign(asset_management_charge=asset_management_charge)
        self.df = self.df.assign(accumulation_account=accumulation_account)
        return death_value_pre_dedn, critical_illness_value_pre_dedn, death_sar_pre_dedn
