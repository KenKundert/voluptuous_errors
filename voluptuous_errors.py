# DESCRIPTION {{{1
# Provides a convenience function used for reporting voluptuous errors when
# using with NestedText and inform.  Uses Inform's error() function when
# reporting the errors as it allows for multiple errors to be reported.

# IMPORTS {{{1
from inform import cull, error, errors_accrued, full_stop, is_array, is_mapping
import nestedtext as nt

# GLOBALS {{{1
voluptuous_error_msg_mappings = {
    "extra keys not allowed": ("unknown key", "key"),
    "expected a dict": ("expected a key-value pair", "value"),
    "expected a dictionary": ("expected a key-value pair", "value"),
    "required key not provided": ("required key is missing", "value"),
}
__version__ = '0.1'
__released__ = '2026-06-28'

# _nested_getvalue() {{{1
def _nested_getvalue(data, path):
    for item_index in path:
        try:
            data = data[item_index]
        except (KeyError, IndexError, TypeError):
            # The index is not present in the dictionary, list or other
            # indexable or data is not subscriptable
            return None
    return data

# _summarize_value() {{{1
def _summarize_value(value):
    if is_array(value):
        return 'list'
    if is_mapping(value):
        return 'key-value pair'
    value = repr(value)
    if len(value) > 20:
        return value[:20] + ' ...'
    return value

# report_voluptuous_errors() {{{1
def report_voluptuous_errors(
    multiple_invalid, data=None, *,
    keymap=None, source=None, sep="›", path_fmt="{path}@{lines}"
):
    source = str(source) if source else ""

    for err in multiple_invalid.errors:

        # convert message to something easier for non-savvy user to understand
        msg, kind = voluptuous_error_msg_mappings.get(
            err.msg, (err.msg, 'value')
        )

        # get metadata about error
        codicil = ()
        if keymap:
            # build culprit
            culprit = nt.get_keys(err.path, keymap=keymap, strict="found", sep=sep)
            line_nums = nt.get_line_numbers(err.path, keymap, kind=kind, sep="-", strict=False)
            file_and_lineno = path_fmt.format(path=str(source), lines=line_nums)
            culprit = cull((file_and_lineno, culprit))

            # build codicil
            loc = nt.get_location(err.path, keymap)
            if data and kind == 'value':
                try:
                    value = nt.get_value(data, err.path)
                    if value is not None:
                        codicil = (f"Found {_summarize_value(value)}.",)
                except KeyError:
                    pass
            if loc:
                codicil += (loc.as_line(kind),)
            else:  # required key is missing
                missing = nt.get_keys(err.path, keymap, strict="missing", sep=sep)
                codicil += (f"‘{missing}’ was not found.",)
        else:
            keys = sep.join(str(c) for c in err.path)
            culprit = cull([source, keys])
            if data and kind == 'value':
                value = _nested_getvalue(data, err.path)
                if value is not None:
                    codicil = (f"Found {_summarize_value(value)}.",)

        # report error
        error(full_stop(msg), culprit=culprit, codicil=codicil)

    return errors_accrued()
