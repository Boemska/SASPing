import operator

class Settings:
    _keys = [
        # key, required
        ('id', True),
        ('type', True),
        ('execUrl', True),
        ('loginUrl', False),
        ('execParams', False),
        ('loginParams', True),
        ('loginParams.username', True),
        ('loginParams.password', True),
        ('validations', False)
    ]

    def __init__(self, d):
        for key in d:
            self._validateKey(key)

        for key in self._keys:
            if key[1] and not(self._dotNotationGet(key[0], d)):
                raise KeyError('Missing required config property "{0}" in config with id "{1}"'.format(key[0], d['id']))

        self._data = d

    def _validateKey(self, key):
        # key.split('.')[0] to use only first level property
        if not(key.split('.')[0] in [i[0] for i in self._keys]):
            raise KeyError('Wrong settings key "{0}"'.format(key))

    @staticmethod
    def _dotNotationGet(key, obj):
        keys = key.split('.')
        while keys:
            key = keys.pop(0)
            if key in obj:
                obj = obj[key]
            else:
                return None
        return obj

    @staticmethod
    def _dotNotationSet(key, value, obj):
        keys = key.split('.')
        while len(keys) > 1:
            key = keys.pop(0)
            if not(key in obj):
                obj[key] = {}
            obj = obj[key]
        obj[keys.pop(0)] = value

    def getAll(self):
        return self._data

    def get(self, key):
        self._validateKey(key)
        return self._dotNotationGet(key, self._data)

    def set(self, key, value):
        self._validateKey(key)
        self._dotNotationSet(key, value, self._data)
