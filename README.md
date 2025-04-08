# Souhl Microservice

## Prerequisites

- strawberry, uvicorn, fastapi are installed via pip

## Install Tools

- rover (via brew)
- apollo router (binary)

```sh
$ brew install rover
$ curl -sSL https://router.apollo.dev/download/nix/latest | sh

# accept the terms and conditions
$ rover supergraph compose --config ./supergraph.yaml
merging supergraph schema files
supergraph config loaded successfully
By installing this plugin, you accept the terms and conditions outlined by this license.
More information on the ELv2 license can be found here: https://go.apollo.dev/elv2.
Do you accept the terms and conditions of the ELv2 license? [y/N]
y
...
```

## generate supergraph schema

supergraph-schema.graphql を自動生成する

```sh
$ rover supergraph compose --config ./supergraph.yaml > supergraph-schema.graphql
```

## run books service

```sh
$ cd python/books
$ python3 -m strawberry server --port 3500 app.py
```

## run reviews service

```sh
$ cd python/reviews
$ python3 -m uvicorn app:app --host "0.0.0.0" --port 3501 --reload
```

## run router

```sh
$ ./router --supergraph supergraph-schema.graphql
```

## run http request

see `supergraph.http` file
