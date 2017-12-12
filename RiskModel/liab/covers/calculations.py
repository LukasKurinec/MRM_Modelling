from liab.general import look_for_in_df
import math

"""
USED IN DECREMENTS CALCULATION
"""


def qx(self, policy_number, tbl_key, percent_tbl, sex, smoker):
    values = ['']
    previous_age_x = look_for_in_df(self.df, 'age_x', 0)
    for step in range(self.step_size, self.step_until, self.step_size):
        reference = self.mortality.look_for(
            str(self.product_assumptions.look_for(tbl_key,
                                                  label=self.policies.look_for('product', line=policy_number))).lower()
            + str(int(self.policies.look_for(sex, line=policy_number)))
            + str(self.policies.look_for(smoker, line=policy_number))
            , index=previous_age_x
        )
        values.append(float(reference) *
                      self.product_assumptions.look_for(percent_tbl, label=self.policies.look_for('product',
                                                                                                  line=policy_number)) / 100)
        previous_age_x = look_for_in_df(self.df, 'age_x', step)
    return values


def qx_m(self, qx):
    values = ['']
    for step in range(self.step_size, self.step_until, self.step_size):
        values.append(1 - pow(1 - look_for_in_df(self.df, qx, step), 1 / 12))
    return values


def pm_x(self, qx_m):
    values = [1]
    last_value = 1
    for step in range(self.step_size, self.step_until, self.step_size):
        if str(look_for_in_df(self.df, qx_m, step)) == 'nan':
            values.append(last_value)
        else:
            values.append(last_value * (1 - look_for_in_df(self.df, qx_m, step)))
        last_value = values[step]
    return values


"""
USED IN ECONOMIC CALCULATIONS
"""


def spot_m(self, economic, column, proj_term_horizon, additional_parameter=0):
    # last updated for prototype v0.04 @ 12/7/17
    values = ['']
    for step in range(self.step_size, self.step_until, self.step_size):
        if step < proj_term_horizon * 12:
            values.append(pow(1 + economic.look_for(column, line=math.trunc((step + 11) / 12)) + additional_parameter,
                              1 / 12) - 1)
        else:
            values.append(0)
    return values


def forw_m(self, column):
    # last updated for prototype v0.04 @ 12/5/17
    values = [0, look_for_in_df(self.df, column, 1)]
    last_value = pow(values[1] + 1, 1)
    for step in range(self.step_size + 1, self.step_until, self.step_size):
        values.append((pow(look_for_in_df(self.df, column, step) + 1, step) / last_value) - 1)
        last_value = pow(look_for_in_df(self.df, column, step) + 1, step)
    return values


"""
USED IN CFS CALCULATIONS
"""


def outgo(self, module1, module2, column1, column2):
    # last updated for prototype v0.03 @ 12/5/17
    values = ['']
    for step in range(self.step_size, self.step_until, self.step_size):
        if step < self.proj_term_horizon * 12:
            values.append(module1.look_for(column1, index=step)
                          * module2.look_for(column2, index=step if column2 != 'count_live' else step - 1))
        else:
            values.append(0)
    return values


"""
USED IN FUND & BENEFITS
"""


