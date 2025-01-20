def get_bouts(df, index, epm, settings):
    temp = {}
    for day, (start, end) in index.items():
        temp[day] = count_bouts(df, start, end, epm, settings)

    return temp


def count_bouts(df, start, end, epm, settings):
    column = settings['act_column']
    codes = settings['bout_codes']
    max_noise = settings['noise_threshold']

    temp = {key: [] for key in codes}
    selected_values = df[column].iloc[start:end]

    if df[column][start] in codes:
        current_code = df[column][start]
    else:
        current_code = df[column][start + skip(df, start, codes, column)]
    length, noise = 0, 0

    for i, value in selected_values.items():
        if value != current_code:
            epoch_gap = find_next(df, current_code, i, column)
            if (length < 20 and epoch_gap < 2) or (length > 20 and epoch_gap < 3 and noise / length < max_noise):
                noise, length = noise + 1, length + 1
            else:
                temp[current_code].append(length - 1 if df[column][i - 1] != current_code else length)
                length = 2 if df[column][i - 1] != current_code else 1
                noise = 0
                current_code = value if value in codes else df[column][i + skip(df, i, codes, column)]
        else:
            length += 1
    temp[current_code].append(length)
    return get_bout_categories(temp, epm, settings['i_cat'], settings['a_cat'])


def skip(df, index, codes, column) -> int:
    count = 1
    try:
        while df[column][index + count] not in codes:
            count += 1
        return count
    except KeyError:
        return count


def find_next(df, code, index, column) -> int:
    count = 1
    try:
        while df[column][index + count] != code:
            count += 1
        return count
    except KeyError:
        return count


def get_bout_categories(bout_dict, epm, i_cat, a_cat) -> dict[dict[list]]:
    bouts = {code: [sum(map(lambda item: (a_cat if code not in [7, 8] else i_cat)[i][0] / (60 / epm) <= item <=
                                         (a_cat if code not in [7, 8] else i_cat)[i][1] / (60 / epm),
                            bout_dict[code]))
                    for i in list(a_cat.keys())]
             for code in bout_dict.keys()}
    return bouts
    