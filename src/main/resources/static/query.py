import requests as re
import json

HOST = 'http://localhost:8080'

CATEGORY = [
    'Vaccine hesitancy',
    'Stem cell research',
    'History of medieval medicine',
    'Animal testing'
]

FILE_NAME = {cat: '_'.join(cat.split()).lower() + '.json' for cat in CATEGORY}

QUERY = {
    CATEGORY[0]: [
        'vaccine conspirancy',
        'covid-19 conspirancy'
        ],
    CATEGORY[1]: [
        'stem cells',
        'stem cell'
        ],
    CATEGORY[2]: [
        'plague',
        'plague medieval',
        'medieval'
        ],
    CATEGORY[3]: [
        'test medicine animals',
        'animal ethics'
        ]
    }

RESULTS = {}
def test(category):

    global RESULTS
    RESULTS[category] = {}

    for query in QUERY[category]:
        RESULTS[category][query] = {}

        res = re.post(
            f'{HOST}/query',
            json={'text': query}
        )

        if res.status_code == 200:
            data = res.json()
            RESULTS[category][query]['weighted'] = list(map(lambda d: d['ID'], data))


        res = re.post(
            f'{HOST}/full_text',
            json={'text': query}
        )

        if res.status_code == 200:
            data = res.json()
            RESULTS[category][query]['unweighted'] = list(map(lambda d: d['ID'], data))

for c in CATEGORY:
    test(c)

with open('results.json', 'w') as f:
    json.dump(RESULTS, f)
