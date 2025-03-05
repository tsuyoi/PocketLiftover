import os
import shutil

from pathlib import Path
from typing import List, Optional

import yaml

from .dirs import Dirs


class ConfigException(Exception):
    def __init__(self, msg):
        self.msg = msg


class ChainfileConfig(object):
    def __init__(self, label, source_type, destination_type, file):
        self.label = label
        self.source_type = source_type
        self.destination_type = destination_type
        self.file = file

    def update_settings(self, label, source_type, destination_type):
        self.label = label
        self.source_type = source_type
        self.destination_type = destination_type

    def yamlfy(self):
        return {
            'label': self.label,
            'source_type': self.source_type,
            'destination_type': self.destination_type,
            'file': self.file,
        }

    def __repr__(self):
        return f"Chainfile ({self.label}) [{self.source_type} => {self.destination_type}]: {self.file})"


class PatternConfig(object):
    def __init__(self, label, pattern):
        self.label = label
        self.pattern = pattern

    def update_settings(self, label, pattern):
        self.label = label
        self.pattern = pattern

    def yamlfy(self):
        return {
            'label': self.label,
            'pattern': self.pattern,
        }

    def __repr__(self):
        return f"Pattern ({self.label}: {self.pattern})"


class Config(object):
    config_file = Dirs.get_app_path('config.yml')
    default_chainfile = None
    chainfiles = []
    patterns = []

    @staticmethod
    def get_default_chainfile():
        if Config.default_chainfile is not None:
            if Config.default_chainfile in Config.get_chainfiles():
                return Config.get_chainfile(Config.default_chainfile)
            else:
                Config.set_default_chainfile(None)
        return None

    @staticmethod
    def set_default_chainfile(label: Optional[str]):
        Config.default_chainfile = label
        Config.save_config()

    @staticmethod
    def get_chainfiles() -> List[str]:
        return [c.label for c in Config.chainfiles]

    @staticmethod
    def get_chainfile(label: str) -> ChainfileConfig:
        return next((c for c in Config.chainfiles if c.label == label), None)

    @staticmethod
    def load_chainfile(label: str, source_type: str, destination_type: str, chainfile: str):
        Config.chainfiles.append(ChainfileConfig(label, source_type, destination_type, chainfile))

    @staticmethod
    def add_chainfile(label: str, source_type: str, destination_type: str, chainfile: str):
        Config.chainfiles.append(ChainfileConfig(label, source_type, destination_type, chainfile))
        Config.save_config()

    @staticmethod
    def save_new_chainfile(label: str, source_type: str, destination_type: str, chainfile: Path,
                           save_local: bool = False) -> List[str]:
        if label in Config.get_chainfiles():
            raise ConfigException(f"{label} already exists")
        if not chainfile.exists():
            raise ConfigException(f"File {chainfile} does not exist")
        if save_local:
            local_copy = Path(Dirs.get_app_path(f"{label}.chainfile"))
            shutil.copy(chainfile, local_copy)
            chainfile = local_copy
        Config.add_chainfile(label, source_type, destination_type, str(chainfile))
        return [label, source_type, destination_type, str(chainfile)]

    @staticmethod
    def delete_chainfile(label: str):
        to_remove = Config.get_chainfile(label)
        if to_remove is None:
            raise ConfigException(f"Chainfile {label} does not exist")
        local_copy = Path(Dirs.get_app_path(f"{label}.chainfile"))
        if local_copy.exists():
            try:
                os.remove(local_copy)
            except: pass
        Config.chainfiles.remove(to_remove)
        Config.save_config()

    @staticmethod
    def get_patterns() -> List[str]:
        return [p.label for p in Config.patterns]

    @staticmethod
    def get_pattern(label: str) -> PatternConfig:
        return next((p for p in Config.patterns if p.label == label), None)

    @staticmethod
    def load_pattern(label: str, pattern: str):
        if label in Config.get_patterns():
            raise ConfigException(f"{label} already exists")
        Config.patterns.append(PatternConfig(label, pattern))

    @staticmethod
    def add_pattern(label: str, pattern: str) -> List[str]:
        if label in Config.get_patterns():
            raise ConfigException(f"{label} already exists")
        Config.patterns.append(PatternConfig(label, pattern))
        Config.save_config()
        return [label, pattern]

    @staticmethod
    def delete_pattern(label: str):
        to_remove = Config.get_pattern(label)
        if to_remove is None:
            raise ConfigException(f"Pattern {label} does not exist")
        Config.patterns.remove(to_remove)
        Config.save_config()


    @staticmethod
    def save_config():
        yaml.safe_dump(
            {
                'chainfiles': [c.yamlfy() for c in Config.chainfiles],
                'default_chainfile': Config.default_chainfile,
                'patterns': [p.yamlfy() for p in Config.patterns],
            },
            open(Config.config_file, 'w'),
            sort_keys=False
        )

    @staticmethod
    def load_config():
        try:
            conf = yaml.safe_load(open(Config.config_file, 'r'))
            if conf is None:
                Config.save_config()
                return
            if 'chainfiles' in conf:
                for chainfile in conf['chainfiles']:
                    Config.load_chainfile(chainfile['label'], chainfile['source_type'],
                                                      chainfile['destination_type'], chainfile['file'])
            if 'default_chainfile' in conf:
                Config.default_chainfile = conf['default_chainfile']
            if 'patterns' in conf:
                for pattern in conf['patterns']:
                    Config.load_pattern(pattern['label'], pattern['pattern'])
        except FileNotFoundError:
            Config.save_config()