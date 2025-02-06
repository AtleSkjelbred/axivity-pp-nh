import pandas as pd


def filter_dataframe(df, settings):
    df = filter_predictions(df, settings)
    return df


def filter_predictions(df: pd.DataFrame, settings: dict) -> pd.DataFrame:

    df[settings['act_column']] = df[settings['act_column']].replace([2, 4, 5, 13, 14, 130, 140], 1)

    for i in df.index[df[settings['act_column']] == 10].tolist():
        df.at[i, settings['act_column']] = 6

    for i in df.index[df[settings['act_column']] == 3].tolist():
        try:
            if df[settings['act_column']][i - 1] == 1 and df[settings['act_column']][i + 1] == 1:
                df.at[i, settings['act_column']] = 1
            else:
                df.at[i, settings['act_column']] = 6
        except KeyError:
            df.at[i, settings['act_column']] = 6

    df[settings['ai_column']] = ['I' if i == 7 or i == 8 else 'A' for i in df[settings['act_column']]]

    return df


def filter_days(df, index, settings, epd):

    conditions = [(settings['nw_column'], 1, 1)]

    keys_to_delete = set()
    for day, (start, end) in index.items():
        if (end - start) != epd:
            keys_to_delete.add(day)
        for con in conditions:

            if (df[con[0]][start:end].values == con[1]).sum() < ((end - start) * con[2]):
                keys_to_delete.add(day)
                break

    for day in keys_to_delete:
        del index[day]

    return df
    