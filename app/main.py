from fastapi import FastAPI, Request
from elasticsearch import Elasticsearch
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPMethod
from os import getenv
from json import load

search = Elasticsearch(getenv("ELASTICSEARCH_URL"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if request.method != HTTPMethod.GET:
        return await call_next(request)

    if request.url.path.count("/") != 2:
        return await call_next(request)

    index = request.url.path.strip("/v1?")

    if len(index) == 0:
        return await call_next(request)

    index_exists = search.indices.exists(index=index)

    if index_exists:
        return await call_next(request)

    search.indices.create(
        index=index,
        body={
            "mappings": {
                "properties": {
                    "id": {
                        "type": "keyword",
                    }
                }
            }
        },
    )

    with open(f"/code/app/indexes/{index}.json") as file:
        docs = load(file)

        for doc in docs:
            search.index(index=index, body=doc, id=doc["id"])

        file.close()

    return await call_next(request)


@app.get("/v1/countries")
def read_root(request: Request):
    body = {
        "size": request.query_params["limit"],
        "sort": [
            {"id": "asc"},
        ],
    }

    if "after" in request.query_params:
        body["search_after"] = [request.query_params["after"]]

    documents = search.search(index="countries", body=body)
    countries = []

    for document in documents["hits"]["hits"]:
        countries.append(document["_source"])

    return countries
