from fastapi import FastAPI
from elasticsearch import Elasticsearch
from os import getenv

app = FastAPI()
search = Elasticsearch(getenv("ELASTICSEARCH_URL"))


@app.get("/")
def read_root():
    return {}
