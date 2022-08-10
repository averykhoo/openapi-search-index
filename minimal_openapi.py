from dataclasses import dataclass
from pprint import pprint
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from urllib.parse import quote

from pydantic import BaseModel


def string_similarity(query, text):
    return sum(word in text.casefold() for word in query.casefold().split())


@dataclass
class Document:
    path: str
    docs_fragments: Tuple[str]
    api_name: str
    summary: str
    description: str
    parameters: Tuple[Tuple[str, str]]  # (param name, param description)
    tags: Tuple[str]  # maybe an optional tag instead?
    operation: str
    # generate a dedupe id of some kind

    def match(self, query):
        return (
            string_similarity(query, self.api_name),
            max(string_similarity(query, self.summary),
                string_similarity(query, self.description),
                string_similarity(query, self.path)),
            sum(string_similarity(query, ' '.join(param)) for param in self.parameters),
            string_similarity(query, ' '.join(self.tags)),
            string_similarity(query, self.operation)
        )


class Info(BaseModel):
    title: str
    description: Optional[str] = None
    summary: Optional[str] = None


class Parameter(BaseModel):
    name: Optional[str] = None  # make this optional so it parses refs too
    description: Optional[str] = None


class Operation(BaseModel):
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    operationId: Optional[str] = None  # needed to navigate to operation
    parameters: Optional[List[Parameter]] = None


class PathItem(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    get: Optional[Operation] = None
    put: Optional[Operation] = None
    post: Optional[Operation] = None
    delete: Optional[Operation] = None
    options: Optional[Operation] = None
    head: Optional[Operation] = None
    patch: Optional[Operation] = None
    trace: Optional[Operation] = None


class OpenAPI(BaseModel):
    info: Info
    paths: Dict[str, PathItem]

    def get_documents(self):
        all_tags: Set[str] = set()

        for api_path, api_path_item in self.paths.items():
            summary = (api_path_item.summary or '').strip() or ''
            description = (api_path_item.description or '').strip() or ''

            def _create_document(op_name: str, op: Operation):
                docs_fragments = []
                for tag in (op.tags or ['default']):
                    all_tags.add(tag)
                    if op.operationId:
                        docs_fragments.append(f'#/{quote(tag)}/{quote(op.operationId)}')
                params = []
                for param in (op.parameters or []):
                    _name = (param.name or '').strip()
                    _description = (param.description or '').strip()
                    if _name or _description:
                        params.append((_name, _description))
                return Document(api_path,
                                docs_fragments=tuple(docs_fragments),
                                operation=op_name,
                                api_name=self.info.title.strip(),
                                summary=(op.summary or '').strip() or summary,
                                description=(op.description or '').strip() or description,
                                tags=tuple(op.tags) if op.tags else tuple(),
                                parameters=tuple(params),
                                )

            if summary or description:
                yield Document(api_path,
                               docs_fragments=tuple(),
                               summary=summary,
                               description=description,
                               operation='op_name',
                               api_name=self.info.title.strip(),
                               tags=tuple(),
                               parameters=tuple(),
                               )
            if api_path_item.get is not None:
                yield _create_document('GET', api_path_item.get)
            if api_path_item.put is not None:
                yield _create_document('PUT', api_path_item.put)
            if api_path_item.post is not None:
                yield _create_document('POST', api_path_item.post)
            if api_path_item.delete is not None:
                yield _create_document('DELETE', api_path_item.delete)
            if api_path_item.options is not None:
                yield _create_document('OPTIONS', api_path_item.options)
            if api_path_item.head is not None:
                yield _create_document('HEAD', api_path_item.head)
            if api_path_item.patch is not None:
                yield _create_document('PATCH', api_path_item.patch)
            if api_path_item.trace is not None:
                yield _create_document('TRACE', api_path_item.trace)

        yield Document('/',
                       docs_fragments=tuple(['#']),
                       api_name=self.info.title.strip(),
                       summary=(self.info.summary or '').strip(),
                       description=(self.info.description or '').strip(),
                       tags=tuple(all_tags),
                       operation='',
                       parameters=tuple(),
                       )


if __name__ == '__main__':
    pprint(sorted(list(OpenAPI.parse_file('test-petstore.json').get_documents()) +
                  list(OpenAPI.parse_file('test-uspto.json').get_documents()),
                  key=lambda d: d.match('create pet'),
                  reverse=True))
