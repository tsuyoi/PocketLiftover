import FreeSimpleGUI as Sg

from pocketliftover.application import Config, Dirs
from pocketliftover.gui import get_gui_icon, main_window

if __name__ == "__main__":
    Sg.change_look_and_feel('Default 1')
    Sg.set_global_icon(get_gui_icon())
    Sg.set_options(icon=get_gui_icon())
    try:
        Dirs.initialize()
        Config.load_config()
    except OSError as e:
        exit(1)
    main_window()