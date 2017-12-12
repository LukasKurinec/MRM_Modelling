from liab.covers.frame import Frame
from liab.covers.calculations import outgo


class Cfs(Frame):
    def __init__(self, valuation_date, policies, policy_number, decrements, premium, benefits, expenses,
                 chargescommission, step_until=50, step_size=1, val=False, val_decrements=None):
        self.month = policies.look_for('durationif_m', line=policy_number)
        self.age_at_entry = policies.look_for('age_at_entry', line=policy_number)
        self.policies = policies
        super().__init__(step_until=step_until, step_size=step_size, month=self.month, age_x=self.age_at_entry,
                         valuation_date=valuation_date)
        if val:
            self.proj_term_horizon = 40
            self.premiums_income(val_decrements, premium)
            self.val_premiums_income_net(policy_number, chargescommission)
        else:
            self.proj_term_horizon = 40
            self.premiums_income(decrements, premium)
            self.death_outgo(decrements, benefits)
            self.surrender_outgo(decrements, benefits)
            self.maturity_outgo(decrements, benefits)
            self.annuity_outgo(decrements, benefits)
            self.init_comm_paid(decrements, expenses)
            self.init_comm_clawed_lps(decrements, expenses)
            self.commission_initial()
            self.commission_renewal(decrements, expenses)
            self.expense_initial(decrements, expenses)
            self.expense_renewal(decrements, expenses)

    def premiums_income(self, decrements, premium):
        values = ['']
        last_count_live = decrements.look_for('count_live', index=0)
        for step in range(self.step_size, self.step_until, self.step_size):
            if step < self.proj_term_horizon * 12:
                if 'count_maturity' in self.df:
                    values.append(premium.look_for('premium_value', index=step) * (
                            last_count_live - decrements.look_for('count_maturity', index=step)))
                else:
                    values.append(premium.look_for('premium_value', index=step) * last_count_live)
            else:
                values.append(0)
            last_count_live = decrements.look_for('count_live', index=step)
        self.df = self.df.assign(premiums_income=values)

    def val_premiums_income_net(self, policy_number, chargescommission):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(self.df['premiums_income'][step] * (
                    1 - chargescommission.look_for('init_chga_pc',
                                                   label=self.policies.look_for('product', line=policy_number))/100))
        self.df['val_premiums_income_net'] = values

    def death_outgo(self, decrements, benefits):
        values = outgo(self, benefits, decrements, 'death_value', 'count_death')
        self.df['death_outgo'] = values

    def surrender_outgo(self, decrements, benefits):
        if 'surr_value' in self.df:
            values = outgo(self, benefits, decrements, 'surr_value', 'count_surrender')
            self.df['surrender_outgo'] = values
        else:
            pass

    def maturity_outgo(self, decrements, benefits):
        if 'count_maturity' in self.df:
            values = outgo(self, benefits, decrements, 'maturity_value', 'count_maturity')
            self.df['maturity_outgo'] = values
        else:
            pass

    def annuity_outgo(self, decrements, benefits):
        if 'annuity_value' in self.df:
            values = outgo(self, benefits, decrements, 'annuity_value', 'count_death')
            self.df['annuity_outgo'] = values
        else:
            pass

    def commission_initial(self):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(self.df['init_comm_paid'][step] - self.df['init_comm_clawed_lps'][step])
        self.df['commission_initial'] = values

    def init_comm_paid(self, decrements, expenses):
        values = outgo(self, expenses, decrements, 'init_comm_paid', 'count_live')
        self.df['init_comm_paid'] = values

    def init_comm_clawed_lps(self, decrements, expenses):
        values = outgo(self, expenses, decrements, 'init_comm_clawed_lps', 'count_surrender')
        self.df['init_comm_clawed_lps'] = values

    def commission_renewal(self, decrements, expenses):
        values = outgo(self, expenses, decrements, 'commission_renewal', 'count_live')
        self.df['commission_renewal'] = values

    def expense_initial(self, decrements, expenses):
        values = outgo(self, expenses, decrements, 'expense_initial', 'count_live')
        self.df['expense_initial_if'] = values

    def expense_renewal(self, decrements, expenses):
        values = outgo(self, expenses, decrements, 'expense_renewal', 'count_live')
        self.df['expense_renewal_if'] = values
