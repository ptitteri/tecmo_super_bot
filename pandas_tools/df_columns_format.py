import pandas as pd

def pandas_df_format(df):

    df.columns = map(str.lower,df.columns)
    df.columns = df.columns.str.strip()
    df.columns = [x.replace(',','_') for x in df.columns]
    df.columns = [x.replace('/', '_') for x in df.columns]
    df.columns = [x.replace('(', '_') for x in df.columns]
    df.columns = [x.replace(')', '_') for x in df.columns]
    df.columns = [x.replace('+', '_') for x in df.columns]
    df.columns = [x.replace(' ', '_') for x in df.columns]

    for i in df.columns:
        try:
            df[i] = df[i].str.replace(',','')
        except:
            continue

    return df