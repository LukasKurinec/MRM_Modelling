from liab.covers.frame import Frame
from liab.covers.calculations import spot_m
from liab.covers.calculations import forw_m
from liab.general import look_for_in_df


class Economic(Frame):
    def __init__(self, valuation_date, policies, policy_number, assumptions, step_until=50, step_size=1):
        self.month = policies.look_for('durationif_m', line=policy_number)
        self.age_at_entry = policies.look_for('age_at_entry', line=policy_number)
        self.product_assumptions = assumptions.product_assumptions
        super().__init__(step_until=step_until, step_size=step_size, month=self.month, age_x=self.age_at_entry,
                         valuation_date=valuation_date)
        self.typeof_expense \
            = self.product_assumptions.look_for('exp ass key', label=policies.look_for('product', line=policy_number))
        self.typeof_charges \
            = self.product_assumptions.look_for('charges&comm key',
                                                label=policies.look_for('product', line=policy_number))
        self.proj_term_horizon = 40
        self.spot_rate_m(assumptions.economic)
        self.forw_rate_m()
        self.disc_factor_m()
        self.spot_infl_m(assumptions.economic)
        self.forw_infl_m()
        self.index_infl_m()
        self.spot_infl_m_ren_exp(assumptions.expense, assumptions.economic)
        self.forw_infl_m_ren_exp()
        self.index_infl_m_ren_exp()
        self.spot_infl_m_exp_dedn(assumptions.chargescommission, assumptions.economic)
        self.forw_infl_m_exp_dedn()
        self.index_infl_m_exp_dedn()

    def spot_rate_m(self, economic):
        values = spot_m(self, economic, 'spot rates', self.proj_term_horizon)
        self.df['spot_rate_m'] = values

    def forw_rate_m(self):
        values = forw_m(self, 'spot_rate_m')
        self.df['forw_rate_m'] = values

    def disc_factor_m(self):
        values = [1]
        last_value = values[0]
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(last_value / (1 + look_for_in_df(self.df, 'spot_rate_m', step)))
            last_value = values[step]
        self.df['disc_factor_m'] = values

    def spot_infl_m(self, economic):
        values = spot_m(self, economic, 'spot inflation', self.proj_term_horizon)
        self.df['spot_infl_m'] = values

    def forw_infl_m(self):
        values = forw_m(self, 'spot_infl_m')
        self.df['forw_infl_m'] = values

    def index_infl_m(self):
        values = [1]
        result = 1
        for step in range(self.step_size, self.step_until, self.step_size):
            result *= (1 + look_for_in_df(self.df, 'forw_infl_m', step))
            values.append(result)
        self.df['index_infl_m']=values

    def spot_infl_m_ren_exp(self, expenses, economic):
        values = spot_m(self, economic, 'spot inflation', self.proj_term_horizon,
                        expenses.look_for(label=self.typeof_expense, category='re_inflat_pc')/100)
        self.df = self.df.assign(spot_infl_m_ren_exp=values)

    def forw_infl_m_ren_exp(self):
        values = forw_m(self, 'spot_infl_m_ren_exp')
        self.df = self.df.assign(forw_infl_m_ren_exp=values)

    def index_infl_m_ren_exp(self):
        values = [1]
        result = 1
        for step in range(self.step_size, self.step_until, self.step_size):
            result *= (1 + look_for_in_df(self.df, 'forw_infl_m_ren_exp', step))
            values.append(result)
        self.df = self.df.assign(index_infl_m_ren_exp=values)

    def spot_infl_m_exp_dedn(self, chargescommission, economic):
        values = spot_m(self, economic, 'spot inflation', self.proj_term_horizon,
                        chargescommission.look_for(label=self.typeof_charges, category='fdedn_inf_pc')/100)
        self.df = self.df.assign(spot_infl_m_exp_dedn=values)

    def forw_infl_m_exp_dedn(self):
        values = forw_m(self, 'spot_infl_m_exp_dedn')
        self.df = self.df.assign(forw_infl_m_exp_dedn=values)

    def index_infl_m_exp_dedn(self):
        values = [1]
        result = 1
        for step in range(self.step_size, self.step_until, self.step_size):
            result *= (1 + look_for_in_df(self.df, 'forw_infl_m_exp_dedn', step))
            values.append(result)
        self.df = self.df.assign(index_infl_m_exp_dedn=values)
