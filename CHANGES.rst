Changes
=======

1.0.2 (2012-01-13)
------------------

- Fixed issue where a quote appearing in a message id or translation
  would corrupt on save.

1.0.1 (2012-01-13)
------------------

- Fixed issue where generated .po-files would result in a syntax error
  on compilation using ``pythongettext`` due to a missing initial
  dummy message translation.

- Patch the translation domain instead of the (higher-level)
  global translation function.

  This fixes an issue where messages would not be recorded with the
  proper translation domain and the used target languages would not be
  correctly registered.

1.0 (2011-11-28)
----------------

- Initial public release.
