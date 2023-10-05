import matplotlib.pyplot as plt
from pandas import DataFrame


def plt_df(df: DataFrame):
    df.plot(kind="line")
    plt.xlabel("Time frame")
    plt.legend(loc="best")
    plt.show()
