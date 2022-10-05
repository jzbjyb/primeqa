import logging
from typing import Union, List

from primeqa.pipelines.base import RetrieverPipeline
from primeqa.pipelines.factories import SearcherFactory
from primeqa.ir.dense.colbert_top.colbert.infra.config import ColBERTConfig


class ColBERTRetriever(RetrieverPipeline):
    """
    Retriever: ColBERT
    """

    def __init__(
        self,
        logger: Union[logging.Logger, None] = None,
    ) -> None:
        if logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        else:
            self._logger = logger

        # Default object variables
        self.pipeline_id = self.__class__.__name__
        self.pipeline_name = "Dense Retriever (ColBERT)"
        self.pipeline_description = ""
        self.pipeline_type = RetrieverPipeline.__name__

        self.parameters = {
            "similarity": {
                "parameter_id": "similarity",
                "name": "Similarity metric",
                "type": "String",
                "value": "cosine",
                "options": ["cosine", "l2"],
            },
            "dim": {
                "parameter_id": "dim",
                "name": "Dimension",
                "type": "Numeric",
                "value": 128,
                "range": [32, 512, 32],
            },
            "query_maxlen": {
                "parameter_id": "query_maxlen",
                "name": "Maximum query length",
                "type": "Numeric",
                "value": 32,
                "range": [32, 128, 8],
            },
            "doc_maxlen": {
                "parameter_id": "doc_maxlen",
                "name": "Maximum document length",
                "type": "Numeric",
                "value": 180,
                "range": [32, 256, 4],
            },
            "mask_punctuation": {
                "parameter_id": "mask_punctuation",
                "name": "Should mask punctuation",
                "type": "Boolean",
                "value": True,
                "options": [True, False],
            },
            "bsize": {
                "parameter_id": "bsize",
                "name": "Batch size",
                "type": "Numeric",
                "value": 32,
                "range": [8, 128, 8],
            },
            "amp": {
                "parameter_id": "amp",
                "name": "Use amp",
                "type": "Boolean",
                "value": False,
                "options": [True, False],
            },
            "nbits": {
                "parameter_id": "nbits",
                "name": "nbits",
                "type": "Numeric",
                "value": 1,
                "options": [1, 2, 4],
            },
            "kmeans_niters": {
                "parameter_id": "kmeans_niters",
                "name": "Number of iterations (kmeans)",
                "type": "Numeric",
                "value": 4,
                "range": [1, 8, 1],
            },
            "num_partitions_max": {
                "parameter_id": "num_partitions_max",
                "name": "Maximum number of partitions",
                "type": "Numeric",
                "value": 10000000,
            },
            "nway": {
                "parameter_id": "nway",
                "name": "N way",
                "type": "Numeric",
                "value": 2,
            },
            "max_num_documents": {
                "parameter_id": "max_num_documents",
                "name": "Maximum number of answers",
                "type": "Numeric",
                "value": 100,
                "range": [1, 200, 1],
            },
            "ncells": {
                "parameter_id": "ncells",
                "name": "Number of cells",
                "type": "Numeric",
                "value": 1,
                "range": [1, 4, 1],
            },
            "centroid_score_threshold": {
                "parameter_id": "centroid_score_threshold",
                "name": "Centroid Score Threshold",
                "type": "Numeric",
                "value": 0.5,
                "range": [0.0, 1.0, 0.01],
            },
            "min_score_threshold": {
                "parameter_id": "min_score_threshold",
                "name": "Minimum score threshold",
                "type": "Numeric",
                "value": 0.0,
                "range": [-10.0, 10.0, 0.01],
            },
        }

        # Placeholder object variables
        self._config = ColBERTConfig(
            **{
                parameter_id: parameter["value"]
                for parameter_id, parameter in self.parameters.items()
                if parameter_id
                not in [
                    "max_num_documents",
                    "min_score_threshold",
                ]
            }
        )

    def load(self, *args, **kwargs):
        pass

    def get_parameters(self):
        return [self.parameters.values()]

    def set_parameter(self, parameter):
        self.parameters[parameter["parameter_id"]] = parameter

    def get_parameter(self, parameter_id: str):
        return self.parameters[parameter_id]

    def get_parameter_type(self, parameter_id: str):
        return self.parameters[parameter_id]["type"]

    def set_parameter_value(self, parameter_id: str, parameter_value: int):
        self.parameters[parameter_id]["value"] = parameter_value

    def get_parameter_value(self, parameter_id: str):
        return self.parameters[parameter_id]["value"]

    def serialize(self):
        return {
            "pipeline_id": self.pipeline_id,
            "parameters": {
                parameter["parameter_id"]: parameter["value"]
                for parameter in self.parameters.values()
            },
        }

    def retrieve(self, input_texts: List[str], *args, **kwargs):
        self._config.configure(index_path=kwargs["index_path"])
        searcher = SearcherFactory.get(self._config)
        ranking_results = searcher.search_all(
            {idx: str(input_text) for idx, input_text in enumerate(input_texts)},
            self.parameters["max_num_documents"]["value"],
        )
        return [
            [(entry[0], entry[-1]) for entry in results_per_query]
            for results_per_query in ranking_results.data.values()
        ]
