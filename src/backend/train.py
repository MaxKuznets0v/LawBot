from haystack.reader.farm import FARMReader
from datasets import load_dataset
import json


if __name__ == '__main__':
    # ds = load_dataset('sberquad', split='train[0:1000]')
    # t_data = ds
    # squad_format = {'data': list()}
    # paragraphs = list()
    # contexts = set()
    # for line in t_data:
    #     if line['context'] not in contexts:
    #         contexts.add(line['context'])
    #         paragraphs.append({'paragraphs': list()})
    #         paragraphs[-1]['paragraphs'].append({'context': line['context'], 'qas': list()})
    #     paragraphs[-1]['paragraphs'][-1]['qas'].append({'question': line['question'], 'id': line['id'], 'answers': [{'answer_id': line['id'], 'text': line['answers']['text'][0], 'answer_start': line['answers']['answer_start'][0]}]})
    # squad_format['data'] = paragraphs

    # with open('models/train_sber.json', 'w+', encoding='utf-8') as file:
    #     json.dump(squad_format, file, ensure_ascii=False)


    reader = FARMReader(model_name_or_path="AlexKay/xlm-roberta-large-qa-multilingual-finedtuned-ru", use_gpu=True)

    reader.train(data_dir="models", 
                        train_filename="train_sber.json", 
                        use_gpu=False, 
                        n_epochs=3, 
                        save_dir="models/alex_sber")
