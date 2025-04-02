from .command_registry import CommandRegistry
from prompt_toolkit.completion import Completion, PathCompleter
from prompt_toolkit.document import Document

@CommandRegistry.register("cmd_find")
def cmd_find(self, args):
    "Run find with a folder name then pattern and add the matching files"
    matches = None

    if not args.strip():
        self.io.tool_error("Please provide a folder name and a pattern to search for.")
        return

    args = args.split()
    if len(args) == 1:
        folder = args[0]
    elif len(args) == 2:
        folder, pattern = args
    else:
        self.io.tool_error("Too many arguments provided.")
        return

    if not os.path.isdir(folder):
        self.io.tool_error(f"Folder not found: {folder}")
        return

    matches = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            # Get the full path and make it relative to the search folder
            full_path = os.path.join(root, filename)
            # Convert to relative path for matching
            relative_path = os.path.relpath(full_path, start=folder)

            # Match against the relative path instead of just the filename
            if fnmatch.fnmatch(relative_path.lower(), pattern.lower()):
                matches.append(full_path)
    if len(matches) == 0:
        self.io.tool_output(f"No files found in {folder} matching {pattern}")
        return

    if self.io.confirm_ask(f"{len(matches)} files found, do you want to continue?'"):
        for file in matches:
            if self.io.confirm_ask(f"Do you want to add '{file}' to the chat?"):
                self.cmd_add(file)

@CommandRegistry.register("completions_raw_find")
def completions_raw_find(self, document, complete_event):
    # Get the text before the cursor
    text = document.text_before_cursor

    # Don't complete if there are two or more spaces
    if text.count(" ") > 1:
        return

    # Skip the first word and the space after it
    after_command = text.split()[-1]

    # Create a new Document object with the text after the command
    new_document = Document(after_command, cursor_position=len(after_command))

    def get_paths():
        return [self.coder.root] if self.coder.root else None

    path_completer = PathCompleter(
        get_paths=get_paths,
        only_directories=True,
        expanduser=True,
    )

    # Adjust the start_position to replace all of 'after_command'
    adjusted_start_position = -len(after_command)

    # Collect all completions
    all_completions = []

    for completion in path_completer.get_completions(new_document, complete_event):
        quoted_text = self.quote_fname(after_command + completion.text)
        all_completions.append(
            Completion(
                text=quoted_text,
                start_position=adjusted_start_position,
                display=completion.display,
                style=completion.style,
                selected_style=completion.selected_style,
            )
        )

    for completion in all_completions:
        yield completion
