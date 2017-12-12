from liab.policies.policies import Policies
from liab.assumptions.assumptions import Assumptions
from liab.covers.liabilitycalculations import LiabilityCalculations
import liab.utility as utility

inputs = utility.timeit_start()
myPoli = Policies()
# print(myPoli.df)
myAssum = Assumptions()
# print(myAssum.product_assumptions.df)
utility.timeit_stop(inputs, 'Gathering input tables')

calcs = utility.timeit_start()
myCalc = LiabilityCalculations(myPoli, 3, myAssum, 'date', step_until=50)
utility.timeit_stop(calcs, 'Calculation')

print('Writing output to console:\n', myCalc.benefits.df)
# myCalc.all_to_excel()
utility.timeit_stop(inputs, 'Everything')
