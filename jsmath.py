from .jsmath_markdown_extension import JsMathExtension


def configure_typogrify(pelicanobj):
    """Instructs Typogrify to ignore math tags - which allows Typogrify
    to play nicely with math related content.

    Modified from Pelican's render_math plugin.
    """

    # If Typogrify is not being used, then just exit
    if not pelicanobj.settings.get('TYPOGRIFY', False):
        return

    try:
        import typogrify
        from distutils.version import LooseVersion

        if LooseVersion(typogrify.__version__) < LooseVersion('2.0.7'):
            raise TypeError('Incorrect version of Typogrify')

        from typogrify.filters import typogrify

        # At this point, we are happy to use Typogrify, meaning
        # it is installed and it is a recent enough version
        # that can be used to ignore all math
        # Instantiate markdown extension and append it to the current extensions
        pelicanobj.settings['TYPOGRIFY_IGNORE_TAGS'].extend(['.math', 'script'])  # ignore math class and script

    except (ImportError, TypeError) as e:
        pelicanobj.settings['TYPOGRIFY'] = False  # disable Typogrify

        if isinstance(e, ImportError):
            print("\nTypogrify is not installed, so it is being ignored.\nIf you want to use it, please install via: pip install typogrify\n")

        if isinstance(e, TypeError):
            print("\nA more recent version of Typogrify is needed for the render_math module.\nPlease upgrade Typogrify to the latest version (anything equal or above version 2.0.7 is okay).\nTypogrify will be turned off due to this reason.\n")


def jsmath_for_rst(pelicanobj):
    docutils_settings = pelicanobj.settings.get('DOCUTILS_SETTINGS', {})
    docutils_settings.setdefault('math_output', 'JsMath')
    pelicanobj.settings['DOCUTILS_SETTINGS'] = docutils_settings


def jsmath_for_markdown(pelicanobj):
    if not JsMathExtension:
        return

    extension = JsMathExtension()
    pelicanobj.settings['MARKDOWN'].setdefault('extensions', []).append(extension)


def pelican_init(pelicanobj):
    configure_typogrify(pelicanobj)
    jsmath_for_markdown(pelicanobj)
    jsmath_for_rst(pelicanobj)
