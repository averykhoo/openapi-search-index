from dataclasses import dataclass
from pprint import pprint
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from urllib.parse import quote

from pydantic import BaseModel


@dataclass
class Document:
    path: str
    docs_paths: Tuple[str]
    operation: str
    name: str
    summary: str
    description: str
    parameters: Tuple[Tuple[str, str]]
    tags: Tuple[str]


class Info(BaseModel):
    title: str
    description: Optional[str] = None
    summary: Optional[str] = None


# not super useful
# class Server(BaseModel):
#     url: str
#     description: Optional[str] = None


# not useful at all
# class Ref(BaseModel):
#     ref: str = Field(alias="$ref")


class Parameter(BaseModel):
    name: Optional[str] = None  # make this optional so it parses refs too
    description: Optional[str] = None


# not super useful
# class Response(BaseModel):
#     description: str


class Operation(BaseModel):
    # responses: Dict[str, Union[Response, Ref]]
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    operationId: Optional[str] = None  # needed to navigate to operation
    parameters: Optional[List[Parameter]] = None


class PathItem(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    # servers: Optional[List[Server]] = None
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

    # servers: Optional[List[Server]] = None
    # components: Optional[Dict[str, Dict[str, Any]]]

    def get_documents(self):
        all_tags: Set[str] = set()

        for api_path, api_path_item in self.paths.items():
            summary = (api_path_item.summary or '').strip() or None
            description = (api_path_item.description or '').strip() or None

            def _create_document(op_name: str, op: Operation):
                docs_paths = []
                for tag in (op.tags or ['default']):
                    all_tags.add(tag)
                    if op.operationId:
                        docs_paths.append(f'#/{quote(tag)}/{quote(op.operationId)}')
                params = []
                for param in (op.parameters or []):
                    _name = (param.name or '').strip()
                    _description = (param.description or '').strip()
                    if _name or _description:
                        params.append((_name, _description))
                return Document(api_path,
                                docs_paths=tuple(docs_paths),
                                operation=op_name,
                                name='',
                                summary=(op.summary or '').strip() or summary,
                                description=(op.description or '').strip() or description,
                                tags=tuple(op.tags) if op.tags else tuple(),
                                parameters=tuple(params),
                                )

            if summary or description:
                yield Document(api_path,
                               docs_paths=tuple(),
                               summary=summary,
                               description=description,
                               operation='op_name',
                               name='',
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
                       docs_paths=tuple(['#']),
                       name=self.info.title.strip(),
                       summary=(self.info.summary or '').strip(),
                       description=(self.info.description or '').strip(),
                       tags=tuple(all_tags),
                       operation='',
                       parameters=tuple(),
                       )


if __name__ == '__main__':
    pprint(list(OpenAPI.parse_file('test-petstore.json').get_documents()))
    pprint(list(OpenAPI.parse_file('test-uspto.json').get_documents()))
