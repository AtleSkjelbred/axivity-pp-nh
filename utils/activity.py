def count_codes(df, start, end, column, code):
    return (df[column][start:end].values == code).sum()


def get_activities(df, index, codes, column):
    temp = {}

    for day, (start, end) in index.items():
        temp[day] = {}

        for code in codes:
            temp[day][code] = count_codes(df, start, end, column, code)

    return temp
