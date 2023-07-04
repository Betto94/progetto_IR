import requests as re
import json
import os
import matplotlib.pyplot as plt
from pprint import pprint

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
def get_category_documents(category):

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

def load_documents():
    global CATEGORY, RESULTS

    if os.path.exists('./results.json'):
        with open('./results.json', 'r') as f:
            RESULTS = json.load(f)
    else:
        for c in CATEGORY:
            get_category_documents(c)

        with open('results.json', 'w') as f:
            json.dump(RESULTS, f)

def load_relevants(category):
    with open(f'./{category}', 'r') as f:
        relevants = json.load(f)
        return list(map(lambda d: int(d['ID']), relevants))

def compute_precision(category, query):
    global RESULTS, RELEVANTS

    weighted = set(RESULTS[category][query]['weighted'])
    unweighted = set(RESULTS[category][query]['unweighted'])

    relevants = set(RELEVANTS[category])

    precision_weighted = len(weighted & relevants) / len(weighted)
    precision_unweighted = len(unweighted & relevants) / len(unweighted)
    return precision_weighted, precision_unweighted

def compute_recall(category, query):
    global RESULTS, RELEVANTS

    weighted = set(RESULTS[category][query]['weighted'])
    unweighted = set(RESULTS[category][query]['unweighted'])

    relevants = set(RELEVANTS[category])

    precision_weighted = len(weighted & relevants) / len(relevants)
    precision_unweighted = len(unweighted & relevants) / len(relevants)
    return precision_weighted, precision_unweighted

def compute_f1_measure(category, query):
    precision_weighted, precision_unweighted = compute_precision(category, query)
    recall_weighted, recall_unweighted = compute_recall(category, query)
    f1 = lambda p, r: (2*p*r) / (p + r) if (p + r) > 0 else 0

    print(f'p: {precision_weighted}, r: {recall_weighted}')

    return f1(precision_weighted, recall_weighted), f1(precision_unweighted, recall_unweighted)

def precision_at_k(results: list, relevants: list, k: int):
    assert(k <= len(results))
    first_k = set(results[:k])
    return len(first_k & set(relevants)) / len(first_k)


def compute_map(category):
    global RESULTS, RELEVANTS

    relevants = RELEVANTS[category]

    weighted_MAP = []
    unweighted_MAP = []
    for query in QUERY[category]:
        weighted = RESULTS[category][query]['weighted']
        unweighted = RESULTS[category][query]['unweighted']
        
        weighted_ap = []
        K = 0
        for k in range(1, len(weighted)+1):
            if weighted[k-1] in relevants:
                K += 1
                weighted_ap.append(precision_at_k(weighted, relevants, k))
        weighted_ap = sum(weighted_ap) / K if K > 0 else 0
        weighted_MAP.append(weighted_ap)

        unweighted_ap = []
        K = 0
        for k in range(1, len(unweighted)+1):
            if unweighted[k-1] in relevants:
                K += 1
                unweighted_ap.append(precision_at_k(unweighted, relevants, k))
        unweighted_ap = sum(unweighted_ap) / K if K > 0 else 0
        unweighted_MAP.append(unweighted_ap)

    weighted_MAP = sum(weighted_MAP)/len(weighted_MAP)
    unweighted_MAP = sum(unweighted_MAP)/len(unweighted_MAP)
    return weighted_MAP, unweighted_MAP

def plot_valutation_bar_chart():
    import numpy as np

    measure = ('Precision', 'Recall', 'F1 score')

    means = {
        'Weighted Model': (.39, .42, .404),
        'Full Text Model': (.458, .49, .473),
    }

    fig, ax = plt.subplots(layout='constrained')
    width = .25
    multiplier = 0
    x = np.arange(len(measure))
    for attribute, measurement in means.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    # ax.set_ylabel('Length (mm)')
    ax.set_title('Valutazioni')
    ax.set_xticks(x + width, measure)
    ax.legend(loc='upper left', ncols=3)
    ax.set_ylim(0, 250)

    plt.show()
    
RELEVANTS = {}
if __name__ == '__main__':
    load_documents()

    for category in CATEGORY:
        relevants = load_relevants(FILE_NAME[category])
        RELEVANTS[category] = relevants
    
    MAP = {}
    for category in CATEGORY:
        MAP[category] = compute_map(category)

    pprint(MAP)

    mmap_1 = sum([MAP[c][0] for c in CATEGORY])/len(CATEGORY)
    mmap_2 = sum([MAP[c][1] for c in CATEGORY])/len(CATEGORY)

    print(f'MAP weighted:\t{mmap_1}')
    print(f'MAP unweighted:\t{mmap_2}')

    plt.bar(['full text', 'weighted'], [mmap_1,mmap_2])
    # plt.show()

    precision, recall, f1_score = {}, {}, {}
    for c in CATEGORY:
        precision[c] = {
            'weighted': [],
            'full_text': []
        }
        
        recall[c] = {
            'weighted': [],
            'full_text': []
        }

        f1_score[c] = {
            'weighted': [],
            'full_text': []
        }

        for q in QUERY[c]:
            p = compute_precision(c, q)
            r = compute_recall(c, q)
            f = compute_f1_measure(c, q)

            precision[c]['weighted'].append(p[0])
            precision[c]['full_text'].append(p[1])
            
            recall[c]['weighted'].append(r[0])
            recall[c]['full_text'].append(r[1])
            
            f1_score[c]['weighted'].append(f[0])
            f1_score[c]['full_text'].append(f[1])

        precision[c]['weighted'] = sum(precision[c]['weighted']) / len(precision[c]['weighted'])
        precision[c]['full_text'] = sum(precision[c]['full_text']) / len(precision[c]['full_text'])

        recall[c]['weighted'] = sum(recall[c]['weighted']) / len(recall[c]['weighted'])
        recall[c]['full_text'] = sum(recall[c]['full_text']) / len(recall[c]['full_text'])
        
        f1_score[c]['weighted'] = sum(f1_score[c]['weighted']) / len(f1_score[c]['weighted'])
        f1_score[c]['full_text'] = sum(f1_score[c]['full_text']) / len(f1_score[c]['full_text'])
    
    print('WEIGHTED')
    print('Category\t| Precision\t| Recall\t| F1')
    for c in CATEGORY:
        print(f'{c}: \t{precision[c]["weighted"]} | {recall[c]["weighted"]} | {f1_score[c]["weighted"]}')  

    print("\t==================")
    print('FULL TEXT')
    print('Category | Precision | Recall | F1')
    for c in CATEGORY:
        print(f'{c}:\t{precision[c]["full_text"]} | {recall[c]["full_text"]} | {f1_score[c]["full_text"]}')


    plot_valutation_bar_chart()
