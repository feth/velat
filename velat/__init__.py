import warnings

version=0.1

try:
    from traits.api import HasTraits
except ImportError:
    import sys
    warnings.warn("Missing dependency: enthought.traits "
        "(Package 'python-traits' on debian and ubuntu)."
        "\nExiting.\n", ImportWarning)
    raise
