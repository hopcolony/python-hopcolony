import pytest
from .config import *
import hopcolony


class TestInitialize(object):

    def test_initialize(self):
        with pytest.raises(hopcolony.ConfigNotFound):
            hopcolony.initialize(config_file="..")

        with pytest.raises(hopcolony.InvalidConfig):
            hopcolony.initialize(username=user_name)

        with pytest.raises(hopcolony.InvalidConfig):
            hopcolony.initialize(username=user_name, project=project_name)

        project = hopcolony.initialize(username=user_name, project=project_name,
                                                token=token)

        assert project.config.username == user_name
        assert project.config.project == project_name
        assert project.config.token == token