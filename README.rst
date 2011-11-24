Overview
--------

Enable the translation recorder by wrapping an existing translation
function::

  import zope.i18n
  import translationrecorder

  zope.i18n.translate = translationrecorder.recording_translator(
      zope.i18n.translate, './locales'
      )

For each registered path, an ``atexit`` handler is registered. It
writes the recorded messages to disk when the process exits.


Framework integration
---------------------

If the environment variable ``RECORD_TRANSLATIONS`` is set to a valid
path, the module will attempt to wrap the following functions or
classes in a translation recorder:

  ``zope.i18n.translate``
  ``translationstring.Translator``

Note that the ``translationrecorder`` module must be imported for the
wrapping to occur::

  import translationrecorder

This is not required for Plone which is configured to automatically
include the module.


Author
------

Malthe Borch <mborch@gmail.com>
