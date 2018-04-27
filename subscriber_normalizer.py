import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = pd.read_csv("subreddits.csv", index_col=0)

data["norm_subs"] = np.maximum(1, np.power(data.Subscribers, 0.5) / 100)
data.describe()

fig, axs = plt.subplots()
axs.hist(data["norm_subs"], bins=100)
plt.show()

# data.to_csv("normed_subs.csv")
