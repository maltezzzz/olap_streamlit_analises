import pandas as pd

class OlapEngine:

    def __init__(self, df):
        self.df = df

    def pivot(self, index, columns, values, aggfunc):
        return pd.pivot_table(
            self.df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        )
