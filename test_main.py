from argparse import ArgumentError
from unittest.mock import patch

import pytest

from main import Main


@patch('main.Main._start')
@pytest.mark.parametrize(
    'args, missing, errors', [
        (['-m', 'encrypt', '-p', 'pass'], '--file --folder', SystemExit),
        (['-m', 'encrypt', '--file', 'a.txt'], '-p/--password', SystemExit),
        (['-p', 'pass', '--file', 'a.txt'], '-m/--mode', SystemExit),
        (['-m', 'append', '-p', 'pass', '--file', 'file_one.txt'], 'second file', ArgumentError)
    ]
)
def test_load_arguments_without_required(main_mock, args, missing, errors, capsys):
    """Check that the app raised an error when the required argument didn't pass"""
    output_line_one = """usage: crypter.py [-h] -m  -p PASSWORD [-v] (--file FILE [FILE ...] | --folder FOLDER) \
[-e {.csv,.json,.txt,.cr} [{.csv,.json,.txt,.cr} ...]] [-r {True,False}]
"""
    output_line_two = 'crypter.py: error: the following arguments are required: '
    main = Main()

    with pytest.raises(errors) as error:
        main._load_arguments(args)
        main._validate_arguments()

    _, err = capsys.readouterr()

    if missing == 'second file':
        assert error.type == ArgumentError
        assert str(error.value) == 'append mode requires passing two files'

    elif missing == '--file --folder':
        assert error.type == SystemExit
        assert err == output_line_one + """crypter.py: error: \
one of the arguments --file --folder is required\n"""

    else:
        assert error.type == SystemExit
        assert err == output_line_one + output_line_two + missing + '\n'