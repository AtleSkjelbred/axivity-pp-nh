from itertools import groupby
from operator import itemgetter
from collections import Counter


def calculate_transitions(df, start, end, column, code):
    return len([list(map(itemgetter(1), g))[0] for k, g in groupby(enumerate([index for index, item in enumerate(
        df[column][start: end]) if item == code]), lambda ix: ix[0] - ix[1])])


def calc_trans(df, start, end, column, code):
    return dict(Counter([df[column][start_idx - 1] for start_idx in [list(
        map(itemgetter(1), g))[0] + start for k, g in groupby(enumerate(
        [index for index, item in enumerate(df[column][start:end]) if item == code]), lambda ix: ix[0] - ix[1])]
                        if start_idx > start]))


def get_advanced_transitions():
    transitions = {}
    codes = [1, 6, 7, 8]
    for day, value in index.items():
        transitions[day] = {}
        for code in codes:
            transitions[day][code] = calculate_transitions(df, value[0], value[1], 'label', code)
    return transitions


def get_ait(df, index):
    ait = {}
    for day, value in index.items():
        ait[day] = calculate_transitions(df, value[0], value[1], 'ai_column', 'A')
    return ait


def get_transitions(df, index):
    transitions = {}
    codes = [1, 6]
    for day, value in index.items():
        transitions[day] = {}
        for code in codes:
            transitions[day][code] = calc_trans(df, value[0], value[1], 'label', code)
    return transitions
