from flask import request
from pydantic import BaseModel, ValidationError


def parse_json(model: type[BaseModel]) -> BaseModel:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError.from_exception_data(
            model.__name__,
            [{'type': 'dict_type', 'loc': ('body',), 'msg': 'Тело запроса должно быть JSON-объектом', 'input': data}],
        )
    return model.model_validate(data)


def parse_query(model: type[BaseModel]) -> BaseModel:
    args = request.args.to_dict(flat=True)
    if 'my_task' in args:
        args['my_task'] = args['my_task'].lower() in ('1', 'true', 'yes', 'on')
    return model.model_validate(args)
