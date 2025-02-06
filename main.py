import pandas as pd
import glob
import os
from datetime import datetime
from icecream import ic
import time
from itertools import groupby
from operator import itemgetter
import argparse

from utils.processing_settings import get_settings
from utils.df_filter import filter_dataframe, filter_days
from utils.activity import get_activities
from utils.transition import get_ait, get_transitions, calc_trans
from utils.bout import get_bouts

start_time = time.time()


def main(data_folder):
    outgoing_df = pd.DataFrame()
    settings, data_path = get_settings()

    for csvfile in glob.glob(data_folder + '*.csv'):
        df = pd.read_csv(csvfile)
        if settings['id_column'] not in df.columns:
            continue

        new_line = {'subject_id': df[settings['id_column']][0]}
        print(f'--- Processing file: {new_line["subject_id"]} ---', end='\r', flush=True)
        epm, epd = epoch_test(new_line, df, settings['time_column'])
        df = filter_dataframe(df, settings)

        index = get_index(df, settings['time_column'])
        filter_days(df, index, settings, epd)
        index = shift_index_keys(index)

        date_info = get_date_info(df, index)
        variables = get_variables(epm, df, index, settings)

        calculate_variables(new_line, index, date_info, variables, epm, epd, settings)
        outgoing_df = pd.concat([pd.DataFrame(new_line, index=[0]), outgoing_df], ignore_index=True)

    if not os.path.exists(os.path.join(data_path, 'post processing')):
        os.makedirs(os.path.join(data_path, 'post processing'))
    os.chdir(os.path.join(data_path, 'post processing'))

    outgoing_df.to_csv(f'post process data {str(datetime.now().strftime("%d.%m.%Y %H.%M"))}.csv', index=False)
    end_time = time.time()
    print(f'--- Total run time: {end_time - start_time} sec ---')


def epoch_test(new_line: dict, df: pd.DataFrame, time_column: str) -> tuple[int, int]:
    datetime_object1 = datetime.strptime(df[time_column][10][:19], "%Y-%m-%d %H:%M:%S")
    datetime_object2 = datetime.strptime(df[time_column][11][:19], "%Y-%m-%d %H:%M:%S")
    epm = int(60 / (datetime_object2 - datetime_object1).total_seconds())
    epd = epm * 60 * 24

    new_line.update({'epoch per min': epm,
                     'epoch per day': epd})
    return epm, epd


def get_index(df: pd.DataFrame, time_column: str) -> dict:
    index = [(list(map(itemgetter(1), g))[0]) for k, g in
             groupby(enumerate(df.index[df[time_column].str.contains(' 00:00:')].tolist()), lambda ix: ix[0] - ix[1])]
    if index[0] != 0:
        index.insert(0, 0)
    if index[-1] != len(df):
        index.append(len(df))
    index_dict = {i + 1: [index[i], index[i + 1]] for i in range(len(index) - 1)}

    return index_dict


def shift_index_keys(index: dict) -> dict:
    sorted_keys = sorted(index.keys())
    shifted_dict = {new_key: index[old_key] for new_key, old_key in enumerate(sorted_keys, start=1)}
    return shifted_dict


def get_date_info(df, index):
    info = {day: {
        'day_nr': datetime.strptime(df['timestamp'][val[0]][:10], "%Y-%m-%d").weekday() + 1,
        'day_str': datetime.strptime(df['timestamp'][val[0]][:10], "%Y-%m-%d").strftime('%A'),
        'date': df['timestamp'][val[0]][:10], 'length_epoch': index[day][1] - index[day][0]}
        for day, val in index.items()}
    return info


def get_variables(epm, df, index, settings) -> dict:
    variables = {'ai': get_activities(df, index, settings['ai_codes'], settings['ai_column']),

                 'act': get_activities(df, index, settings['act_codes'], settings['act_column']),

                 'ait': get_ait(df, index),

                 'transitions': get_transitions(df, index),

                 'bout': get_bouts(df, index, epm, settings)}

    return variables


