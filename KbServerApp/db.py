import os
import shutil
from pathlib import Path
import re
import glob
import KbServerApp.colors
from KbServerApp.LineStatement import Compiler
from KbServerApp.logger import GptLogger as Logger


# This class represents a simple database that stores its data as files in a directory hierarchy.
class DB:
    """A simple key-value store, where keys are filenames and values are file contents."""

    # a class variable holding a dictionary of all macro_name -> values
    # this is used to replace macro names in the contents of the files
    # macro syntax is '&{macro_name} i.e. &{version} will be replace with the version number defined below'
    macro: dict[str, str] = {'version': '1.0'}

    def __init__(self, path):
        # path is the directory where the data is stored
        self.path = Path(path).absolute()
        self.path.mkdir(parents=True, exist_ok=True)
        self.compiler = Compiler(self)

    def __contains__(self, key):
        return (self.path / key).is_file()

    def __getitem__(self, key: str) -> [dict[str, str]]:
        """Return the contents of the file with the given key."""
        full_path = self.path / key

        result = []
        if not full_path.is_file():
            Logger.log('ERROR', f"Invalid Memory Item.  \nPath not found: {full_path}")
            raise KeyError(key)
        with full_path.open("r", encoding="utf-8") as f:
            # read the file and return the contents
            Logger.log('STEP', f"Reading>>{key}")
            msgs = self.get_messages(key, f.read().splitlines())
            return msgs

    def get_messages(self, name: str, macro_source: [str]) -> [dict[str, str]]:
        """ Compile the code in source into a list of statements
            Execute the statements to return a list of messages """
        source = []
        for line in macro_source:
            source.append(self.replace_macros(line))
        # print(f"source to compile {len(source)} lines of source: {source}")
        # for stmt in source:
        #     print(stmt)
        code = self.compiler.compile(source)
        # print(f"compiled source into {len(code)} lines of code:")
        # for stmt in code:
        #     print(stmt)
        msgs = self.compiler.execute(code)
        # print(f"executed code into {len(msgs)} messages:")
        # for msg in msgs:
        #     print(msg)
        return msgs

    def glob_files(self, search: str) -> [str]:
        """ Return a list of all files in the database that match the search pattern """
        s = self.path / search
        l = len(str(self.path))
        files = [x[l + 1:] for x in glob.glob(str(s))]
        return files

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, val):
        full_path = self.path / key
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(val, str):
            full_path.write_text(val, encoding="utf-8")
        else:
            # If val is neither a string nor bytes, raise an error.
            raise TypeError("val must be either a str or bytes")

    # this routine is used to substitute macros within a string
    def replace_macros(self, string: str) -> str:
        # find all '${' and '}$' pairs, occurring in the string
        # processes them in reverse order (right to left)

        # if there is no '${' in the string, return the string
        if '${' not in string:
            return string

        # split the string into substrings where '${' is found
        begin = string.split('${')

        # while there are still portions separated by '${' in the string
        while len(begin) > 1:
            # get last portion after '${'
            ending = begin.pop()

            # if there is no '}$' in the last portion, no macro substitution needed
            if '}$' not in ending:
                begin.append(begin.pop() + '${' + ending)
                continue
            else:
                # split the last portion by first '}$'
                (macro_name, rest) = ending.split('}$', 1)

                # replace the macro name with its value, and add to end of string
                t = begin.pop()
                t += str(self.macro[macro_name]) + rest
                begin.append(t)
                continue

        # we now have a string with no '${' as only element in begin
        return begin[0]

    def delete_dynamic_memory(self, process_name: str):
        # delete all subdirectories and files in the directory Dynamic
        this_dir = self.path / 'Dynamic' / process_name
        if os.path.exists(this_dir):
            shutil.rmtree(this_dir)
        os.mkdir(this_dir)
        Logger.log('MEMORY', f"deleted {this_dir} ")