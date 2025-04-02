# command_registry.py
import functools

class CommandRegistry:
    registry = {}
    prepend_hooks = {}  # Stores functions to prepend
    append_hooks = {}   # Stores functions to append

    @classmethod
    def register(cls, name):
        """Decorator to register/override commands dynamically."""
        def decorator(func):
            cls.registry[name] = func  # Store function in registry
            return func
        return decorator

    @classmethod
    def prepend(cls, name):
        """Decorator to prepend logic to an existing command."""
        def decorator(func):
            cls.prepend_hooks[name] = func  # Store function
            return func
        return decorator

    @classmethod
    def append(cls, name):
        """Decorator to append logic to an existing command."""
        def decorator(func):
            cls.append_hooks[name] = func  # Store function
            return func
        return decorator

    @classmethod
    def inject(cls, target_class):
        """Inject hooks into existing command methods dynamically."""
        for name, func in cls.registry.items():
            setattr(target_class, name, func)

        for name in set(cls.prepend_hooks.keys()).union(cls.append_hooks.keys()):
            if hasattr(target_class, name):  # Only wrap if method exists
                original_method = getattr(target_class, name)

                @functools.wraps(original_method)
                def wrapped(self, *args, **kwargs):
                    # Run prepended function if available
                    if name in cls.prepend_hooks:
                        return_value = cls.prepend_hooks[name](self, *args, **kwargs)

                    # Execute the original method
                    if return_value:
                      result = original_method(self, *args, **kwargs)

                    # Run appended function if available
                    if name in cls.append_hooks:
                        cls.append_hooks[name](self, result, *args, **kwargs)

                    return result  # Return the original method's output

                setattr(target_class, name, wrapped)  # Replace method with wrapped version