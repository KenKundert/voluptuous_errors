# IMPORTS {{{1
from inform import Inform, indent
import nestedtext as nt
from functools import partial
from parametrize_from_file import parametrize
from voluptuous import Schema, Required, Optional, MultipleInvalid
from voluptuous_errors import report_voluptuous_errors
import pytest


# GLOBALS {{{1
NAMES_SEEN = set()  # used to enforce that all test names are unique
                    # without this names could be repeated between levels,
                    # which might cause confusion when debugging
                    #
# SCHEMA {{{1
# Adapt parametrize_for_file to read dictionary rather than list {{{2
def name_from_dict_keys(tests):
    return [{**v, 'scenario': k} for k,v in tests.items()]

parametrize = partial(parametrize, preprocess=name_from_dict_keys)

# utilities {{{2
# as_int() {{{3
def as_int(arg):
    return int(arg)

# from_enum {{{2
def from_enum(arg):
    if arg:
        enum = str(arg).lower()
        if enum[0] == "'":
            return enum[1:]
        return enum

# to_bool {{{2
def to_bool(arg):
    if type(arg) is bool:
        return arg
    if not arg:
        return False
    arg = from_enum(arg)
    if arg in ["no", "n", "false", "f", "off", "0"]:
        return False
    if arg in ["yes", "y", "true", "t", "on", "1"]:
        return True
    raise Error(f"cannot convert {arg!r} to boolean.")

# to_snake_case() {{{3
def to_snake_case(s, parent_keys):
    return "_".join(s.strip().lower().split())


# scenario schema {{{2
validate_tests = Schema({
    Required('scenario'): str,  # this field is promoted to key by name_from_dict_keys
    Required('schema'): str,
    Required('cases'): {str: dict(source=str, given=str, expected=str)},
    Optional('normalize', default=""): str,
    Optional('keymap', default="'yes"): to_bool,
})


# CHECKERS {{{1
class Checker:
    def __init__(self, name):
        self.name = name

    def verbatim_check(self, expected, achieved, name):
        assert expected == achieved,  self.fail_message('verbatim', expected, achieved, name)

    def fail_message(self, kind, expected, achieved, name):
        report = [f"{kind} check on {name} failed."]
        report += [f"case: {self.name}"]

        if expected and '\n' in expected:
            expected = indent(expected)
            report += ['expected:', expected]
        else:
            report += [f"expected: {expected}"]

        if achieved and '\n' in achieved:
            achieved = indent(achieved)
            report += ['result:', achieved]
        else:
            report += [f"result: {achieved}"]

        return '\n'.join(report)


# TESTS {{{1
# test_basic() {{{2
@parametrize(
    key = "basic_tests",
    schema = validate_tests,
)
def test_basic(capsys, subtests, scenario, schema, cases, normalize, keymap):
    # complain about duplicate names
    assert scenario not in NAMES_SEEN, f"{scenario}: duplicate name"
    NAMES_SEEN.add(scenario)
    if normalize:
        normalize = eval(normalize)

    validate = Schema(eval(schema))
    for name, case in cases.items():
        assert name not in NAMES_SEEN, f"{name}: duplicate name"
        NAMES_SEEN.add(name)

        full_name = f"{scenario}.{name}"
        with subtests.test(full_name):
            keymap = {} if keymap else None
            capsys.readouterr()  # flush stdout & stderr
            data = nt.loads(case["given"], top=any, keymap=keymap, normalize_key=normalize)
            with pytest.raises(MultipleInvalid) as exception:
                validate(data)
            with Inform(prog_name=False):
                report_voluptuous_errors(exception.value, keymap, case.get("source"))
            stdout, stderr = capsys.readouterr()
            checker = Checker(full_name)
            checker.verbatim_check("", stderr.rstrip(), "stderr")
            checker.verbatim_check(case["expected"], stdout.rstrip(), "stdout")
                # not sure why, but I sometimes get an extra space on stdout
