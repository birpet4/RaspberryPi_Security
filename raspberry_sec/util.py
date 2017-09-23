import importlib
import pkgutil
import logging
from raspberry_sec.interface.producer import Producer
from raspberry_sec.interface.consumer import Consumer
from raspberry_sec.interface.action import Action


class DynamicLoader:

    LOGGER = logging.getLogger('DynamicLoader')

    @staticmethod
    def load_class(full_class_name: str):
        class_name_parts = full_class_name.split('.')
        class_name = class_name_parts[-1]
        module_name = '.'.join(class_name_parts[:-1])

        _module = importlib.import_module(module_name)
        return getattr(_module, class_name)

    @staticmethod
    def list_modules(package_name: str):
        package = importlib.import_module(package_name)
        modules = []
        for (path, name, is_package) in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            if not is_package:
                modules.append(name)
        return modules


class PCALoader(DynamicLoader):

    LOGGER = logging.getLogger('PCALoader')
    module_package = 'raspberry_sec.module'
    allowed_modules = set(['action', 'consumer','producer'])
    loaded_classes = {Action: set(), Consumer: set(), Producer: set()}

    @staticmethod
    def generate_class_names(modules: list):
        class_names = []
        for _module in modules:
            _module_parts = _module.split('.')
            module_name = _module_parts[-1]
            package_name = _module_parts[-2]
            class_names.append('.'.join([_module, package_name.capitalize() + module_name.capitalize()]))
        return class_names

    def filter_for_allowed_modules(self, modules: list):
        filtered_modules = []
        for _module in modules:
            module_name = _module.split('.')[-1]
            if module_name in self.allowed_modules:
                filtered_modules.append(_module)
        return filtered_modules

    def load(self):
        modules = DynamicLoader.list_modules(self.module_package)
        modules = self.filter_for_allowed_modules(modules)
        classes = PCALoader.generate_class_names(modules)

        for _class in classes:
            try:
                loaded_class = DynamicLoader.load_class(_class)
                for key in self.loaded_classes.keys():
                    if issubclass(loaded_class, key):
                        self.loaded_classes[key].add(loaded_class)
                        break
            except ImportError:
                PCALoader.LOGGER.error(_class + ' - Cannot be imported')
