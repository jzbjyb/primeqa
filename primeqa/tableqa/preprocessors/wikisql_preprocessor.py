from primeqa.tableqa.preprocessors.convert_to_sqa_format import parse_question
from primeqa.tableqa.preprocessors.dataset import TableQADataset
from primeqa.tableqa.utils.wikisql_utils import _execute_sql
import pandas as pd
import csv
import nlp
from nlp import load_dataset


def preprocess_wikisql(dataset,split):
    file_to_write = open("primeqa/tableqa/preprocessors/data/wikisql/"+split+".tsv","w")
    tsv_writer = csv.writer(file_to_write, delimiter='\t')
    tsv_writer.writerow(['id','question','table_file','answer_coordinates','answer_text','float_answer','aggregation_label'])
    for id, d in enumerate(dataset):
        question = d['question']
        qid = "wikisql_"+str(id)
        table = d['table']
        
        sql = d['sql']
        answer_text,table =  get_answer(table,sql)
        answer_text = [str(i) for i in answer_text]
        table_id,processed_table,min_tokens = preprocess_table(table)
        if answer_text==['']:
            continue
        if min_tokens > 150:
            continue
        table_df = pd.DataFrame.from_dict(processed_table)
        #print("question and answer",question,answer_text,sql,table_df)
        parsed_data = parse_question(table_df,question,answer_text)
        table_df.to_csv("primeqa/tableqa/preprocessors/data/wikisql/tables/"+str(table_id)+".csv", sep=',')
        answer_coordinates = parsed_data[2]
        if answer_coordinates=="" or answer_coordinates==None or answer_coordinates==[]:
            continue
        #print(parsed_data)
        float_answer = parsed_data[3]
        aggregation_label = parsed_data[4]
        tsv_writer.writerow([qid,question,"tables/"+str(table_id)+".csv",answer_coordinates,answer_text,float_answer,aggregation_label])
    print("done")
    file_to_write.close()


def preprocess_table(table):
    header = table['header']
    id = table['id']
    rows = table['rows']
    min_tokens = len(header)*len(rows)
    table_data = {}
    for i,h in enumerate(header):
        table_data[h] = [r[i] for r in rows]
    return id,table_data,min_tokens


def get_answer(table,sql):
    answer_text = None
    answer_text,table = _execute_sql(sql,table)
    return answer_text,table





if __name__=="__main__":
    print("preprocessing wikisql dataset")
    wikisql = TableQADataset("wikisql")
    dataset_dev = load_dataset('wikisql', split=nlp.Split.VALIDATION)
    dataset_train = load_dataset('wikisql', split=nlp.Split.TRAIN)
    preprocess_wikisql(dataset_dev,"dev")
    preprocess_wikisql(dataset_train,"train")
