from liab.covers.frame import Frame


class Expenses(Frame):
    def __init__(self, valuation_date, policies, policy_number, assumptions, premiums, economic, step_until=50,
                 step_size=1, val=False):
        self.month = policies.look_for('durationif_m', line=policy_number)
        self.age_at_entry = policies.look_for('age_at_entry', line=policy_number)
        self.policies = policies
        self.product_assumptions = assumptions.product_assumptions
        self.commission_initial_m = 34
        self.icl_mdisc_pc = 0.75
        self.ic_recov_pc = 100
        self.typeof_product = self.product_assumptions.look_for('exp ass key',
                                                                label=policies.look_for('product', line=policy_number))
        super().__init__(step_until=step_until, step_size=step_size, month=self.month, age_x=self.age_at_entry,
                         valuation_date=valuation_date)
        if val:
            self.val_expense_renewal_fixed(policy_number, assumptions.expense)
        else:
            self.icl_earn_pp(assumptions.chargescommission, premiums)
            self.icl_disc_pp()
            self.init_comm_paid()
            self.fut_icl_earnl()
            self.init_comm_clawed_lps()
            self.commission_renewal(assumptions.chargescommission, premiums)
            self.expense_initial_fixed(assumptions.expense)
            self.expense_initial_pcprem(assumptions.expense)
            self.expense_initial()
            self.expense_renewal_fixed(economic, assumptions.expense)
            self.expense_renewal_inv_pc(economic, assumptions.expense)
            self.expense_renewal()

    def icl_earn_pp(self, chargescommission, premiums):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            if 0 < self.month + step <= self.commission_initial_m:
                values.append(premiums.df['premium_value'][step] / 100
                              * chargescommission.look_for(label=self.typeof_product, category='init_comm_pc'))
            else:
                values.append(0)
        self.df['icl_earn_pp'] = values

    def icl_disc_pp(self):
        values = ['']
        result = 0
        for step in range(self.step_until - 1, self.step_size - 1, -self.step_size):
            result /= 1 + self.icl_mdisc_pc / 100
            result += self.df['icl_earn_pp'][step]

            values.insert(0, result)
        self.df['icl_disc_pp'] = values

    def init_comm_paid(self):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            if self.month == 1:
                values.append(self.df['icl_disc_pp'][step - 1])
            else:
                values.append(0)
        self.df['init_comm_paid'] = values

    def fut_icl_earnl(self):
        values = [0]
        icl_earn_vector = self.df['icl_earn_pp']
        for step in range(self.step_size, self.step_until, self.step_size):
            result = sum(icl_earn_vector[step::])
            result /= (1 + self.icl_mdisc_pc / 100) ** (step - 1)
            values.insert(len(values) - 1, result)
        self.df['fut_icl_earnl'] = values

    def init_comm_clawed_lps(self):
        values = ['']
        fut_icl_earnl_vector = self.df['fut_icl_earnl']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(fut_icl_earnl_vector[step] * self.ic_recov_pc / 100)
        self.df['init_comm_clawed_lps'] = values

    def commission_renewal(self, chargescommission, premiums):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            if self.commission_initial_m < self.month + step:
                values.append(premiums.df['premium_value'][step] / 100
                              * chargescommission.look_for(label=self.typeof_product, category='ren_comm_pc'))
            else:
                values.append(0)
        self.df['commission_renewal'] = values

    def expense_initial_fixed(self, expense):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            if self.month == 1:
                values.append(expense.look_for(label=self.typeof_product, category='ie_fixed'))
            else:
                values.append(0)
        self.df['expense_initial_fixed'] = values

    def expense_initial_pcprem(self, expense):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            if self.month == 1:
                values.append(expense.look_for(label=self.typeof_product, category='ie_prem_pc'))
            else:
                values.append(0)
        self.df['expense_initial_pcprem'] = values

    def expense_initial(self):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(self.df['expense_initial_pcprem'][step] + self.df['expense_initial_fixed'][step])
        self.df['expense_initial'] = values

    def expense_renewal_fixed(self, economic, expense):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(expense.look_for(label=self.typeof_product, category='re_fixed_y')
                          / 12 * economic.df['index_infl_m'][step])
        self.df['expense_renewal_fixed'] = values

    def expense_renewal_inv_pc(self, economic, expense):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(expense.look_for(label=self.typeof_product, category='re_reserv_pc')
                          / 100 / 12 * economic.df['index_infl_m'][step])  # * disc cashflow, needs to be added later
        self.df['expense_renewal_inv_pc'] = values

    def expense_renewal(self):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(self.df['expense_renewal_fixed'][step] + self.df['expense_renewal_inv_pc'][step])
        self.df['expense_renewal'] = values

    def val_expense_renewal_fixed(self, policy_number, expense):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(expense.look_for(label=self.typeof_product, category='val_re_fixed_y') / 12 *
                          ((1 + self.product_assumptions.look_for('val_infl_pc',
                                                                  label=self.policies.look_for('product',
                                                                                               line=policy_number)) / 100) ** (
                                   1 / 12)) ** step)
        self.df['expense_renewal_fixed'] = values

    def val_expense_renewal_inv_pc(self, policy_number, expense):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            pass
