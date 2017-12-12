from liab.covers.frame import Frame
from liab.general import look_for_in_df
from liab.general import blockPrint, enablePrint
from liab.covers.calculations import qx
from liab.covers.calculations import qx_m
from liab.covers.calculations import pm_x
import math


class Decrements(Frame):
    def __init__(self, valuation_date, policies, policy_number, assumptions, column_titles, step_until=50, step_size=1):
        self.month = policies.look_for('durationif_m', line=policy_number)
        self.age_at_entry = policies.look_for('age_at_entry', line=policy_number)
        self.mortality = assumptions.mortality
        self.policies = policies
        self.product_assumptions = assumptions.product_assumptions
        self.product_features = assumptions.product_features
        super().__init__(step_until=step_until, step_size=step_size, month=self.month, age_x=self.age_at_entry,
                         valuation_date=valuation_date)

        self.tbl_mort_key = column_titles[0]
        self.percent_tbl_mort = column_titles[1]
        self.lps_ass_key = column_titles[2]
        self.tbl_ci_key = column_titles[3]
        self.percent_tbl_ci = column_titles[4]
        self.surrender_timing = 0.5

        self.qx(policy_number)
        self.qx_m()
        self.pm_x()
        if self.product_features.look_for('joint life (y/n)',
                                          label=self.policies.look_for('product', line=policy_number)) > 0:
            self.qx2(policy_number)
            self.qx2_m()
            self.pm2_x()
            self.qx12_fd_m()
            self.qx12_sd_m()
        if self.product_features.look_for('critical illness (y/n)',
                                          label=self.policies.look_for('product', line=policy_number)) > 0:
            self.qx_ci(policy_number)
            self.qx_ci_m()
        self.surr_percent(policy_number, assumptions.persistency)
        self.surr_percent_m()
        self.part_percent(policy_number, assumptions.persistency)
        self.part_percent_m()
        self.paidup_percent(policy_number, assumptions.persistency)
        self.paidup_percent_m()
        self.count_live(policy_number)

    def qx(self, policy_number):
        values = qx(self, policy_number, self.tbl_mort_key, self.percent_tbl_mort, 'sex', 'smoker_stat')
        self.df['qx'] = values

    def qx_m(self):
        values = qx_m(self, 'qx')
        self.df['qx_m'] = values

    def pm_x(self):
        values = pm_x(self, 'qx_m')
        self.df['pm_x'] = values

    def qx2(self, policy_number):
        values = qx(self, policy_number, self.tbl_mort_key, self.percent_tbl_mort, 'sex2', 'smoker2_stat')
        self.df['qx2'] = values

    def qx2_m(self):
        values = qx_m(self, 'qx2')
        self.df['qx2_m'] = values

    def pm2_x(self):
        values = pm_x(self, 'qx2_m')
        self.df['pm2_x'] = values

    def qx12_fd_m(self):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(look_for_in_df(self.df, 'qx_m', step) + look_for_in_df(self.df, 'qx2_m', step)
                          - look_for_in_df(self.df, 'qx_m', step) * look_for_in_df(self.df, 'qx2_m', step))
        self.df['qx12_fd_m'] = values

    def qx12_sd_m(self):
        step_for_calc = 11
        values = ['']
        previous_calc = look_for_in_df(self.df, 'pm_x', 0) + look_for_in_df(self.df, 'pm2_x', 0) \
                        - look_for_in_df(self.df, 'pm_x', 0) * look_for_in_df(self.df, 'pm2_x', 0)
        blockPrint()
        for step in range(self.step_size, self.step_until, self.step_size):
            try:
                values.append(1 - ((look_for_in_df(self.df, 'pm_x', step + step_for_calc)
                                    + look_for_in_df(self.df, 'pm2_x', step + step_for_calc)
                                    - look_for_in_df(self.df, 'pm_x', step + step_for_calc)
                                    * look_for_in_df(self.df, 'pm2_x', step + step_for_calc)) / previous_calc))
                previous_calc = look_for_in_df(self.df, 'pm_x', step) + look_for_in_df(self.df, 'pm2_x', step) \
                                - look_for_in_df(self.df, 'pm_x', step) * look_for_in_df(self.df, 'pm2_x', step)
            except KeyError:
                values.append(1)
            except TypeError:
                values.append(1)
        enablePrint()
        self.df['qx12_sd_m'] = values

    # yearly critical illness rate
    def qx_ci(self, policy_number):
        values = qx(self, policy_number, self.tbl_ci_key, self.percent_tbl_ci, 'sex', 'smoker_stat')
        self.df['qx_ci'] = values

    # monthly critical illness rate
    def qx_ci_m(self):
        values = qx_m(self, 'qx_ci')
        self.df['qx_ci_m'] = values

    def surr_percent(self, policy_number, persistency):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(persistency.look_for(str(math.floor(look_for_in_df(self.df, 'month', step - 1) / 12)), label=(
                self.product_assumptions.look_for(self.lps_ass_key,
                                                  label=self.policies.look_for('product', line=policy_number)),
                'Surrender')) / 100)
        self.df['surr_percent'] = values

    def surr_percent_m(self):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(1 - pow(1 - look_for_in_df(self.df, 'surr_percent', step), 1 / 12))
        self.df['surr_percent_m'] = values

    def part_percent(self, policy_number, persistency):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(persistency.look_for(str(math.floor(look_for_in_df(self.df, 'month', step - 1) / 12)), label=(
                self.product_assumptions.look_for(self.lps_ass_key,
                                                  label=self.policies.look_for('product', line=policy_number)),
                'Partial')) / 100)
        self.df['part_percent'] = values

    def part_percent_m(self):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(1 - pow(1 - look_for_in_df(self.df, 'part_percent', step), 1 / 12))
        self.df['part_percent_m'] = values

    def paidup_percent(self, policy_number, persistency):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(persistency.look_for(str(math.floor(look_for_in_df(self.df, 'month', step - 1) / 12)), label=(
                self.product_assumptions.look_for(self.lps_ass_key,
                                                  label=self.policies.look_for('product', line=policy_number)),
                'PUP')) / 100)
        self.df['paidup_percent'] = values

    def paidup_percent_m(self):
        values = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            values.append(1 - pow(1 - look_for_in_df(self.df, 'paidup_percent', step), 1 / 12))
        self.df['paidup_percent_m'] = values

    def count_live(self, policy_number):
        count_live = [1.0]
        last_count_live = count_live[0]
        count_death = ['']
        count_surrender = ['']
        count_paidup = ['']
        count_critical_illness = ['']
        count_maturity = ['']
        for step in range(self.step_size, self.step_until, self.step_size):
            if self.product_features.look_for('joint life (y/n)',
                                              label=self.policies.look_for('product', line=policy_number)) == 1:
                count_death.append(last_count_live
                                   * (1 - look_for_in_df(self.df, 'surr_percent_m', step) * self.surrender_timing)
                                   * (1 - look_for_in_df(self.df, 'paidup_percent_m', step) * self.surrender_timing)
                                   * look_for_in_df(self.df, 'qx12_fd_m', step))
                count_surrender.append(last_count_live
                                       * (1 - look_for_in_df(self.df, 'qx12_fd_m', step) * self.surrender_timing)
                                       * (1 - look_for_in_df(self.df, 'paidup_percent_m', step) * self.surrender_timing)
                                       * look_for_in_df(self.df, 'surr_percent_m', step))
            elif self.product_features.look_for('joint life (y/n)',
                                                label=self.policies.look_for('product', line=policy_number)) == 2:
                count_death.append(last_count_live
                                   * (1 - look_for_in_df(self.df, 'surr_percent_m', step) * self.surrender_timing)
                                   * (1 - look_for_in_df(self.df, 'paidup_percent_m', step) * self.surrender_timing)
                                   * look_for_in_df(self.df, 'qx12_sd_m', step))
                count_surrender.append(last_count_live
                                       * (1 - look_for_in_df(self.df, 'qx12_sd_m', step) * self.surrender_timing)
                                       * (1 - look_for_in_df(self.df, 'paidup_percent_m', step) * self.surrender_timing)
                                       * look_for_in_df(self.df, 'surr_percent_m', step))
            else:
                count_death.append(last_count_live
                                   * (1 - look_for_in_df(self.df, 'surr_percent_m', step) * self.surrender_timing)
                                   * (1 - look_for_in_df(self.df, 'paidup_percent_m', step) * self.surrender_timing)
                                   * look_for_in_df(self.df, 'qx_m', step))
                count_surrender.append(last_count_live
                                       * (1 - look_for_in_df(self.df, 'qx_m', step) * self.surrender_timing)
                                       * (1 - look_for_in_df(self.df, 'paidup_percent_m', step) * self.surrender_timing)
                                       * look_for_in_df(self.df, 'surr_percent_m', step))

            count_paidup.append(last_count_live
                                * (1 - look_for_in_df(self.df, 'surr_percent_m', step) / 2)
                                * (1 - look_for_in_df(self.df, 'qx_m', step) / 2)
                                * look_for_in_df(self.df, 'paidup_percent_m', step))

            if self.product_features.look_for('critical illness (y/n)',
                                              label=self.policies.look_for('product', line=policy_number)) > 0:
                count_critical_illness.append(last_count_live
                                              * (1 - look_for_in_df(self.df, 'surr_percent_m', step) / 2)
                                              * (1 - look_for_in_df(self.df, 'qx_m', step) / 2)
                                              * (1 - look_for_in_df(self.df, 'paidup_percent_m', step) / 2)
                                              * look_for_in_df(self.df, 'qx_ci_m', step))
            elif self.product_features.look_for('critical illness (y/n)',
                                                label=self.policies.look_for('product', line=policy_number)) == 0:
                pass

            if self.month == self.policies.look_for('pol_term_y', line=policy_number) * 12:
                count_maturity.append(count_live[step])
            else:
                pass

            count_live_value = last_count_live
            count_live_value -= count_surrender[step]
            count_live_value -= count_death[step]
            if self.product_features.look_for('critical illness (y/n)',
                                              label=self.policies.look_for('product', line=policy_number)) > 0:
                count_live_value -= count_critical_illness[step]
            if self.month == self.policies.look_for('pol_term_y', line=policy_number) * 12:
                count_live_value -= count_maturity[step]
            count_live_value -= count_paidup[step]

            count_live.append(count_live_value)
            last_count_live = count_live[step]

        self.df['count_surrender'] = count_surrender
        self.df['count_death'] = count_death
        if self.product_features.look_for('critical illness (y/n)',
                                          label=self.policies.look_for('product', line=policy_number)) > 0:
            self.df['count_critical_illness'] = count_critical_illness
        if self.month == self.policies.look_for('pol_term_y', line=policy_number) * 12:
            self.df['count_maturity'] = count_maturity
        self.df['count_paidup'] = count_paidup
        self.df['count_live'] = count_live
