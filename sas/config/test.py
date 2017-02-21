from base import Base
import re
import sre_compile

class Test(Base):
    _keys = [
        # key, required
        ('id', True),
        ('type', True),
        ('execPath', True),
        ('execParams', False),
        ('validations', False)
    ]

    def __init__(self, data):
        try:
            super(Test, self).__init__(data)
        except KeyError as e:
            if 'id' in data and data['id']:
                raise KeyError((e.message + " in config with id '{0}'").format(data['id']))
            else:
                raise e

        if self.get('execPath')[0] != '/':
            raise ValueError('Exec path must start with /')
        # if 'validations' is defuned, 'mustContain' and 'cantContain' must be also defined
        if self.get('validations') != None:
            if not('mustContain' in self.get('validations')):
                raise KeyError("Missing required 'mustContain' property in config with id '{0}'".format(self.get('id')))
            elif type(self.get('validations.mustContain')) != list:
                raise ValueError("Property 'mustContain' should be list")
            if not('cantContain' in self.get('validations')):
                raise KeyError("Missing required 'cantContain' property in config with id '{0}'".format(self.get('id')))
            elif type(self.get('validations.cantContain')) != list:
                raise ValueError("Property 'cantContain' should be list")

            for validation in (self.get('validations.mustContain') + self.get('validations.cantContain')):
                try:
                    re.compile(validation)
                except:
                    raise ValueError("Validation '{0}' is not a valid regular expression".format(validation))
