import json
from os import path
from threading import RLock

from config.fields import BoolField


class Config:
    def __init__(self, file_path, format='json'):
        self.file_path = file_path
        self.format = format
        self.data = dict()  # module_name:item_name:ConfigField
        self.synced = False
        self._lock = RLock()

    def get(self, module, item):
        if module not in self.data or item not in self.data.get(module):
            raise KeyError(f'Config item {module}:{item} not in config')
        return self.data.get(module).get(item).value

    def set(self, module, item, value):
        with self._lock:
            if module not in self.data or item not in self.data.get(module):
                raise KeyError(f'Config item {module}:{item} not in config')
            self.data.get(module).get(item).value = value
            self.synced = False
        self.save()

    def __getitem__(self, item):
        # TODO: think about how this would work
        raise Exception('not implemented')

    def __setitem__(self, key, value):
        # TODO: think about how this would work
        raise Exception('not implemented')

    def register_module(self, module: str, items: list):
        with self._lock:
            self.data[module] = {item.name: item for item in items}

    def serialize(self, full=False):
        if full:
            return {
                module_name: [item.serialize() for item in module_items.values()]
                for module_name, module_items in self.data.items()
            }

        else:
            return {
                module_name: {
                    item.name: item.value for item in items.values()
                } for module_name, items in self.data.items()
            }

    def serialize_json(self, full=False):
        return json.dumps(self.serialize(full=full))

    def save(self, force=False):
        with self._lock:
            if not force and self.synced:
                return True

            try:
                data = self.serialize(full=False)
                if path.isfile(self.file_path):
                    with open(self.file_path, 'r') as f:
                        file_conf = json.load(f)
                        file_conf.update(data)
                        data = file_conf

                with open(self.file_path, 'w+') as f:
                    json.dump(data, f, indent=2)
                self.synced = True
                return True
            except Exception:
                return False

    def update(self, update, full=False):
        if not isinstance(update, dict):
            raise AttributeError('Expected dict')

        with self._lock:
            for module_name, module in update.items():
                if module_name not in self.data:
                    continue

                if full:
                    for item in module:
                        if item.get('name') in self.data.get(module_name):
                            self.data.get(module_name).get(item.get('name')).value = item.get('value')
                else:
                    for key, value in module.items():
                        if key in self.data.get(module_name):
                            self.data.get(module_name).get(key).value = value
            self.synced = False
        self.save()

    def load(self):
        if not path.isfile(self.file_path):
            self.save(force=True)
            return True

        with self._lock:
            with open(self.file_path, 'r') as f:
                file_conf = json.load(f)  # TODO: maybe catch exception?
                self.update(file_conf, full=False)
                return True

    def initialize(self):
        """
        Initializes the configuration. Only call after all modules registered their config parameters.
        """
        self.load()
        self.save(force=True)


config = Config(path.join(path.dirname(path.abspath(__file__)), 'config.json'))


if __name__ == '__main__':
    config = Config('test.json')
    config.register_module('test_module', [BoolField('test', False), BoolField('test2', True)])
    config.load()
    config.save()
