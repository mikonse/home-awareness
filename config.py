from os import path
import json

from log import LOG

CONFIG_FILE = path.join(path.dirname(path.abspath(__file__)), 'config.json')


WS_ROUTE = r'/ws/'
WS_HOST = '127.0.0.1'
WS_PORT = 12345

_initialized = False
_config = dict()
_dirty = False


def validate_module_config(config):
    for key, value in config.items():
        if not isinstance(value, dict) or not all(k in value for k in ('default', 'type')):
            return False
    return True


def resolve_string_type(type):
    if type == 'int':
        return int
    elif type == 'str':
        return str
    elif type == 'bool':
        return bool
    elif type == 'pair_list':
        return list
    else:
        raise AttributeError('Unknown type')


def apply_default(config):
    """
    Applies the default value to a module config. Assumes default parameter exists.

    Args:
        config (dict): module config
    """
    for item in config.values():
        item.update({'value': item['default']})


def register_module(name, config):
    """
    Register a module with a config dictionary. Example for config parameter:
    config = {
        "param1": {
            "default": 1,
            "type": "int"
        },
        "param2": {
            "default": "test",
            "type": "str"
        }
    }
    Args:
        name (str): module name
        config (dict): dictionary containing the config item specifications
    """
    global _config
    if name in _config:
        raise AttributeError(f'module {name} already registered')
    if not validate_module_config(config):
        raise AttributeError('malformed config dict')

    apply_default(config)
    _config[name] = config
    _load_module_config(name)


def _get_item(module, item):
    """
    Retrieve the config dict, containing default, type and value for a given module and item
    Args:
        module (str): module name
        item (str): config item name
    """
    if module not in _config or item not in _config.get(module):
        raise ValueError(f'Config does not contain item {item} for module {module}')
    return _config.get(module).get(item)


def _load_module_config(module):
    global _config, _dirty
    if not path.isfile(CONFIG_FILE):  # no config file exists, create a new one
        save_config()
        return

    with open(CONFIG_FILE, 'r') as f:
        file_conf = json.load(f)
        if module in file_conf:
            for key, value in file_conf.get(module).items():
                if key in _config.get(module) \
                        and isinstance(value, resolve_string_type(_config.get(module).get(key).get('type'))):
                    _config.get(module).get(key)['value'] = value
        else:
            _save_module_config(module)


def _save_module_config(module):
    if not path.isfile(CONFIG_FILE):  # no config file exists, create a new one
        save_config()
        return

    with open(CONFIG_FILE, 'r+') as f:
        file_conf = json.load(f)
        if module not in file_conf:  # module config present in file
            file_conf[module] = dict()
        for key, value in _config.get(module).items():
            file_conf.get(module)[key] = value.get('value')
        f.seek(0)
        json.dump(file_conf, f, indent=2)
        f.truncate()


def update_config(update):
    # TODO: do input sanitising
    global _config, _dirty
    if not isinstance(update, dict):
        raise AttributeError('Expected dictionary')

    for name, module in update.items():
        if name not in _config:
            LOG.warning(f'Found config for unknown module {name}')
            continue

        for key, value in module.items():
            if key in _config.get(name) \
                    and isinstance(value, resolve_string_type(_config.get(name).get(key).get('type'))):
                _config.get(name).get(key)['value'] = value

    _dirty = True


def update_pretty_config(update: list):
    # TODO: input sanitising
    internal = {
        module.get('name'): {
            item.get('name'): item.get('values').get('value')
            for item in module.get('items')
        } for module in update
    }
    print(internal)
    update_config(internal)


def load_config():
    """
    Load config values from CONFIG_FILE. Only key value pairs are stored there however.
    """
    global _config, _dirty
    if not path.isfile(CONFIG_FILE):  # no config file exists, create a new one
        save_config()
        return

    with open(CONFIG_FILE, 'r') as f:
        file_conf = json.load(f)
        update_config(file_conf)

    _dirty = False


def save_config(force=False):
    global _config, _dirty
    if _dirty or not path.isfile(CONFIG_FILE) or force:
        save_dict = {name: {key: value.get('value') for key, value in module.items()} for name, module in _config.items()}
        with open(CONFIG_FILE, 'w+') as f:
            json.dump(save_dict, f, indent=2)

        _dirty = False


def get_item(module, item):
    """
    Retrieve the config value for a given module and config item
    Args:
        module (str): module name
        item (str): config item name
    """
    return _get_item(module, item).get('value')


def set_item(module, item, value):
    global _config, _dirty
    item = _get_item(module, item)
    expected_type = resolve_string_type(item.get('type'))

    if not isinstance(value, expected_type):
        raise AttributeError(f'Provided value {value} does not match type {expected_type}')

    item['value'] = value
    _dirty = True
    save_config()


def get_config():
    return _config


def get_pretty_config():
    data = [
        {'name': module_name,
         'items': [
             {'name': name, 'values': values}
             for name, values in module_items.items()
         ]
         }
        for module_name, module_items in get_config().items()
    ]
    return data


def initialize():
    """
    Initializes the configuration. Only call after all modules registered their config parameters.
    """
    load_config()
    save_config(force=True)
    LOG.debug(f'Current config: {_config}')
