import argparse

import settings
from classes.game_context import GameContext
from elements.global_classes import sound_manager
from elements.progressbar_menu import ProgressBarMenu


def main():
    try:
        # noinspection PyPackageRequirements
        import jaba_speedup  # type: ignore
    except ImportError:
        raise RuntimeError("Can't find speedup extension. You need to run `setup.py build_ext --inplace`")
    parser = argparse.ArgumentParser(description='Jaba')
    parser.add_argument("-d", "--debug", help='Logs some useful information', action="store_true")
    parser.add_argument("-m", "--map", help='Opens the whole map', action="store_true")
    args = parser.parse_args()
    if args.debug:
        settings.DEBUG = True
        print("Debug on")
    if args.map:
        settings.FREEMAP = True
        print("Map opened")

    sound_manager.start_download()
    GameContext(ProgressBarMenu).run()


if __name__ == '__main__':
    main()
