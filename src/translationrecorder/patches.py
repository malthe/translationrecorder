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

        real_value = value

        # Register with utility; note that arguments appear in a
        # slightly different order.
        if mapping is not None:
            for key, string in mapping.items():
                value = value.replace(string, '${%s}' % key)

        recorder.register(
            value, msgid, domain, mapping, context, target_language, default
            )

        return real_value

    TranslationDomain.translate = wraps(TranslationDomain.translate)(translate)

    return True


def patch_translationstring(path, wrapper):
    try:
        import translationstring
    except ImportError:
        return False

    factory = translationstring.Translator

    @wraps(factory)
    def Translator(*args, **kwargs):
        translator = factory(*args, **kwargs)
        return wrapper(translator, path)

    translationstring.Translator = Translator

    chameleon_factory = translationstring.ChameleonTranslate

    @wraps(factory)
    def ChameleonTranslate(translator):
        translate = chameleon_factory(translator)
        if translator is not None:
            translate = wrapper(translate, path)
        return translate

    translationstring.ChameleonTranslate = ChameleonTranslate

    return True
