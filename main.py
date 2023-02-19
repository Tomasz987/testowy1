"""Encrypting files application"""
from argparse import ArgumentParser, ArgumentError
import logging
import os
import sys


# The .cr extension belongs to encrypted files
ENCRYPTED_EXTENSION = ['.cr']
UNENCRYPTED_EXTENSIONS = ['.csv', '.json', '.txt']
FILE_TYPES = UNENCRYPTED_EXTENSIONS + ENCRYPTED_EXTENSION


class Main:
    """Main class of the crypter application.

    Methods:
         start(): classmethod to load all the necessary methods and start the application
    """
    def __init__(self):
        """Construct all the necessary attributes"""
        self.parser = ArgumentParser(
            prog='crypter.py',
            description='Encypting files application',
        )
        self.args = None

    def _load_arguments(self, args):
        """Init arguments"""
        self.parser.add_argument(
            '-m',
            '--mode',
            choices=['encrypt', 'decrypt', 'append'],
            required=True,
            metavar='',
            help="""Available modes: encrypt, decrypt, append;
            encrypt given file or files;
            decrypt encrypted file or files;
            append -> decrypt file, append text and encrypt the file again""",
        )
        self.parser.add_argument(
            '-p',
            '--password',
            metavar='PASSWORD',
            required=True,
            help='Password to encrypt or decrypt',
        )
        self.parser.add_argument(
            '-v',
            '--verbose',
            action='count',
            default=0,
            help='Verbose mode',
        )
        file_group = self.parser.add_mutually_exclusive_group(required=True)
        file_group.add_argument(
            '--file',
            nargs='+',
            help='The path to the name of the file/files with data to be processed',
        )
        file_group.add_argument(
            '--folder',
            help='The path to the folder with files to be processed',
        )
        self.parser.add_argument(
            '-e',
            '--extension',
            choices=FILE_TYPES,
            nargs='+',
            help="""The extensions of files to be processed.
                 All supported extensions are processed by default""",
        )
        self.parser.add_argument(
            '-r',
            '--remove',
            choices=[True, False],
            default=False,
            help='Remove parent file. Default is False'
        )
        self.args = self.parser.parse_args(args)

    def _set_default_extensions(self):
        """Set the default file extensions.
        Not used "default" option in extension implementation,
        because there are some dependence.
        """
        if not self.args.extension and self.args.mode == 'decrypt':
            self.args.extension = ['.cr']
        else:
            self.args.extension = FILE_TYPES

    def _validate_arguments(self):
        """Validate passed arguments."""
        if self.args.file and self.args.extension:
            raise ArgumentError(None, 'argument --file not allowed with argument --extension')

        if self.args.mode == 'decrypt' and None is not self.args.extension != ['.cr']:
            raise ArgumentError(None, 'argument --mode decrypt not allowed with argument --extension')

        if self.args.mode == 'append':
            if len(self.args.file) != 2:
                raise ArgumentError(None, 'append mode requires passing two files')
            extensions = {os.path.splitext(file)[1].lower() for file in self.args.file}
            if all(
                    [
                        extensions.issubset(set(ENCRYPTED_EXTENSION)),
                        extensions.issubset(set(UNENCRYPTED_EXTENSIONS)),
                    ]
            ):
                raise ArgumentError(None, 'append mode requires passing two files, encrypted and unencrypted')

        if self.args.file:
            for file in self.args.file:
                if os.path.splitext(file)[1].lower() not in FILE_TYPES:
                    raise ArgumentError(None, 'unsupported file type')

    def _start(self):
        """The method with application logic."""
        crypter = Crypter(
            self.args.password,
            self.args.verbose,
            self.args.remove,
        )
        crypter_mode = getattr(crypter, self.args.mode)

        if self.args.folder:
            for directory in os.walk(self.args.folder):
                for file in directory[2]:
                    if os.path.splitext(file)[1].lower() in self.args.extension:
                        crypter_mode(f'{directory[0]}/{file}')

        if self.args.file and self.args.mode != 'append':
            for file in self.args.file:
                crypter_mode(file)

        else:
            crypter_mode(self.args.file)

    @classmethod
    def start(cls):
        """Classmethod to init arguments and set verbose mode."""
        app = cls()
        app._load_arguments(sys.argv[1:])
        app._validate_arguments()
        app._set_default_extensions()
        app._start()


if __name__ == '__main__':
    try:
        Main().start()

    except ArgumentError as error:
        print(f'error: {error.message}')

    except FileNotFoundError as error:
        print(f'error: {error}')
        sys.exit()

    except ValueError as error:
        print(f'error: {error}')

