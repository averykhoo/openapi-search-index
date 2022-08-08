# OpenAPI Search Index

* extract relevant strings from openapi specifications
* tokenize them
* build a search index over tokens
* provide a search method to query the index

## TODO

* extract from openapi
  * per-route and per-verb
  * bunch of relevant strings
* tokenizer
* spec index
  * add/update spec
    * try to avoid updating routes that didn't change
  * delete spec
  * list spec
* token index
  * add, remove
  * fuzzy query
* generate pydantic classes somehow
  * datamodel-code-generator + 
    * https://github.com/google/gnostic/blob/main/openapiv2/openapi-2.0.json
    * https://github.com/google/gnostic/blob/main/openapiv3/openapi-3.0.json
    * https://github.com/google/gnostic/blob/main/openapiv3/openapi-3.1.json
  * openapi-schema-pydantic
  * write some super basic classes that ignore most of the things
* merge openapi specs
  * how to handle unique fields, eg. spec.info.title?
