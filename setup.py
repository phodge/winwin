from setuptools import find_packages, setup

setup(
    name='winwin',
    description='CLI Utility to open/manage termina/tmux/nvim windows',
    author='Peter Hodge',
    license='MIT',
    packages=['winwin'] + ['winwin.{}'.format(p)
                           for p in find_packages('winwin')],
    install_requires=['simplejson', 'click', 'libtmux', 'pyxdg'],
    entry_points={
        'console_scripts': ['winwin=winwin.cli:main'],
    },
    # automatic version number using setuptools_scm
    setup_requires=['setuptools_scm'],
    use_scm_version={
        "write_to": 'winwin/_version.py',
    },
)