def calculate_variables(new_line, index, date_info, variables, epm, epd, settings):
    temp = {'ai': ['ai_codes', 'ai_column'], 'act': ['act_codes', 'act_column'], 'walk': ['walk_codes', 'walk_column']}
    chosen_var = {key: {'codes': settings[codes], 'column': settings[column]}
                  for key, (codes, column) in temp.items() if key in variables}
    code_name = settings['code_name']
    bout_codes = settings['bout_codes']

    wk_wknd = weekday_distribution(new_line, index, date_info, epm)
    if wk_wknd['total'] == 0:
        return
    average_variables(new_line, variables, index, wk_wknd, epm, epd, code_name, chosen_var, bout_codes)
    daily_variables(new_line, variables, date_info, code_name)

    return


def weekday_distribution(new_line, index, date_info, epm) -> dict:
    wk_wknd = {'wk': [val[1] - val[0] for key, val in index.items() if date_info[key]['day_nr'] not in [6, 7]],
               'wknd': [val[1] - val[0] for key, val in index.items() if date_info[key]['day_nr'] in [6, 7]]}
    for key, val in wk_wknd.items():
        wk_wknd[key] = sum(val) / (epm * 60 * 24)
    wk_wknd['total'] = wk_wknd['wk'] + wk_wknd['wknd']

    new_line[f'total_days'] = round(wk_wknd['total'], 2)
    new_line[f'wk_days'] = round(wk_wknd['wk'], 2)
    new_line[f'wknd_days'] = round(wk_wknd['wknd'], 2)
    return wk_wknd


def average_variables(new_line, var, index, wk_wknd, epm, epd, code_name, chosen_var, bout_codes):

    for key, dic in chosen_var.items():
        temp = {code: [var[key][day][code] for day in index.keys()] for code in dic['codes']}
        act_avg = {code: sum(temp[code]) / (wk_wknd['total']) for code in dic['codes']}
        for code, value in act_avg.items():
            new_line[f'avg_{code_name[code]}_min'] = round(value / epm, 2)
            new_line[f'avg_{code_name[code]}_pct'] = round(value / epd * 100, 2)

    temp = sum(var['ait'][day] for day in index.keys()) / wk_wknd['total']
    new_line[f'avg_ait'] = round(temp, 2)

    temp = {}
    for outer_key, inner_dict in var["transitions"].items():
        for second_tier_key, inner_values in inner_dict.items():
            for inner_key, value in inner_values.items():
                temp.setdefault(second_tier_key, {}).setdefault(inner_key, []).append(value)
    
    for t_code, dic in temp.items():
        for f_code, val in dic.items():
            new_line[f'avg_tran_{code_name[f_code]}_to_{code_name[t_code]}'] = round(sum(val) / wk_wknd['total'], 2)

    temp = {code: [var['bout'][day][code] for day in index.keys()] for code in bout_codes}
    for code, lists in temp.items():
        temp[code] = [round(sum(x) / wk_wknd['total'], 2) for x in zip(*lists)]
    for code, values in temp.items():
        for nr, val in enumerate(values):
            new_line[f'avg_{code_name[code]}_bout_c{nr + 1}'] = val


def daily_variables(new_line, var, date_info, code_name):

    for day, info in date_info.items():
        new_line[f'day{day}_nr'] = day
        new_line[f'day{day}_date'] = info['date']
        new_line[f'day{day}_wkday_nr'] = info['day_nr']
        new_line[f'day{day}_wkday_str'] = info['day_str']
        new_line[f'day{day}_length_min'] = info['length_epoch']
        new_line[f'day{day}_length_pct'] = round(info['length_epoch'] / 1440 * 100, 2)

        for code, values in var['act'][day].items():
            new_line[f'day{day}_{code_name[code]}'] = values

        for code, values in var['act'][day].items():
            new_line[f'day{day}_{code_name[code]}'] = values

        new_line[f'day{day}_ait'] = var['ait'][day]
        
        for t_code, dic in var['transitions'][day].items():
            for f_code, value in dic.items():
                new_line[f'day{day}_tran_{code_name[f_code]}_to_{code_name[t_code]}'] = value

        for code, values in var['bout'][day].items():
            for nr, val in enumerate(values):
                new_line[f'day{day}_{code_name[code]}_bouts_c{nr + 1}'] = val


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-folder', type=str, dest='data_folder', help='Path of dataset folder')
    args = parser.parse_args()
    if not args.data_folder:
        args.data_folder = os.path.join(os.getcwd(), 'data/')    
    main(args.data_folder)
