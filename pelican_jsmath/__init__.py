from . import jsmath
from pelican import signals


def register():
    signals.initialized.connect(jsmath.pelican_init)