def fund_and_benefits_circle(self, chargescommission, product_features, product_assumptions, policies, policy_number,
                             economic):
    print("I'm here")
    risk_charge = [0]
    accumulation_account_post_dedn = [0]
    return_on_accumulation_account = [0]
    asset_management_charge = [0]
    print(policies.look_for('fund_value_acc_init', line=policy_number))
    accumulation_account = [float(policies.look_for('fund_value_acc_init', line=policy_number)) *
                            (1 + chargescommission.look_for(label=self.typeof_charges, category='amc_pc') / 12)]
    accumulation_account_pre_dedn = [float(policies.look_for('fund_value_acc_init', line=policy_number))]
    '''death value pre dedn'''
    if product_features.look_for('death value  (y/n)',
                                 label=policies.look_for('product', line=policy_number)) == 0:
        death_value_pre_dedn = [0]
        death_sar_pre_dedn = [0]
    elif product_features.look_for('death value  (y/n)',
                                   label=policies.look_for('product', line=policy_number)).lower() == 'sum_assured':
        death_value_pre_dedn = [policies.look_for('sum_assured', line=policy_number)]
        death_sar_pre_dedn = [death_value_pre_dedn[0]
                              - self.df['capital_fund_value'][0] - max(0, accumulation_account_pre_dedn[0])]
    else:
        death_value_pre_dedn = [max(policies.look_for('sum_assured', line=policy_number),
                                    self.df['capital_fund_value'][0] + max(0, accumulation_account_pre_dedn[0]))]
        death_sar_pre_dedn = [death_value_pre_dedn[0]
                              - self.df['capital_fund_value'][0] - max(0, accumulation_account_pre_dedn[0])]

    '''critical illness value pre dedn'''
    if product_features.look_for('unit linked (y/n)',
                                 label=policies.look_for('product', line=policy_number)) == 0:
        critical_illness_value_pre_dedn = [0]
    elif product_features.look_for('critical illness (y/n)',
                                   label=policies.look_for('product', line=policy_number)) == 0:
        critical_illness_value_pre_dedn = [0]
    elif product_features.look_for('critical illness (y/n)',
                                   label=policies.look_for('product', line=policy_number)) > 0:
        critical_illness_value_pre_dedn = [policies.look_for('sum_assured_ci', line=policy_number)
                                           - policies.look_for('sum_assured', line=policy_number)]
    else:
        critical_illness_value_pre_dedn = [max(policies.look_for('sum_assured_ci', line=policy_number),
                                               self.df['capital_fund_value'][0] + max(0,
                                                                                      accumulation_account_pre_dedn[0]))
                                           - max(policies.look_for('sum_assured', line=policy_number),
                                                 self.df['capital_fund_value'][0] + max(0,
                                                                                        accumulation_account_pre_dedn[
                                                                                            0]))]

    '''Starting the for cycle'''
    for step in range(self.step_size, self.step_until, self.step_size):
        accumulation_account_pre_dedn.append(self.df['accumulation_allocation_premium'][step] +
                                             accumulation_account[step - 1])
        '''death value pre dedn'''
        if product_features.look_for('death value  (y/n)',
                                     label=policies.look_for('product', line=policy_number)) == 0:
            death_value_pre_dedn.append(0)
            death_sar_pre_dedn.append(0)
        elif product_features.look_for('death value  (y/n)',
                                       label=policies.look_for('product',
                                                               line=policy_number)).lower() == 'sum_assured':
            death_value_pre_dedn.append(policies.look_for('sum_assured', line=policy_number))
            death_sar_pre_dedn.append(death_value_pre_dedn[step]
                                      - self.df['capital_fund_value'][step] - max(0, accumulation_account_pre_dedn[step]))
        else:
            death_value_pre_dedn.append(max(policies.look_for('sum_assured', line=policy_number),
                                            self.df['capital_fund_value'][step] + max(0,
                                                                                    accumulation_account_pre_dedn[step])))
            death_sar_pre_dedn.append(death_value_pre_dedn[0]
                                      - self.df['capital_fund_value'][step] - max(0, accumulation_account_pre_dedn[step]))

        '''critical illness value pre dedn & death sar pre dedn'''
        if product_features.look_for('unit linked (y/n)',
                                     label=policies.look_for('product', line=policy_number)) == 0:
            critical_illness_value_pre_dedn.append(0)
        elif product_features.look_for('critical illness (y/n)',
                                       label=policies.look_for('product', line=policy_number)) == 0:
            critical_illness_value_pre_dedn.append(0)
        elif product_features.look_for('critical illness (y/n)',
                                       label=policies.look_for('product',
                                                               line=policy_number)) > 0:
            critical_illness_value_pre_dedn.append(policies.look_for('sum_assured_ci', line=policy_number)
                                                   - policies.look_for('sum_assured', line=policy_number))
        else:
            critical_illness_value_pre_dedn.append(max(policies.look_for('sum_assured_ci', line=policy_number),
                                                       self.df['capital_fund_value'][step] + max(0,
                                                                                              accumulation_account_pre_dedn[
                                                                                                  step]))
                                                   - max(policies.look_for('sum_assured', line=policy_number),
                                                         self.df['capital_fund_value'][step] + max(0,
                                                                                                accumulation_account_pre_dedn[
                                                                                                    step])))

        '''other fund columns'''
        risk_charge.append(0 * death_sar_pre_dedn[step] + 0 * critical_illness_value_pre_dedn[step]) #TODO:imple decrements
        accumulation_account_post_dedn.append(accumulation_account_pre_dedn[step] - risk_charge[step]
                                              - self.df['fix_admin_exp_charge'][step])
        return_on_accumulation_account.append(max(0, accumulation_account_post_dedn[step])
                                              * economic.df['forw_rate_m'][step]
                                              * 1 - product_assumptions.look_for('tax_pc_invinc_polholder',
                                                                                 label=policies.look_for('product',
                                                                                                         line=policy_number)))
        asset_management_charge.append(chargescommission.look_for(label=self.typeof_charges, category='ren_fchga_pc')
                                       / 12 * (accumulation_account_post_dedn[step] + return_on_accumulation_account[
            step]))
        accumulation_account.append(accumulation_account_post_dedn[step] + return_on_accumulation_account[step]
                                    + asset_management_charge[step])
    return death_value_pre_dedn, critical_illness_value_pre_dedn, death_sar_pre_dedn, accumulation_account_pre_dedn, \
           risk_charge, accumulation_account_post_dedn, return_on_accumulation_account, asset_management_charge, \
           accumulation_account
