"""
This file contains the config 'Section' class
"""


class Section(object):

    def __init__(self, *args):
        self.__header__ = str(args[0]) if args else None

    def __repr__(self):
        if self.__header__ is None:
            return super(Section, self).__repr__()
        return self.__header__

    def to_dict(self):
        d = {}
        for key in self.keys():
            v = getattr(self, str(key))
            if isinstance(v, Section):
                d[key] = v.to_dict()
            else:
                d[key] = v
        return d

    def keys(self):
        return self.__dict__.keys()

    def next(self):
        """ Fake iteration functionality.
        """
        raise StopIteration

    def __iter__(self):
        """ Fake iteration functionality.
        We skip magic attribues and Structs, and return the rest.
        """
        ks = self.keys()
        for k in ks:
            if not k.startswith('__') and not isinstance(k, Section):
                yield getattr(self, k)

    def __len__(self):
        """ Don't count magic attributes or Structs.
        """
        ks = self.__dict__.keys()
        return len([k for k in ks if not k.startswith('__') \
                    and not isinstance(k, Section)])
