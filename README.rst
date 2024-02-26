Voluptuous Errors — Voluptuous Error Reporting when using NestedText and Inform
===============================================================================

.. image:: https://pepy.tech/badge/voluptuous_errors/month
    :target: https://pepy.tech/project/voluptuous_errors

..  image:: https://github.com/KenKundert/voluptuous_errors/actions/workflows/build.yaml/badge.svg
    :target: https://github.com/KenKundert/voluptuous_errors/actions/workflows/build.yaml

.. image:: https://coveralls.io/repos/github/KenKundert/voluptuous_errors/badge.svg?branch=master
    :target: https://coveralls.io/github/KenKundert/voluptuous_errors?branch=master

.. image:: https://img.shields.io/pypi/v/voluptuous_errors.svg
    :target: https://pypi.python.org/pypi/voluptuous_errors

.. image:: https://img.shields.io/pypi/pyversions/voluptuous_errors.svg
    :target: https://pypi.python.org/pypi/voluptuous_errors/

:Author: Ken Kundert
:Version: 0.0.0
:Released: 2024-02-25


A convenience function used for reporting voluptuous_ errors from nestedtext_ 
with inform_.  Here is a typical use of this function::

    >>> from voluptuous import Schema, Invalid, MultipleInvalid, Required
    >>> from voluptuous_errors import report_voluptuous_errors
    >>> from inform import error, os_error, terminate
    >>> import nestedtext as nt

    >>>  try:
    ...      settings_path = Path('settings.nt')
    ...      settings = nt.load(
    ...          settings_path,
    ...          keymap = (keymap:={}),
    ...      )
    ...      settings = schema(settings)
    >>>  except nt.NestedTextError as e:
    ...      e.report()
    >>>  except MultipleInvalid as e:
    ...      report_voluptuous_errors(e, keymap, settings_path)
    >>>  except OSError as e:
    ...      error(os_error(e))
    >>>  terminate()

This code reports all errors found by *Voluptuous* when reading the settings 
file.  It employs the *NestedText* *keymap* facility to annotate the error 
messages with helpful context such as line numbers.


Releases
--------

**Latest development release**:
    | Version: 0.0.0
    | Released: 2024-03-25

**0.0 (2024-02-25)**:
    Initial version.

.. _voluptuous: https://github.com/alecthomas/voluptuous
.. _nestedtext: https://nestedtext.org
.. _inform: https://inform.readthedocs.io

