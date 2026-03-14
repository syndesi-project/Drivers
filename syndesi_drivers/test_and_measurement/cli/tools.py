import inspect
import pkgutil
import importlib
import syndesi_drivers
from ..driver import Driver
from pathlib import Path
#from os.path import relpath
from pathlib import Path
from rich.tree import Tree
from rich.console import Console
from rich.theme import Theme

FOLDER_STYLE = "green"
DRIVER_STYLE = "bold cyan"

console = Console(theme=Theme({"folder": FOLDER_STYLE, "driver": DRIVER_STYLE}))

def list_drivers():
    """
    Return a list of drivers, grouped by location

    drivers : {
        'folder0' : {
            'driver0' : None,
            'driver1' : None,
            'folder2' : {
                'driver3' : None
            },
        'driver2' : None
        },
        'driver4' : None
    }
    Returns
    -------
    drivers : list
    """
    drivers = {}
    # Iterate through all modules in the package
    module_path = Path(syndesi_drivers.__path__[0])
    for _, modname, _ in pkgutil.walk_packages(syndesi_drivers.__path__, syndesi_drivers.__name__ + "."):
        module = importlib.import_module(modname)

        # Iterate through members of the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Driver) and obj is not Driver:
                if '_EXCLUDE_FROM_LIST' in obj.__dict__ and obj._EXCLUDE_FROM_LIST:
                    continue
                relative_path = Path(module.__file__).relative_to(module_path)
                location = relative_path.parts[:-1]
                

                dl = drivers
                for l in location:
                    if l not in dl:
                        dl[l] = {}
                    dl = dl[l]

                
                dl[name] = None

    return drivers

def print_drivers():
    drivers = list_drivers()
    tree = Tree("[folder]syndesi_drivers[/folder]")

    

    def add_drivers(tree : Tree, d : dict):
        for name, contents in d.items():
            if contents is None:
                # This is a driver
                tree.add(f'[driver]{name}[/driver]')
            elif isinstance(contents, dict):
                # This is a folder
                # Create a subtree and add it
                sub_tree = tree.add(f"[folder]{name}[/folder]")  # Folder name
                add_drivers(sub_tree, contents)
            else:
                raise ValueError(f'Cannot parse {contents}')
    

    add_drivers(tree, drivers)
    console.print(tree)



    # for location, lst in drivers.items():
    #     if location not in sub_trees:
            
    #         sub_trees[location] = sub_tree.add
    #     # TODO : Group the items by location
    #     sub_tree = tree
    #     if len(location) == 0:
    #         #sub_tree = tree
    #         pass
    #     else:
    #         for l in location:
    #             sub_tree
                

    #     for i, name in enumerate(lst):
    #         # if len(location) == 0:
    #         #     tree.add(f"[driver]{name}[/driver]")  # Driver name
    #         # else:
    #         sub_tree.add(f"")  # Driver name

    # console.print(tree)