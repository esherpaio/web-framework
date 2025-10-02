import importlib
import importlib.util
import logging
import pkgutil


def import_package(module_name: str) -> None:
    try:
        # Use importlib.util.find_spec to inspect before importing
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            logging.warning(f"Module '{module_name}' not found")
        else:
            # Import the module
            module = importlib.import_module(module_name)
            # Handle packages vs regular modules
            if spec.submodule_search_locations is not None:
                # It's a package - auto-discover submodules
                for _, name, _ in pkgutil.iter_modules(
                    module.__path__, module.__name__ + "."
                ):
                    try:
                        importlib.import_module(name)
                    except ImportError:
                        continue
            # Import all public attributes
            attrs_to_import = getattr(module, "__all__", None) or [
                name
                for name in dir(module)
                if not name.startswith("_")
                and not hasattr(getattr(module, name), "__file__")
            ]
            # Add to globals and __all__
            for attr_name in attrs_to_import:
                if hasattr(module, attr_name):
                    globals()[attr_name] = getattr(module, attr_name)
            logging.info(f"Imported {len(attrs_to_import)} items from {module_name}")
    except Exception as e:
        logging.error(f"Failed to import {module_name}: {e}")
