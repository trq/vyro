from vyro.util import AttrDict

env = AttrDict({
    'default_repo': 'trq',
    'paths': AttrDict({
        'root': '.vyro',
        'hooks': '.vyro/hooks',
        'cache': '.vyro/cache',
        'conf': '.vyro/conf',
        'stage': '.vyro/stage'
    }),
    'names': AttrDict({
        'repo_dir': 'repos'
    })
})
