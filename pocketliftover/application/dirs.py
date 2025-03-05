import errno
import os

from appdirs import user_data_dir


class Dirs(object):
    appname = "PocketLiftover"
    appauthor = "CaylinHickey"
    dir = user_data_dir(appname, appauthor)

    @classmethod
    def initialize(cls):
        try:
            if cls.dir != "":
                os.makedirs(cls.dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e
            pass

    @classmethod
    def get_app_path(cls, sub_path: str):
        return os.path.join(cls.dir, sub_path)