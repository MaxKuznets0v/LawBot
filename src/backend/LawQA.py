from haystack.utils import launch_es
from haystack.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.reader.farm import FARMReader
from haystack.pipeline import ExtractiveQAPipeline
from haystack.utils import print_answers
import torch, gc
import json
import time


class LawBot:
    data_path = "data/es_articles.json"
    #reader_model = "deepset/xlm-roberta-base-squad2"
    # reader_model = "AlexKay/xlm-roberta-large-qa-multilingual-finedtuned-ru"
    #reader_model = "models/my_data_sber_train"
    reader_model = "models/law_tuned_second"

    def __init__(self, bm25: bool, gpu: bool = False) -> None:
        self._launch_db()
        self._set_pipe(bm25=bm25, gpu=gpu)

    def _launch_db(self) -> None:
        try:
            self.database = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document", analyzer="russian")
        except ConnectionError:
            launch_es()
            time.sleep(5)
            self.database = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document", analyzer="russian")

            with open(self.data_path, 'r', encoding="utf-8") as file:
                data = json.load(file)
            # TODO: make proper data file!!
            fixed_data = list()
            for elem in data:
                fixed_data.append({'content': elem['text'], 'meta': elem['meta']})

            self.database.write_documents(fixed_data)

    def _set_pipe(self, bm25: bool, gpu: bool = False) -> None:
        if gpu:
            torch.cuda.set_device(0)
        if bm25:
            self.retriever = ElasticsearchRetriever(document_store=self.database)
        else:
            self.retriever = EmbeddingRetriever(
                document_store=self.database,
                model_format="sentence_transformers",
                embedding_model="distiluse-base-multilingual-cased-v1",
                use_gpu=gpu
            )
            self.database.update_embeddings(self.retriever, update_existing_embeddings=False)
        self.reader = FARMReader(model_name_or_path=self.reader_model, use_gpu=gpu)
        self.pipe = ExtractiveQAPipeline(self.reader, self.retriever)

    def _empty_cache(self):
        try:
            gc.collect()
            torch.cuda.empty_cache()
        except Exception as e:
            print("Can't empty cache!")
            print(e)

    def answer(self, query: str, mode: str = "all") -> None:    
        self._empty_cache()
        pred = self.pipe.run(query=query, params={"Retriever": {"top_k": 15}, "Reader": {"top_k": 5}})
        print_answers(pred, mode)
        return pred
