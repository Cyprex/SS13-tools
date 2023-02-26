"""Defines our special log magics so people can use short commands"""
# pylint: disable=unused-argument
import re
import os

from IPython.terminal.magics import Magics, magics_class, line_magic

from .log_parser import LogFile
from .log import LogType


LOGS_VARIABLE_NAME = 'logs'


# For info on pasting see IPython.terminal.magics.TerminalMagics.paste
@magics_class
class LogMagics(Magics):
    """Stores our custom log magics for ease of use"""

    @line_magic
    def download(self, parameter_s=''):
        """Downloads logs from a round ID and stores it in `logs`"""
        if not parameter_s:
            print(f"No arguments! Usage: %{self.download.__name__} <round id>")
            return
        if '-' in parameter_s:
            parameter_s = parameter_s.split('-')
            if len(parameter_s) != 2:
                print("I don't know what to do with this, please try again")
                return
            try:
                first, last = (int(x) for x in parameter_s)
            except ValueError:
                print("One of these is not a number, try again")
                return
            self.shell.user_ns[LOGS_VARIABLE_NAME] = LogFile.from_round_range(first, last)
            return
        if ' ' in parameter_s or ',' in parameter_s:
            # Split with spaces and commas
            parameter_s = re.split(r'[, ]', parameter_s)
            try:
                # Prase ints and get rid of empty strings
                round_ids = (int(x) for x in parameter_s if x)
            except ValueError:
                print("One of those is not a number, please try again")
                return
            self.shell.user_ns[LOGS_VARIABLE_NAME] = LogFile.from_round_collection(*round_ids)
            return
        self.shell.user_ns[LOGS_VARIABLE_NAME] = LogFile.from_round_id(int(parameter_s))

    @line_magic
    def length(self, parameter_s=''):
        """Prints how many logs we have"""
        print(len(self.shell.user_ns[LOGS_VARIABLE_NAME]))

    @line_magic
    def sort(self, parameter_s=''):
        """Sorts our logs"""
        self.shell.user_ns[LOGS_VARIABLE_NAME].sort()

    @line_magic
    def search_ckey(self, parameter_s=''):
        """Excludes logs that do not contain any of the ckeys"""
        if not parameter_s:
            print(f"Add some ckeys! Usage: %{self.search_ckey.__name__} ckey1 ckey2 ckey3...")
            return
        parameter_s = (x.strip() for x in re.split(r'[, ]', parameter_s) if x)
        self.shell.user_ns[LOGS_VARIABLE_NAME].filter_ckeys(*parameter_s, source_only=False)

    @line_magic
    def search_string(self, parameter_s=''):
        """Works just like bookmarking in Notepad++, or CTRL+F multiple times. Case insensitive"""
        if not parameter_s:
            print("No string to search for!")
            return
        self.shell.user_ns[LOGS_VARIABLE_NAME].filter_strings(parameter_s, source_only=False)

    @line_magic
    def heard(self, parameter_s=''):
        """Gets only what the person could have heard"""
        if not parameter_s:
            print(f"Add a ckey! Usage: %{self.heard.__name__} ckey")
            return
        self.shell.user_ns[LOGS_VARIABLE_NAME].get_only_heard(parameter_s)

    @line_magic
    def conversation(self, parameter_s=''):
        """Tries to reconstruct a conversation between parties"""
        if not parameter_s:
            print(f"Add some ckeys! Usage: %{self.conversation.__name__} ckey1 ckey2 ckey3...")
            return
        parameter_s = (x.strip() for x in re.split(r'[, ]', parameter_s) if x)
        self.shell.user_ns[LOGS_VARIABLE_NAME].filter_conversation(*parameter_s)

    @line_magic
    def reset(self, parameter_s=''):
        """Resets the work set"""
        self.shell.user_ns[LOGS_VARIABLE_NAME].reset_work_set()
        print("Filters reset!")

    @line_magic
    def location(self, parameter_s=''):
        """Filters by exact location name. Search for strings if you want a more fuzzy search"""
        if not parameter_s:
            print(f"Add some ckeys! Usage: %{self.location.__name__} Medbay Central")
            return
        parameter_s = (x.strip() for x in re.split(r'[, ]', parameter_s) if x)
        self.shell.user_ns[LOGS_VARIABLE_NAME].filter_by_location_name(*parameter_s)

    @line_magic
    def radius(self, parameter_s=''):
        """Tries to reconstruct a conversation between parties"""
        parameter_s = parameter_s.split(' ')
        if len(parameter_s) != 4:
            print(f"Add some ckeys! Usage: %{self.radius.__name__} x y z radius")
            return
        try:
            x, y, z, radius = (int(x) for x in parameter_s)
        except ValueError:
            print("Could not convert to an integer")
            return
        self.shell.user_ns[LOGS_VARIABLE_NAME].filter_by_radius((x, y, z), radius)

    @line_magic
    def type(self, parameter_s=''):
        """Filters by log type"""
        exclude = (x[1:].strip() for x in re.split(r'[, ]', parameter_s) if x and x[0] == '!')
        include = (x.strip() for x in re.split(r'[, ]', parameter_s) if x and x[0] != '!')
        log_types = (LogType.parse_log_type(log_type) for log_type in parameter_s)
        if LogType.UNKNOWN in log_types:
            print("Unrecognised log type. Available types:")
            print(LogType.list())
            print(f"Example include: %{self.type.__name__} GAME ATTACK")
            print(f"Example exclude: %{self.type.__name__} !SILICON")
            return
        self.shell.user_ns[LOGS_VARIABLE_NAME].filter_by_type(include, exclude)

    @line_magic
    def print_logs(self, parameter_s=''):
        """Prints our filtered logs"""
        self.shell.user_ns[LOGS_VARIABLE_NAME].print_logs()

    @line_magic
    def head(self, parameter_s=''):
        """Prints our filtered logs, but only the head"""
        try:
            self.shell.user_ns[LOGS_VARIABLE_NAME].head(int(parameter_s))
        except ValueError:
            self.shell.user_ns[LOGS_VARIABLE_NAME].head()

    @line_magic
    def tail(self, parameter_s=''):
        """Prints our filtered logs, but only the tail"""
        try:
            self.shell.user_ns[LOGS_VARIABLE_NAME].tail(int(parameter_s))
        except ValueError:
            self.shell.user_ns[LOGS_VARIABLE_NAME].tail()

    @line_magic
    def clear(self, parameter_s=''):
        """Clears the logs, freeing memory"""
        print("Are you sure you want to remove all logs? [y/N] ", end="")
        if input().strip().lower() != 'y':
            return
        self.shell.user_ns[LOGS_VARIABLE_NAME] = LogFile()
        print("Logs cleared!")

    @line_magic
    def save(self, parameter_s=''):
        """Saves the working set to a file"""
        if not parameter_s:
            parameter_s = "logs.log"
        print(f"Writing to file {parameter_s}")
        self.shell.user_ns[LOGS_VARIABLE_NAME].write_working_to_file(parameter_s)

    @line_magic
    def load_file(self, parameter_s=''):
        """Opens the file and adds all logs to our current collection"""
        if not parameter_s:
            print("Enter a file name!")
        if not os.path.exists(parameter_s):
            print("File does not exist")
            return
        self.shell.user_ns[LOGS_VARIABLE_NAME].collate(LogFile.from_file(parameter_s))


def register_aliases(shell):
    """Adds shorthands for all magics"""
    macros = [
        ('dl', LogMagics.download.__name__),
        ('l', LogMagics.length.__name__),
        ('ckeys', LogMagics.search_ckey.__name__),
        ('string', LogMagics.search_string.__name__),
        ('loc', LogMagics.location.__name__),
        ('s', LogMagics.save.__name__),
        ('p', LogMagics.print_logs.__name__),
    ]
    for alias, magic in macros:
        shell.magics_manager.register_alias(alias, magic, 'line')