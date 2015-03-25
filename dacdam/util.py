from __future__ import division

import re
import logging
import simpy

__all__ = ['snake_case', 'pluralize', 'SimpyMixin']


ABERRANT_PLURAL_MAP = {
    'appendix': 'appendices',
    'barracks': 'barracks',
    'cactus': 'cacti',
    'child': 'children',
    'criterion': 'criteria',
    'deer': 'deer',
    'echo': 'echoes',
    'elf': 'elves',
    'embargo': 'embargoes',
    'focus': 'foci',
    'fungus': 'fungi',
    'goose': 'geese',
    'hero': 'heroes',
    'hoof': 'hooves',
    'index': 'indices',
    'knife': 'knives',
    'leaf': 'leaves',
    'life': 'lives',
    'man': 'men',
    'mouse': 'mice',
    'nucleus': 'nuclei',
    'person': 'people',
    'phenomenon': 'phenomena',
    'potato': 'potatoes',
    'self': 'selves',
    'syllabus': 'syllabi',
    'tomato': 'tomatoes',
    'torpedo': 'torpedoes',
    'veto': 'vetoes',
    'woman': 'women',
    }

VOWELS = set('aeiou')


def snake_case(camel_case_str):
    """ Converts a 'CamelCase' string into a 'snake_case' string """
    snake_case_str = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_case_str).lower()


def pluralize(singular):
    """Return plural form of given lowercase singular word (English only). Based on
    ActiveState recipe http://code.activestate.com/recipes/413172/

    >>> pluralize('')
    ''
    >>> pluralize('goose')
    'geese'
    >>> pluralize('dolly')
    'dollies'
    >>> pluralize('genius')
    'genii'
    >>> pluralize('jones')
    'joneses'
    >>> pluralize('pass')
    'passes'
    >>> pluralize('zero')
    'zeros'
    >>> pluralize('casino')
    'casinos'
    >>> pluralize('hero')
    'heroes'
    >>> pluralize('church')
    'churches'
    >>> pluralize('x')
    'xs'
    >>> pluralize('car')
    'cars'

    """
    if not singular:
        return ''
    plural = ABERRANT_PLURAL_MAP.get(singular)
    if plural:
        return plural
    root = singular
    try:
        if singular[-1] == 'y' and singular[-2] not in VOWELS:
            root = singular[:-1]
            suffix = 'ies'
        elif singular[-1] == 's':
            if singular[-2] in VOWELS:
                if singular[-3:] == 'ius':
                    root = singular[:-2]
                    suffix = 'i'
                else:
                    root = singular[:-1]
                    suffix = 'ses'
            else:
                suffix = 'es'
        elif singular[-2:] in ('ch', 'sh'):
            suffix = 'es'
        else:
            suffix = 's'
    except IndexError:
        suffix = 's'
    plural = root + suffix
    return plural


def clean_kwargs(obj, kwargs):
    keys = obj.__init__.im_func.func_code.co_varnames
    for key in kwargs:
        if key not in keys:
            _ = kwargs.pop(key)
    return kwargs


def set_env(self, args, kwargs):
    if 'env' not in kwargs or (len(args) > 0 and \
        not isinstance(args[0], simpy.Environment)):
        kwargs['env'] = self.env
    return kwargs

class SimpyMixin(object):
    def __init__(self, env, *args, **kwargs):
        if not isinstance(env, simpy.Environment):
            raise ValueError("'env' must be a <simpy.Environment> object not an object of type <{}>.".format(type(env).__name__))

        self.env = env

    @property
    def now(self):
        return self.env.now

    def process(self, *args, **kwargs):
        return self.env.process(*args, **kwargs)

    def timeout(self, *args, **kwargs):
        return self.env.timeout(*args, **kwargs)

    def store(self, *args, **kwargs):
        kwargs = set_env(self, args, kwargs)
        return simpy.Store(*args, **kwargs)

    def filter_store(self, *args, **kwargs):
        kwargs = set_env(self, args, kwargs)
        return simpy.FilterStore(*args, **kwargs)

    def container(self, *args, **kwargs):
        kwargs = set_env(self, args, kwargs)
        return simpy.Container(*args, **kwargs)

    def resource(self, *args, **kwargs):
        kwargs = set_env(self, args, kwargs)
        return simpy.Resource(*args, **kwargs)

    def preemtive_resource(self, *args, **kwargs):
        kwargs = set_env(self, args, kwargs)
        return simpy.PreemptiveResource(*args, **kwargs)

    def priority_resource(self, *args, **kwargs):
        kwargs = set_env(self, args, kwargs)
        return simpy.PriorityResource(*args, **kwargs)
