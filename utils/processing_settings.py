def get_settings():
    settings = {'id_column': 'SID',
                'time_column': 'timestamp',
                'ai_column': 'ai_column',
                'act_column': 'label',
                'walk_column': 'walking_intensity_prediction',
                'nw_column': 'snt_prediction'}

    act_codes = [1, 6, 7, 8]

    settings.update({'nw_codes': [1, 2, 3, 4],
                     'ai_codes': ['A', 'I'],
                     'act_codes': act_codes,
                     'bout_codes': [1, 6, 7, 8]})

    settings.update({'i_cat': {1: [60, 299], 2: [300, 599], 3: [600, 1799], 4: [1800, 3599], 5: [3600, 9999999],
                               6: [9999999, 9999999], 7: [9999999, 9999999], 8: [9999999, 9999999],
                               9: [9999999, 9999999], 10: [9999999, 9999999], 11: [9999999, 9999999],
                               12: [9999999, 9999999]},
                     'a_cat': {1: [60, 119], 2: [120, 179], 3: [180, 239], 4: [240, 299], 5: [300, 359], 6: [360, 419],
                               7: [420, 479], 8: [480, 539], 9: [540, 599], 10: [600, 1799], 11: [1800, 3599],
                               12: [3600, 9999999]},
                     'noise_threshold': 0.15})

    settings.update(
        {'code_name': {'I': 'inactive', 'A': 'active', 8: 'lying', 7: 'sitting', 6: 'standing', 1: 'walking',
                       2: 'running', 20: 'jumping', 13: 'cycling', 130: 'cyc_sit_inactive', 140: 'cyc_stand_inactive',
                       101: '101', 102: '102', 103: '103', 104: '104'}})

    data_path = ''

    return settings, data_path
