import pandas as pd
import os

def get_data(code):
    df = pd.read_csv(f"blog/stock_price/{code}.csv")
    data = df.head()
    data = data.to_html()
    return data
