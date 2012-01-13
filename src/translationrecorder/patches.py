from functools import wraps


def patch_zope(path, wrapper):
    try:
        from zope.i18n.translationdomain import TranslationDomain
    except ImportError:
        return False

    recorder = wrapper(None, path)
    translator = TranslationDomain.translate

    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        domain = self.domain

        # Call translation domain to get value
        value = translator(
            self, msgid, mapping, context, target_language, default
            )

        # Register with utility; note that arguments appear in a
        # slightly different order.
        recorder.register(
            value, msgid, domain, mapping, context, target_language, default
            )

        return value

    TranslationDomain.translate = wraps(TranslationDomain.translate)(translate)

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
