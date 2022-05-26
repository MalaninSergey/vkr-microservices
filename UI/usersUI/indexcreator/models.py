import logging

from django.contrib.auth.models import User
from django.db import models
from elasticsearch import Elasticsearch


class UserProject(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, auto_now=False, blank=True)
    projectId = models.CharField(max_length=32)

    def __str__(self):
        return self.name

    def create_index(self, fields):
        products_index_name = str(self.name) + '_products_' + str(self.projectId)
        logging.info(f"Creating indexes {products_index_name}")
        es = Elasticsearch(hosts=["http://elasticsearch:9200/"])
        mapping = {
            "settings": {
                "analysis": {
                    "filter": {
                        "ru_stopwords": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        }
                    },
                    "char_filter": {
                        "dots": {
                            "pattern": """(\d+),(\d+)""",
                            "type": "pattern_replace",
                            "replacement": "$1.$2"
                        },
                        "symbols": {
                            "pattern": "[^a-zA-Z0-9а-яА-Я]+",
                            "type": "pattern_replace",
                            "replacement": " "
                        },
                        "ru": {
                            "type": "mapping",
                            "mappings": [
                                "ё => е",
                                "Ё => Е"
                            ]
                        }
                    },
                    "analyzer": {
                        "default_search": {
                            "filter": [
                                "lowercase",
                                "ru_stopwords",
                            ],
                            "char_filter": [
                                "ru",
                                "dots"
                            ],
                            "type": "custom",
                            "tokenizer": "standard"
                        },
                        "default": {
                            "filter": [
                                "lowercase",
                                "ru_stopwords",
                            ],
                            "char_filter": [
                                "ru",
                                "dots"
                            ],
                            "type": "custom",
                            "tokenizer": "standard"
                        },
                    }
                }
            },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "name": {
                        "type": "text",
                    },
                    "itemId": {
                        "type": "text",
                    },
                }
            }
        }
        if len(fields):
            for field in fields:
                mapping["mappings"]["properties"].update({field["field_name"]: {"type": field["field_type"]}})
        k = es.indices.create(index=products_index_name, body=mapping)
        return k
