from flask import Blueprint
from flask import request
from elasticsearch import Elasticsearch

search_bp = Blueprint('search', __name__)


@search_bp.route('/search', methods=['POST'])
def hello_world():
    a = request.json
    es = Elasticsearch(hosts=["http://elasticsearch:9200/"])
    index_name = a['project_name'] + '_products_' + a['projectId']
    search_phrase = a['key_phrase']
    query = {
        "from": 0,
        "size": 200,
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": [
                                {
                                    "match_phrase": {
                                        "name.keyword": {
                                            "query": search_phrase,
                                            "slop": 0,
                                            "zero_terms_query": "NONE",
                                            "boost": 100.0
                                        }
                                    }
                                },
                                {
                                    "match": {
                                        "name": {
                                            "query": search_phrase,
                                            "operator": "AND",
                                            "prefix_length": 0,
                                            "max_expansions": 50,
                                            "fuzzy_transpositions": True,
                                            "lenient": False,
                                            "zero_terms_query": "NONE",
                                            "auto_generate_synonyms_phrase_query": True,
                                            "boost": 2.0
                                        }
                                    }
                                },
                                {
                                    "match": {
                                        "name": {
                                            "query": search_phrase,
                                            "operator": "OR",
                                            "prefix_length": 0,
                                            "max_expansions": 50,
                                            "fuzzy_transpositions": True,
                                            "lenient": False,
                                            "zero_terms_query": "NONE",
                                            "auto_generate_synonyms_phrase_query": True,
                                            "boost": 1.0
                                        }
                                    }
                                }
                            ],
                            "adjust_pure_negative": True,
                            "boost": 1.0
                        }
                    }
                ],
                "adjust_pure_negative": True,
                "boost": 1.0
            }
        },
        "_source": {
            "includes": [
                "itemId"
            ],
            "excludes": []
        },
        "sort": [
            {
                "_score": {
                    "order": "desc"
                }
            }
        ]

    }
    hits = es.search(index=index_name, body=query)
    items_list = []
    for elem in hits['hits']['hits']:
        items_list.append(elem['_source']['itemId'])
    return {'Items': items_list}
