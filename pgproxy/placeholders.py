NUMBER = "N"
SCHEMA = "schema"
PROC = "proc"
PROCS = "procs"
AFTER_ALL_MARKER = "after-all"
TMPL_SUFFIX = ".tmpl"


def ph(p):
    return "${%s}" % p


def interpret_name(name, n, schema="", proc=""):
    return name.replace(ph(NUMBER), "{:03d}".format(n)) \
        .replace(ph(SCHEMA), schema) \
        .replace(ph(PROC), proc) \
        .replace(ph(AFTER_ALL_MARKER), "") \
        .replace(TMPL_SUFFIX, "")


def is_schema_related_only(name):
    return name.count(ph(SCHEMA)) > 0 \
        and name.count(ph(PROC)) == 0 \
        and name.count(ph(AFTER_ALL_MARKER)) == 0


def is_proc_related(name):
    return name.count(ph(PROC)) > 0 \
        and name.count(ph(AFTER_ALL_MARKER)) == 0


def is_after_all(name):
    return name.count(ph(SCHEMA)) == 0 \
        and name.count(ph(PROC)) == 0 \
        and name.count(ph(AFTER_ALL_MARKER)) > 0
