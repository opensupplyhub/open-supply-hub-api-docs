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

    request.state.index = request.url.path.strip("/v1?")

    if len(request.state.index) == 0:
        return await call_next(request)

    with open(f"/code/app/indexes/{request.state.index}_config.json") as file:
        request.state.index_config = load(file)

        for field in request.state.index_config["mappings"]["properties"]:
            if (
                request.state.index_config["mappings"]["properties"][field]["type"]
                == "keyword"
            ):
                request.state.index_id_field = field
                break

    index_exists = search.indices.exists(index=request.state.index)

    if index_exists:
        return await call_next(request)

    search.indices.create(
        index=request.state.index,
        body=request.state.index_config,
    )

    with open(f"/code/app/indexes/{request.state.index}.json") as file:
        docs = load(file)

        for doc in docs:
            search.index(
                index=request.state.index,
                body=doc,
                id=doc[request.state.index_id_field],
            )

        file.close()

    return await call_next(request)


@app.get("/v1/countries")
def read_root(request: Request):
    body = {
        "size": 10,
        "sort": [
            {request.state.index_id_field: "asc"},
        ],
    }

    order_by = "asc"

    if "order_by" in request.query_params:
        order_by = request.query_params["order_by"]

    if "sort_by" in request.query_params:
        body["sort"] = [
            {request.query_params["sort_by"]: order_by},
        ]

    if "size" in request.query_params:
        body["size"] = request.query_params["size"]

    if "search_after" in request.query_params:
        body["search_after"] = [request.query_params["search_after"]]

    fields = []

    if "fields" in request.query_params and len(request.query_params["fields"]) > 0:
        fields = request.query_params["fields"].split(",")

    for field in request.state.index_config["mappings"]["properties"]:
        match = {
            "match": {},
        }

        if field in request.query_params:
            match["match"][field] = request.query_params[field]

        if len(match["match"]) > 0:
            body["query"] = match

    documents = search.search(
        index=request.state.index,
        body=body,
    )
    countries = []

    for document in documents["hits"]["hits"]:
        if len(fields) > 0:
            country = {}

            for field in fields:
                country[field] = document["_source"][field]

            countries.append(country)
        else:
            countries.append(document["_source"])

    return countries
