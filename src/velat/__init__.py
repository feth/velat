version=0.1

try:
    from enthought.traits.api import HasTraits
except ImportError:
    from sys import stderr
    stderr.write(
        "Missing dependency: enthought.traits "
        "(Package 'python-traits' on debian and ubuntu)."
        "\nExiting.\n"
    )
    exit(2)
