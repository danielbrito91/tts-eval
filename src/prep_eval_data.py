import json
from typing import List

import pandas as pd


def read_dict_results(dict_results: dict) -> pd.DataFrame:
    open_dict = {
        'quality': [],
        'speaker_sim': [],
        'emotion_sim': [],
        'model': [],
        'synthFile': [],
        'refFile': [],
        'type': [],
        'emotion': [],
    }
    for result in dict_results['results']:
        open_dict['emotion'].append(result['hiddenData']['emotion'])
        open_dict['model'].append(result['hiddenData']['model'])
        open_dict['synthFile'].append(result['hiddenData']['synthFile'])
        open_dict['refFile'].append(result['hiddenData']['refFile'])
        open_dict['type'].append(result['type'])
        open_dict['quality'].append(result['ratings']['mos'])
        open_dict['speaker_sim'].append(result['ratings']['speakerSimilarity'])
        open_dict['emotion_sim'].append(result['ratings']['emotionSimilarity'])

    return pd.DataFrame(open_dict)


def prep_eval_data(src_path: str = 'results/tts-results.csv') -> pd.DataFrame:
    form_results = pd.read_csv(src_path)
    result_dfs: List[pd.DataFrame] = []

    for _, row in form_results.iterrows():
        participant_id = row['participant_id']
        confirmation_code = row['confirmation_code']
        results_json = row['results_json']
        timestamp = row['timestamp']

        dict_results = json.loads(results_json)
        result_df = read_dict_results(dict_results)
        result_df['participant_id'] = participant_id
        result_df['confirmation_code'] = confirmation_code
        result_df['timestamp'] = timestamp
        result_dfs.append(result_df)

    return pd.concat(result_dfs)
