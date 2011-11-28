Overview
--------

The recorder is attached to an existing translation function keeps
track of the inputs and outputs.

The result is a *locales* directory structure::

  <domain>.pot
  <lang>/
  <lang>/LC_MESSAGES
  <lang>/LC_MESSAGES/<domain>.po
  ...

This structure is written on process exit.

Note that when the recorder is initialized, it imports any existing
message catalog. That is, it's robust to process startup/shutdown and
can operate continuously.

Usage
-----

In Python-code, enable the translation recorder by wrapping an
existing translation function.

The easiest way to wire this up is by patching the module that holds
the function (if possible)::


  import zope.i18n
  import translationrecorder

  # Patch Zope's translation function
  zope.i18n.translate = translationrecorder.Recorder(
      zope.i18n.translate, './locales'
      )


Framework Integration
---------------------

There's integration included for the Pyramid and Zope/Plone
frameworks.

Set the environment variable ``RECORD_TRANSLATIONS`` to an existing
*locales* directory and run your server process::

  $ mkdir ./locales
  $ RECORD_TRANSLATIONS=./locales bin/paster serve ...

This requires that the `translationrecorder` module is imported. This
is handled automatically on Plone. For other systems::

  import translationrecorder

Technically, the package applies patches against the global
translation functions of the applicable frameworks.


Author
------

Malthe Borch <mborch@gmail.com>
