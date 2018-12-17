from typing import List, Type, TypeVar

import pluggy  # type: ignore

from crib import config
from crib.repositories import properties

hookspec = pluggy.HookspecMarker("crib")


PR = TypeVar("PR", bound=properties.PropertyRepo)
TPR = Type[PR]


class CribSpec:
    @hookspec
    def crib_add_property_repos(self) -> List[TPR]:
        """Add scraper plugins

        :return: a list of PropertyRepos
        """
        return []

    @hookspec
    def crib_add_config_loaders(self) -> List[config.AbstractConfigLoader]:
        """Add config loaders

        :return: a list or AbstractConfigLoader
        """
        return []


def _init_plugin_manager() -> pluggy.PluginManager:
    pm = pluggy.PluginManager("crib")
    pm.add_hookspecs(CribSpec)
    pm.load_setuptools_entrypoints("crib")
    pm.register(config)
    pm.register(properties)
    return pm


_plugin_manager = _init_plugin_manager()
hook = _plugin_manager.hook
