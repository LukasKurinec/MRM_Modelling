from liab.covers.frame import Frame


class DiscountedCfs(Frame):
    def __init__(self, valuation_date, policies, policy_number, economic, cfs, step_until=50, step_size=1):
        self.month = policies.look_for('durationif_m', line=policy_number)
        self.age_at_entry = policies.look_for('age_at_entry', line=policy_number)
        self.economic = economic
        self.cfs = cfs
        super().__init__(step_until=step_until, step_size=step_size, month=self.month, age_x=self.age_at_entry,
                         valuation_date=valuation_date)

        self.proj_term_horizon = 40
        self.pv_premium_income(economic, cfs)
        self.pv_death_outgo(economic, cfs)
        self.pv_surrender_outgo(economic, cfs)
        self.pv_maturity_outgo(economic, cfs)
        self.pv_annuity_outgo(economic, cfs)
        self.pv_commission_initial(economic, cfs)
        self.pv_commission_renewal(economic, cfs)
        self.pv_expense_initial_if(economic, cfs)
        self.pv_expense_renewal_if(economic, cfs)
        self.bel()

    def pv_premium_income(self, economic, cfs):
        pv_premium_income = [0]
        result = 0
        for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
            result /= 1 + economic.look_for('forw_rate_m', index=step - 1)
            result += cfs.look_for('premiums_income', index=step)
            pv_premium_income.insert(0, result)
        self.df['pv_premium_income'] = pv_premium_income

    def pv_death_outgo(self, economic, cfs):
        pv_death_outgo = [0]
        result = 0
        for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
            result += cfs.look_for('death_outgo', index=step)
            result /= (1 + economic.look_for('forw_rate_m', index=step - 1))
            pv_death_outgo.insert(0, result)
        self.df['pv_death_outgo'] = pv_death_outgo

    def pv_surrender_outgo(self, economic, cfs):
        if 'surrender_outgo' in self.df:
            pv_surrender_outgo = [0]
            result = 0
            for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
                result += cfs.look_for('surrender_outgo', index=step)
                result /= (1 + economic.look_for('forw_rate_m', index=step - 1))
                pv_surrender_outgo.insert(0, result)
            self.df['pv_surrender_outgo'] = pv_surrender_outgo
        else:
            pass

    def pv_maturity_outgo(self, economic, cfs):
        if 'maturity_outgo' in self.df:
            pv_maturity_outgo = [0]
            result = 0
            for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
                result += cfs.look_for('maturity_outgo', index=step)
                result /= (1 + economic.look_for('forw_rate_m', index=step - 1))
                pv_maturity_outgo.insert(0, result)
            self.df['pv_maturity_outgo'] = pv_maturity_outgo
        else:
            pass

    def pv_annuity_outgo(self, economic, cfs):
        if 'annuity_outgo' in self.df:
            pv_annuity_outgo = [0]
            result = 0
            for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
                result += cfs.look_for('annuity_outgo', index=step)
                result /= (1 + economic.look_for('forw_rate_m', index=step - 1))
                pv_annuity_outgo.insert(0, result)
            self.df['pv_annuity_outgo'] = pv_annuity_outgo
        else:
            pass

    def pv_commission_initial(self, economic, cfs):
        pv_commission_initial = [0]
        result = 0
        for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
            result /= 1 + economic.look_for('forw_rate_m', index=step - 1)
            result += cfs.look_for('commission_initial', index=step)
            pv_commission_initial.insert(0, result)
        self.df['pv_commission_initial'] = pv_commission_initial

    def pv_commission_renewal(self, economic, cfs):
        pv_commission_renewal = [0]
        result = 0
        for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
            result /= 1 + economic.look_for('forw_rate_m', index=step - 1)
            result += cfs.look_for('commission_renewal', index=step)
            pv_commission_renewal.insert(0, result)
        self.df['pv_commission_renewal'] = pv_commission_renewal

    def pv_expense_initial_if(self, economic, cfs):
        pv_expense_initial_if = [0]
        result = 0
        for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
            result /= 1 + economic.look_for('forw_rate_m', index=step - 1)
            result += cfs.look_for('expense_initial_if', index=step)
            pv_expense_initial_if.insert(0, result)
        self.df['pv_expense_initial_if'] = pv_expense_initial_if

    def pv_expense_renewal_if(self, economic, cfs):
        pv_expense_renewal_if = [0]
        result = 0
        for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
            result /= 1 + economic.look_for('forw_rate_m', index=step - 1)
            result += cfs.look_for('expense_renewal_if', index=step)
            pv_expense_renewal_if.insert(0, result)
        self.df['pv_expense_renewal_if'] = pv_expense_renewal_if

    def bel(self):
        values = []
        for step in range(self.step_until - 1, self.step_size - 2, -self.step_size):
            result = - self.df['pv_premium_income'][step]
            result += self.df['pv_death_outgo'][step]
            result += self.df['pv_surrender_outgo'][step] if 'pv_surrender_outgo' in self.df else 0
            result += self.df['pv_maturity_outgo'][step] if 'pv_maturity_outgo' in self.df else 0
            result += self.df['pv_annuity_outgo'][step] if 'pv_annuity_outgo' in self.df else 0
            result += self.df['pv_commission_initial'][step]
            result += self.df['pv_commission_renewal'][step]
            result += self.df['pv_expense_initial_if'][step]
            result += self.df['pv_expense_renewal_if'][step]
            values.insert(0, result)
        self.df['bel'] = values
