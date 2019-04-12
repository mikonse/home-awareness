import json


class Message(object):
    def __init__(self, type, data=None):
        self.type = type
        self.data = data

    def serialize(self):
        return json.dumps({
            'type': self.type,
            'data': self.data
        })

    def serialize_data(self):
        return json.dumps(self.data)

    @staticmethod
    def deserialize(value):
        obj = json.loads(value)
        return Message(obj.get('type'), obj.get('data'))
