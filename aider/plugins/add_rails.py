import os
import fnmatch
from .command_registry import CommandRegistry
from prompt_toolkit.completion import Completion, PathCompleter
from prompt_toolkit.document import Document

@CommandRegistry.register("cmd_add_rails")
def cmd_add_rails(self, args):
    """
    Find and add Rails files for a resource to the chat.

    Usage: /add-rails [namespace/]resource_name [--views view1 view2 ...]

    Examples: /add-rails locations /add-rails admin/locations /add-rails locations --views new edit

    This command finds and links existing Rails files for a resource:
      - View templates (by default all *.html.erb files, or specific ones with --views)
      - Model file
      - Controller file

    If a namespace is provided, view templates will be looked for in that namespace,
    but the model and controller will be looked for at the root level.
    """
    if not args.strip():
        self.io.tool_error("Usage: /add-rails [namespace/]resource_name [--views view1 view2 ...]")
        return

    # Parse arguments
    args_list = args.split()
    resource_path = args_list[0]

    # Check for --views flag
    specific_views = []
    try:
        views_index = args_list.index('--views')
        if views_index < len(args_list) - 1:
            specific_views = args_list[views_index + 1:]
    except ValueError:
        pass  # No --views flag

    # Parse resource path
    parts = resource_path.split('/')
    if len(parts) > 1:
        namespace = '/'.join(parts[:-1])
        resource_name = parts[-1]
    else:
        namespace = None
        resource_name = resource_path

    # Convert to singular for model (simple pluralization rule)
    model_name = resource_name[:-1] if resource_name.endswith('s') else resource_name

    # Ensure resource_name is plural for controllers and views
    resource_name_plural = resource_name if resource_name.endswith('s') else f"{resource_name}s"

    # Define paths
    view_path = os.path.join("app/views", namespace, resource_name_plural) if namespace else os.path.join("app/views", resource_name_plural)
    model_path = os.path.join("app/models", f"{model_name}.rb")
    controller_path = os.path.join("app/controllers", f"{resource_name_plural}_controller.rb")

    # Files found
    files_found = []

    # Check view templates
    # Rails convention is to use plural for view directories, but check both to be safe
    view_paths = [view_path]
    for current_view_path in view_paths:
        if os.path.isdir(current_view_path):
            if not specific_views:
                # If no specific views are requested, include all views
                for filename in os.listdir(current_view_path):
                    if filename.endswith('.html.erb'):
                        files_found.append(os.path.join(current_view_path, filename))
            else:
                # If specific views are requested, only include those
                for view in specific_views:
                    file_path = os.path.join(current_view_path, f"{view}.html.erb")
                    if os.path.exists(file_path):
                        files_found.append(file_path)

    # Check model
    if os.path.exists(model_path):
        files_found.append(model_path)

    # Check controller (Rails convention is to use plural for controller names)
    # First check for namespaced controller if namespace exists
    if namespace:
        namespaced_controller_path = os.path.join("app/controllers", namespace, f"{resource_name_plural}_controller.rb")

        if os.path.exists(namespaced_controller_path):
            files_found.append(namespaced_controller_path)
        elif os.path.exists(controller_path):  # Fall back to non-namespaced controller
            files_found.append(controller_path)
    else:
        # No namespace, just check the standard path
        if os.path.exists(controller_path):
            files_found.append(controller_path)

    if not files_found:
        self.io.tool_output(f"No Rails files found for resource: {resource_path}")
        return

    # Output found files
    self.io.tool_output(f"Found {len(files_found)} Rails files for {resource_path}:")
    for file_path in files_found:
        self.io.tool_output(f"  {file_path}")

    string_with_filenames = "\n".join(files_found)
    self.coder.check_for_file_mentions(string_with_filenames)

