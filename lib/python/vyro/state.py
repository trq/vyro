class _AttrDict(dict):
    """
    Dictionary subclass enabling attribute lookup/assignment of keys/values.

    Blatantly stolen from fabric.
    https://github.com/fabric/fabric/blob/master/fabric/utils.py#L157 
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # to conform with __getattr__ spec
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

env = _AttrDict({
    'default_repo': 'trq',
    'paths': _AttrDict({
        'root': '.vyro',
        'hooks': '.vyro/hooks',
        'stage': '.vyro/stage'
    }),
    'names': _AttrDict({
        'repo_dir': 'repos'
    })
})
