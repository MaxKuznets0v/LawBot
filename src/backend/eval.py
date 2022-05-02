import json

from datasets import load_dataset
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import PreProcessor
from haystack.nodes import ElasticsearchRetriever
from haystack.nodes import FARMReader
from haystack.nodes import DensePassageRetriever, EmbeddingRetriever
from haystack.pipelines import ExtractiveQAPipeline
from haystack.schema import EvaluationResult


if __name__ == '__main__':
    # ds = load_dataset('sberquad', split='validation[0:1000]')
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

    # with open('evaluation/test.json', 'w+', encoding='utf-8') as file:
    #     json.dump(squad_format, file, ensure_ascii=False)

    with open('models/train.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    data['data'] = data['data'][:100]
    with open('models/train_sliced.json', 'w+', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

    doc_index = "test_data"
    label_index = "test_labels"
    
    # Connect to Elasticsearch
    document_store = ElasticsearchDocumentStore(
        host="localhost",
        username="",
        password="",
        index=doc_index,
        label_index=label_index,
        embedding_field="sber",
        #embedding_dim=512,
        # embedding_dim=768,
        embedding_dim=1024,
        excluded_meta_data=["sber"],
        similarity="cosine"
    )

    # Add evaluation data to Elasticsearch Document Store
    # We first delete the custom tutorial indices to not have duplicate elements
    # and also split our documents into shorter passages using the PreProcessor
    preprocessor = PreProcessor(
        split_length=200,
        split_overlap=0,
        split_respect_sentence_boundary=False,
        clean_empty_lines=False,
        clean_whitespace=False,
    )
    
    document_store.delete_documents(index=doc_index)
    document_store.delete_documents(index=label_index)

    document_store.add_eval_data(
        filename="models/train_sliced.json",
        doc_index=doc_index,
        label_index=label_index,
        preprocessor=preprocessor,
    )

    # retriever = ElasticsearchRetriever(document_store=document_store)
    # retriever = EmbeddingRetriever(
    #     document_store=document_store,
    #     model_format="sentence_transformers",
    #     embedding_model="distiluse-base-multilingual-cased-v1",
    #     use_gpu=False
    # )
    retriever = EmbeddingRetriever(
        document_store=document_store,
        model_format="sentence_transformers",
        embedding_model="sberbank-ai/sbert_large_nlu_ru",
        use_gpu=False
    )
    # retriever = DensePassageRetriever(document_store=document_store,
    #                                   query_embedding_model="voidful/dpr-question_encoder-bert-base-multilingual",
    #                                   passage_embedding_model="voidful/dpr-ctx_encoder-bert-base-multilingual",
    #                                   use_gpu=False,
    #                                   max_seq_len_passage=256,
    #                                   embed_title=True)
    document_store.update_embeddings(retriever, index=doc_index)
    reader = FARMReader("models/my_data_sber_train", top_k=5, return_no_answer=True, use_gpu=True)

    # Define a pipeline consisting of the initialized retriever and reader

    pipeline = ExtractiveQAPipeline(reader=reader, retriever=retriever)


    eval_labels = document_store.get_all_labels_aggregated(drop_negative_labels=True, drop_no_answers=False)
    eval_labels = [label for label in eval_labels if not label.no_answer]  # filter out no_answer cases
    eval_result = pipeline.eval(labels=eval_labels, params={"Retriever": {"top_k": 15}})
    eval_result.save("shorts/sber_alex_sber_train_100")

    saved_eval_result = EvaluationResult.load("shorts/sber_alex_sber_train_100")
    metrics = saved_eval_result.calculate_metrics()
    print(f'Retriever - Recall (single relevant document): {metrics["Retriever"]["recall_single_hit"]}')
    print(f'Retriever - Recall (multiple relevant documents): {metrics["Retriever"]["recall_multi_hit"]}')
    print(f'Retriever - Mean Reciprocal Rank: {metrics["Retriever"]["mrr"]}')
    print(f'Retriever - Precision: {metrics["Retriever"]["precision"]}')
    print(f'Retriever - Mean Average Precision: {metrics["Retriever"]["map"]}')

    print(f'Reader - F1-Score: {metrics["Reader"]["f1"]}')
    print(f'Reader - Exact Match: {metrics["Reader"]["exact_match"]}')

    pipeline.print_eval_report(saved_eval_result)
