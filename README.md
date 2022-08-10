# OpenAPI Search Index

* extract relevant strings from openapi specifications
* tokenize them
* build searchable documents for each entity (route, path, overall api)
* build a search index over tokens
* provide a search method to query the index

## TODO

* [x] extract from openapi
  * [x] per-route and per-verb
  * [x] bunch of relevant strings
  * [ ] remove links from markdown to avoid searching url paths
  * [ ] tokenize content correctly into words 
* inverted index
  * add/update spec
    * try to avoid updating routes that didn't change
  * delete spec
  * list spec
* token index
  * add, remove
  * fuzzy query
* generate pydantic classes somehow
  * ~~datamodel-code-generator +~~ 
    * ~~https://github.com/google/gnostic/blob/main/openapiv2/openapi-2.0.json~~
    * ~~https://github.com/google/gnostic/blob/main/openapiv3/openapi-3.0.json~~
    * ~~https://github.com/google/gnostic/blob/main/openapiv3/openapi-3.1.json~~
  * ~~openapi-schema-pydantic~~
  * write some super basic classes that ignore most of the things
* merge openapi specs
  * how to handle unique fields, eg. spec.info.title?
  * also, how to handle refs?
  * does not need to be guaranteed correct, just reasonably best effort