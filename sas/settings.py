import operator

class Settings:
    _keys = [
        # key, required
        ('id', True),
        ('type', True),
        ('execUrl', True),
        ('loginUrl', True),
        ('execParams', False),
        ('loginParams', True),
        ('validations', False)
    ]

    def __init__(self, d):
        for key in d:
            self._validateKey(key)

        for key in self._keys:
            if key[1] and not(key[0] in d):
                raise KeyError('Missing required config property ' + key[0])

        self._data = d

    def _validateKey(self, key):
        # key.split('.')[0] to use only first level property
        if not(key.split('.')[0] in [i[0] for i in self._keys]):
            raise KeyError('Wrong settings key ' + key)

    def _dotNotationGet(self, key):
        keys = key.split('.')
        lastPlace = reduce(operator.getitem, keys[:-1], self._data)
        return lastPlace[keys[-1]]

    def _dotNotationSet(self, key, value):
        keys = key.split('.')
        lastPlace = reduce(operator.getitem, keys[:-1], self._data)
        lastPlace[keys[-1]] = value

    def getAll(self):
        return self._data

    def get(self, key):
        self._validateKey(key)
        return self._dotNotationGet(key)

    def set(self, key, value):
        self._validateKey(key)
        self._dotNotationSet(key, value)
