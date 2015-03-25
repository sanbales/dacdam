from __future__ import division

__all__ = ['Datafile']


class Datafile(SimpyMixin, object):
    def __init__(self, env, file_type=None, value=0.0, *args, **kwargs):

        super(Datafile, self).__init__(*args, **kwargs)

        self.file_type = 'data' if file_type is None else file_type
        self.value = value
