import os, json, base64, yaml
from pathlib import Path

_app = None

class ConfigNotFound(Exception):
    pass

class InvalidConfig(Exception):
    pass

class HopConfig:
    hop_dir = str(Path.home()) + "/.hop"
    hop_file = os.path.join(hop_dir, "config")
    app = None
    project = None
    token = None
    identity = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.identity = self.compute_identity()

    def compute_identity(self):
        if not self.app or not self.project:
            return None
        raw = str(self.project) + "." + str(self.app)
        message_bytes = raw.encode('ascii')
        return base64.b64encode(message_bytes).decode('ascii')
    
    @property
    def valid(self):
        return self.app and self.project and self.token and self.identity
    
    @classmethod
    def update(cls, **kwargs):
        try:
            current = cls.fromFile(cls.hop_file).json
            for key,value in kwargs.items():
                if value:
                    current[key] = value
            return cls.fromJson(**current)
        except FileNotFoundError:
            return cls(**kwargs)
    
    @classmethod
    def fromFile(cls, file):
        with open(file, "r") as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
            return cls.fromJson(**config)
        
    @classmethod
    def fromJson(cls, **kwargs):
        return cls(**kwargs)

    @property
    def json(self):
        return {"app": self.app,
                "project": self.project,
                "token": self.token}

    @property
    def yaml(self):
        return yaml.dump(self.json)
    
    def commit(self):
        Path(self.hop_dir).mkdir(parents=False, exist_ok=True)
        with open(self.hop_file, "w") as f:
            f.write(self.yaml)
        return self.json

class App:
    def __init__(self, app = None, project = None, token = None, 
                 config_file = ".hop.config"):

        # Use app, project and token values if the 3 provided
        if any([app, project, token]):
            if all([app, project, token]):
                self.config = HopConfig(app = app, project = project, token = token)
                return
            else:
                raise InvalidConfig("If you provide one of [app, project, token], you need to provide the 3 of them")

        # Else, use the provided config_file if provided. If not, try ~/.hop/config
        try:
            self.config = HopConfig.fromFile(config_file)
        except FileNotFoundError:
            if config_file != HopConfig.hop_dir:
                try:
                    self.config = HopConfig.fromFile(HopConfig.hop_file)
                except FileNotFoundError:
                    raise ConfigNotFound(f"Hop Config not found. Run 'hopctl config set' or place a .hop.config file here.")
            else:
                raise ConfigNotFound(f"Hop Config not found. Run 'hopctl config set' or place a .hop.config file here.")
        except IsADirectoryError:
            raise ConfigNotFound(f"Config file provided [{config_file}] is a directory")
    
    @property
    def name(self):
        return self.config.app

def initialize(**kwargs):
    global _app
    _app = App(**kwargs)
    return _app

def get_app():
    assert _app, "You need to initialize the app first with hopcolony_core.initialize()"
    return _app

def config():
    app = get_app()
    return app.config