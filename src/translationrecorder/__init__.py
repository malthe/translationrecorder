import os
import logging
import datetime
import patches
import atexit
import glob

logger = logging.getLogger("translationrecorder")
global_handlers = {}


try:
    from pycountry import languages

    def get_language_name(code):
        if code is None:
            return ""

        language = languages.get(alpha2=code)
        if language is not None:
            return language.name

except ImportError:
    logger.warn("Not able to translate language code to name "
                "(requires `pycountry` module).")

    def get_language_name(code):
        return ""


def quote(string):
    return string.replace('"', '\"').replace('\n', '\\n')


def unquote(string):
    return string.strip('"').replace('\\n', '\n')


def safe_encode(string, encoding='utf-8'):
    if string is None:
        return

    if not isinstance(string, str):
        string = unicode(string).encode(encoding)

    return string


def write_pot(path, domain, messages, language=None, encoding="utf-8"):
    if language is None:
        filename = os.path.join(path, "%s.pot" % domain)
    else:
        language_path = os.path.join(path, language, 'LC_MESSAGES')
        if not os.path.exists(language_path):
            os.makedirs(language_path)

        filename = os.path.join(language_path, "%s.po" % domain)

    time = datetime.datetime.now()

    with open(filename, 'w') as f:
        f.write('msgid ""\n')
        f.write('msgstr ""\n')

        write_header(f, "Project-Id-Version", "PACKAGE VERSION")
        write_header(f, "POT-Creation-Date", time.isoformat())
        write_header(f, "PO-Revision-Date", "YEAR-MO-DA HO:MI +ZONE")
        write_header(f, "Last-Translator", "FULL NAME <EMAIL@ADDRESS>")
        write_header(f, "Language-Team", "LANGUAGE <LL@li.org>")
        write_header(f, "MIME-Version", "1.0")
        write_header(f, "Content-Type", "text/plain; charset=utf-8")
        write_header(f, "Content-Transfer-Encoding", "8bit")
        write_header(f, "Plural-Forms", "nplurals=1; plural=0")
        write_header(f, "Language-Code", language or "en")
        write_header(f, "Language-Name", get_language_name(language))
        write_header(f, "Preferred-Encodings", encoding)
        write_header(f, "Domain", domain)

        f.write('\n')

        for msgid, (default, location, msgstr) in sorted(messages.items()):
            if default and default != msgid:
                f.write('#. Default: "%s"\n' % quote(default))

            if location:
                f.write('#: %s\n' % quote(location))

            f.write('msgid "%s"\n' % quote(msgid))
            f.write('msgstr "%s"\n\n' % quote(msgstr))


def write_header(f, header, value):
    f.write('"%s: %s\\n"\n' % (header, value))


def load_language(path, language, catalog):
    default = location = msgid = None

    processed = 0
    with open(path, 'r') as f:
        for line in f:
            if line.startswith('#.'):
                default = unquote(line.split('Default:', 1)[1].strip())

            if line.startswith('#:'):
                location = line[2:].strip()

            if line.startswith('msgid'):
                msgid = unquote(line[5:].strip())

            if line.startswith('msgstr'):
                msgstr = unquote(line[6:].strip())

                catalog[msgid, language] = (default, location, msgstr)
                processed += 1
                default = location = msgid = None

    return processed


def glob_domains(path):
    for pot_path in glob.iglob("%s/*.po*" % path):
        domain = os.path.splitext(os.path.basename(pot_path))[0]

        if domain == 'DEFAULT':
            domain = None

        yield pot_path, domain


def load_catalogs(path, domains, language=None):
    # Templates
    for pot_path, domain in glob_domains(path):
        catalog = domains.setdefault(domain, {})
        count = load_language(pot_path, language, catalog)

        if language is None:
            info = ''
        else:
            info = ' (%s)' % language

        logger.info("processed %d definitions for '%s'%s." % (
            count, domain or 'DEFAULT', info
            ))

    # Languages
    for language in os.listdir(path):
        messages_path = os.path.join(path, language, 'LC_MESSAGES')
        if os.path.exists(messages_path):
            load_catalogs(messages_path, domains, language)


class Recorder(object):
    """Proxies translation attempts to the provided ``translator`` and
    records them in ``<domain>.pot`` translation templates on disk
    when the configured signal is fired.

    The provided path must exist. Typically the path will end in a
    directory named 'locales'.
    """

    def __init__(self, translator, path):
        self.translator = translator

        domains = global_handlers.get(path)
        if domains is None:
            domains = global_handlers[path] = {}

            load_catalogs(path, domains)

            def handler(logger=logger, domains=domains, path=path):
                count = len(domains)
                if not count:
                    return

                logger.info("Writing out .pot files for %d domains..." % count)

                count = 0
                for domain, catalog in domains.items():
                    if not catalog:
                        continue

                    if domain is None:
                        domain = "DEFAULT"

                    messages = {}
                    languages = {}

                    for (msgid, language), translation in catalog.items():
                        default, location, msgstr = translation
                        messages.setdefault(msgid, (default, location, ""))

                        if language:
                            languages.setdefault(language, {})[msgid] = (
                                translation)

                    catalogs = [(None, messages)]
                    catalogs.extend(languages.items())

                    for language, messages in catalogs:
                        try:
                            write_pot(path, domain, messages, language)
                        except IOError, exc:
                            logger.warn(exc)
                        except os.error, exc:
                            logger.warn(exc)
                        else:
                            count += 1

                logger.info("Wrote %d translation file(s) at %s." % (
                    count, path
                    ))

            atexit.register(handler)

        self.domains = domains

    def __call__(self, msgid, *args, **kwargs):
        value = self.translator(msgid, *args, **kwargs)

        if msgid:
            self.register(value, msgid, *args, **kwargs)

        return value

    def register(self, value, msgid, domain=None, mapping=None,
                 context=None, target_language=None, default=None):
        catalog = self.domains.get(domain)
        if catalog is None:
            catalog = self.domains[domain] = {}

        catalog[safe_encode(msgid), target_language] = (
            safe_encode(default), None, safe_encode(value)
            )


path = os.environ.get('RECORD_TRANSLATIONS')
if path is not None:
    path = os.path.abspath(path)

    if not os.path.exists(path):
        logger.warn("Path does not exist: %s." % path)
    else:
        patched = 0

        if patches.patch_zope(path, Recorder):
            logger.info("patched zope.i18n.")
            patched += 1

        if patches.patch_translationstring(path, Recorder):
            logger.info("patched translationstring.")
            patched += 1

        if patched:
            logger.info(
                "configured to write .pot files in: %s." % path
                )
