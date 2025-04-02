from .command_registry import CommandRegistry
from aider.run_cmd import run_cmd

@CommandRegistry.register("cmd_run_add")
def cmd_run_add(self, args, add_on_nonzero_exit=False):
    "Run a shell command and optionally add the output to the chat (alias: !)"
    exit_status, combined_output = run_cmd(
        args, verbose=self.verbose, error_print=self.io.tool_error, cwd=self.coder.root
    )

    if combined_output is None:
        return
    print(combined_output)
    self.coder.check_for_file_mentions(combined_output)