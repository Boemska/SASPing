from base import Base

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
        super(Test, self).__init__(data)
