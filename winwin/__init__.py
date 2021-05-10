try:
    from winwin._version import version, version_tuple
except ImportError:
    version = '0.0.noversion'
    version_tuple = (0, 0, 'noversion')

__all__ = ['version', 'version_tuple']
