from liab.covers.frame import Frame
from liab.general import look_for_in_df
import math


class Premium(Frame):
    def __init__(self, valuation_date, policies, policy_number, step_until=50, step_size=1):
        self.month = policies.look_for('durationif_m', line=policy_number)
        self.age_at_entry = policies.look_for('age_at_entry', line=policy_number)
        self.frequencyof_premium = policies.look_for('prem_freq', line=policy_number)
        self.premium_pa = policies.look_for('annual_prem', line=policy_number)
        self.payable_premium_y = policies.look_for('prem_paybl_y', line=policy_number)
        super().__init__(step_until=step_until, step_size=step_size, month=self.month, age_x=self.age_at_entry,
                         valuation_date=valuation_date)
        self.premium()

    def premium(self):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            if 0 < self.month + step <= self.payable_premium_y * 12:
                if (self.month + step) % (12 / self.frequencyof_premium) == 0:
                    values.append(self.premium_pa / self.frequencyof_premium)
                else:
                    values.append(0)
            else:
                values.append(0)

        self.df['premium_value'] = values
