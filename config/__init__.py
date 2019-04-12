from os import path

from modular_conf import Config
from modular_conf.fields import BoolField


config = Config(path.join(path.dirname(path.abspath(__file__)), 'config.json'))


if __name__ == '__main__':
    config = Config('test.json')
    config.register_module('test_module', [BoolField('test', False), BoolField('test2', True)])
    config.load()
    config.save()
