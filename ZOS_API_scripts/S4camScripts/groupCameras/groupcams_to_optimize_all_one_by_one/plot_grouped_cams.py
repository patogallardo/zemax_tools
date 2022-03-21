import hexlattice
import pandas as pd
import numpy as np

df = pd.read_csv('85cam_groups.csv')
hexlattice.plot_df(df, 100*2/np.sqrt(3), show=False)
