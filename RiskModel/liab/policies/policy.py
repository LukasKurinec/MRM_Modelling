class Policy:
    def __init__(self, policy_number, age_at_entry, sex, pol_term_y, prem_paybl_y, prem_freq, annual_prem, single_prem,
                 sum_assured, init_pols_if, init_netprem, init_decb_if, durationif_m, exp_ass_key, charges_and_comm_key,
                 surrpen_key, lps_ass_key, tbl_mort_key, percent_tbl_mort, death_value, surr_value, maturity_value,
                 annuity_value, critical_illness_value):
        self.policy_number = policy_number
        self.age_at_entry = age_at_entry
        self.sex = sex
        self.pol_term_y = pol_term_y
        self.prem_paybl_y = prem_paybl_y
        self.prem_freq = prem_freq
        self.annual_prem = annual_prem
        self.single_prem = single_prem
        self.sum_assured = sum_assured
        self.init_pols_if = init_pols_if
        self.init_netprem = init_netprem
        self.init_decb_if = init_decb_if
        self.durationif_m = durationif_m
        self.exp_ass_key = exp_ass_key
        self.charges_and_comm_key = charges_and_comm_key
        self.surrpen_key = surrpen_key
        self.lps_ass_key = lps_ass_key
        self.tbl_mort_key = tbl_mort_key
        self.percent_tbl_mort = percent_tbl_mort
        self.death_value = death_value
        self.surr_value = surr_value
        self.maturity_value = maturity_value
        self.annuity_value = annuity_value
        self.critical_illness_value = critical_illness_value


