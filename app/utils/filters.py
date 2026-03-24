import base64


# Фильтр для кодирования данных в base64
def b64encode_filter(data):
    if data:
        return base64.b64encode(data).decode('utf-8')
    return None









