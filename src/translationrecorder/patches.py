from functools import wraps


def patch_zope(path, wrapper):
    try:
        import zope.i18n
    except ImportError:
        return False

    recorder = wrapper(zope.i18n.translate, path)
    zope.i18n.translate = wraps(zope.i18n.translate)(recorder)

    return True

def patch_translationstring(path, wrapper):
    try:
        import translationstring
    except ImportError:
        return False

    factory = translationstring.Translator

    @wraps(factory)
    def Translator(**kwargs):
        translator = factory(**kwargs)
        return wrapper(translator, path)

    translationstring.Translator = Translator

    return True
