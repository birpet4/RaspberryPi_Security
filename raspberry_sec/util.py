import importlib
import pkgutil
from raspberry_sec.interface.producer import Producer
from raspberry_sec.interface.consumer import Consumer
from raspberry_sec.interface.action import Action


class DynamicLoader:

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


class PCALoader(DynamicLoader):

    module_package = 'raspberry_sec.module'
    allowed_modules = {'action': Action, 'consumer': Consumer, 'producer': Producer}

    def filter_modules(self, modules: list):
        filtered_modules = []
        for _module in modules:
            module_name = _module.split('.')[:-1]
            if self.allowed_modules.has_key(module_name):
                filtered_modules.append(module)
        return filtered_modules

    def method(self):
        module_base = 'modules'
        entry_base = 'consumer'
        new_mod1 = 'detector'
        new_mod2 = 'recognizer'

        new_mod_consumer1 = DynamicLoader.load_class('.'.join([
            module_base, 
            new_mod1, 
            entry_base, 
            new_mod1.capitalize() + 'Consumer']))

        new_mod_consumer2 = DynamicLoader.load_class('.'.join([
            module_base, 
            new_mod2, 
            entry_base, 
            new_mod2.capitalize() + 'Consumer'])) 
    
        if (issubclass(new_mod_consumer1, Consumer) and 
            issubclass(new_mod_consumer2, Consumer)):    
            new_mod_consumer1().run()
            new_mod_consumer2().run()
        else:
            print('Wrong class detected')


print('Hi')
