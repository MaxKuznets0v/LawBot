from haystack.schema import EvaluationResult
import os


def show(folder):
    saved_eval_result = EvaluationResult.load(folder)
    metrics = saved_eval_result.calculate_metrics()
    print(f'Retriever - Recall (single relevant document): {metrics["Retriever"]["recall_single_hit"]}')
    print(f'Retriever - Recall (multiple relevant documents): {metrics["Retriever"]["recall_multi_hit"]}')
    print(f'Retriever - Mean Reciprocal Rank: {metrics["Retriever"]["mrr"]}')
    print(f'Retriever - Precision: {metrics["Retriever"]["precision"]}')
    print(f'Retriever - Mean Average Precision: {metrics["Retriever"]["map"]}')

    print(f'Reader - F1-Score: {metrics["Reader"]["f1"]}')
    print(f'Reader - Exact Match: {metrics["Reader"]["exact_match"]}')
    print('-------------------------------------------------------------------------------------------------------')



if __name__ == '__main__':
    for elem in os.listdir('shorts/'):
        if os.path.isdir('shorts/' + elem):
            print(elem)
            try:
                show('shorts/' + elem)
            except:
                print("Can't do it")

