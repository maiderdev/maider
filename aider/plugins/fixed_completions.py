from .command_registry import CommandRegistry
import inspect
import os

@CommandRegistry.register("completions_add")
def completions_add(self):
    with_folders = True
    if inspect.stack()[1].function == "completions_raw_read_only":
        with_folders = False
    files = set(self.coder.get_all_relative_files())
    folders = {os.path.dirname(f) + '/' for f in files if os.path.dirname(f)}
    files = files - set(self.coder.get_inchat_relative_files())
    files = [self.quote_fname(fn) for fn in files]
    if with_folders:
        files.extend(folders)
    return files