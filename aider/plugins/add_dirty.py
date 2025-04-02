from .command_registry import CommandRegistry

@CommandRegistry.register("cmd_add_dirty")
def cmd_add_dirty(self, args):
    "Add all dirty files in the repository to the chat"
    if not self.coder.repo:
        self.io.tool_error("No git repository found.")
        return

    dirty_files = self.coder.repo.get_dirty_files()
    untracked_files = self.coder.repo.repo.untracked_files
    dirty_files.extend(untracked_files)
    for file in dirty_files:
        self.cmd_add(file)