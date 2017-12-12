inputs = {'mortality':
              {'filename': 'mortality'},
          'economic':
              {'filename': 'economic',
               'separator': ','},
          'expense':
              {'filename': 'expense',
               'separator': ',',
               'index_col': 0},
          'persistency':
              {'filename': 'persistency',
               'separator': ',',
               'index_col': (0, 1)},
          'surrpenalties':
              {'filename': 'surrpenalties',
               'separator': ',',
               'index_col': 0},
          'chargescommission':
              {'filename': 'chargescommission',
               'separator': ',',
               'index_col': 0},
          }

# for key, value in inputs.items():
#     if key.lower() == 'mortality':
#         print(value.get('index_col'))
#         value.keys()

# def do(arg=0):
#     print(arg)

# do()

import pandas as pd
df = pd.DataFrame()
df['name'] = ['John', 'Steve', 'Sarah']
df['age'] = [31, 32, 19]

# df.loc[3] = ['Lisa', 6]
df.insert(2, 'status', ['m', 's', 's'])

df['smoker'] = ['n', 'y', 'y']

print(df)
