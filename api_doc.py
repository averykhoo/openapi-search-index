import json
from typing import List
from urllib.parse import quote

import tabulate as tabulate
from pydantic import BaseModel


class ParameterInfo(BaseModel):
    name: str
    description: str


# service -> path -> endpoint -> param, tag

class EndpointInfo(BaseModel):
    service_hostname: str
    service_title: str
    service_description: str

    path_summary: str
    path_description: str

    endpoint_verb: str
    endpoint_path: str
    endpoint_parameters: List[ParameterInfo]

    openapi_operation_id: str
    openapi_summary: str
    openapi_description: str
    openapi_tags: List[str]

    @property
    def service_name(self):
        return self.service_hostname.split('.', 1)[0]  # only works if there are never any subdomains

    @property
    def openapi_fragment(self):
        return f'#/{quote((self.openapi_tags + ["default"])[0])}/{quote(self.openapi_operation_id)}'

    @property
    def dedupe_id(self):
        return f'`{self.endpoint_verb.upper()}` {self.service_hostname or ""}/{self.endpoint_path}'

    @property
    def content(self):
        """
        content optimized for search
        it also happens to be valid markdown

        :return:
        """
        _content = []
        if self.service_title.strip():
            _content.append(f'# {self.service_title.strip()}')
        if self.service_description.strip():
            _content.append(self.service_description.strip())

        if _content and _content[-1]:
            _content.append('')
        if self.path_summary.strip():
            _content.append(self.path_summary.strip())
        if self.path_description.strip():
            _content.append(self.path_description.strip())

        if _content and _content[-1]:
            _content.append('')
        if self.endpoint_verb:
            _content.append(f'`{self.endpoint_verb.upper()}` {self.service_name}{self.endpoint_path}')

        if _content and _content[-1]:
            _content.append('')
        if self.endpoint_parameters:
            _content.append(tabulate.tabulate([(p.name, p.description) for p in self.endpoint_parameters],
                                              headers=['', ''],
                                              tablefmt='github'))
            # for p in self.endpoint_parameters:
            #     content.append(f'\t{p.name}\t:\t{p.description}')

        if _content and _content[-1]:
            _content.append('')
        if self.openapi_summary.strip():
            _content.append(self.openapi_summary.strip())
        if self.openapi_description.strip():
            _content.append(self.openapi_description.strip())

        if _content and _content[-1]:
            _content.append('')
        _content.append('\t'.join(f'`#{quote(tag)}`' for tag in self.openapi_tags))

        return '\n'.join(_content).rstrip()


def parse_openapi(path: str, service_hostname: str):
    with open(path, encoding='utf8') as f:
        data = json.load(f)

    service_title = data.get('info', dict()).get('title', '').strip()
    service_description = data.get('info', dict()).get('description', '').strip()

    all_tags = []
    for path, path_item in list(data.get('paths', dict()).items()) + list(data.get('webhooks', dict()).items()):
        path_tags = []
        path_summary = path_item.get('summary', '').strip()
        path_description = path_item.get('description', '').strip()
        for verb, operation in path_item.items():
            if verb in {'summary', 'description'}:
                continue
            if '$ref' in operation:
                continue
            tags = operation.get('tags', []) or ['default']
            summary = operation.get('summary', '').strip()
            description = operation.get('description', '').strip()
            operation_id = operation.get('operationId', '').strip()
            parameters = operation.get('parameters', [])

            _parameters = [ParameterInfo(name=p.get('name', '').strip(),
                                         description=p.get('description', '').strip(),
                                         ) for p in parameters]

            if operation.get('requestBody', dict()).get('description', '').strip():
                _parameters.append(ParameterInfo(name='*BODY*',
                                                 description=operation['requestBody']['description'].strip()))

            path_tags.extend(tags)
            yield EndpointInfo(service_hostname=service_hostname,
                               service_title=service_title,
                               service_description=service_description,
                               path_summary=path_summary,
                               path_description=path_description,
                               endpoint_verb=verb,
                               endpoint_path=path,
                               endpoint_parameters=_parameters,
                               openapi_operation_id=operation_id,
                               openapi_summary=summary,
                               openapi_description=description,
                               openapi_tags=tags,
                               )

        # somehow we have a path with no verbs, so emit an endpoint with no verb
        if not path_tags:
            path_tags.append(None)
            yield EndpointInfo(service_hostname=service_hostname,
                               service_title=service_title,
                               service_description=service_description,
                               path_summary=path_summary,
                               path_description=path_description,
                               endpoint_verb='',
                               endpoint_path=path,
                               endpoint_parameters=[],
                               openapi_operation_id='',
                               openapi_summary='',
                               openapi_description='',
                               openapi_tags=[],
                               )

        all_tags.extend(path_tags)

    # we have an openapi spec with no paths that have verbs, so emit an endpoint with nothing
    if not list(filter(None, all_tags)):
        yield EndpointInfo(service_hostname=service_hostname,
                           service_title=service_title,
                           service_description=service_description,
                           path_summary='',
                           path_description='',
                           endpoint_verb='',
                           endpoint_path='',
                           endpoint_parameters=[],
                           openapi_operation_id='',
                           openapi_summary='',
                           openapi_description='',
                           openapi_tags=[],
                           )


if __name__ == '__main__':
    # for endpoint_info in parse_openapi('test-uspto.json', 'uspto.example'):
    # for endpoint_info in parse_openapi('test-petstore.json', 'petstore.example'):
    # for endpoint_info in parse_openapi('test-v2.0.json', 'swagger-v2.0.example'):
    # for endpoint_info in parse_openapi('test-v3.1.json', 'openapi-v3.1.example'):
    for endpoint_info in parse_openapi('test-link-example.json', 'link.example'):
        print()
        print('-' * 100)
        print()
        print(endpoint_info.content)
        print()
        print('-' * 100)
        print()
