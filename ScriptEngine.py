import pygame
import pickle
import os
import inspect
import types

from utils.gamewindow import size
class ResourceManager:
    def __init__(self, data_file):
        self.resources = {}
        self.load_resources(data_file)

    def load_resources(self, data_file):
        with open(data_file, 'rb') as f:
            self.resources = pickle.load(f)
        print("Loaded resources:", self.resources.keys())

    def get_script(self, key):
        if key in self.resources:
            return self.resources[key].decode('utf-8')
        else:
            raise KeyError(f"Resource {key} not found")

def load_scripts(resource_manager, script_folder):
    script_keys = [key for key in resource_manager.resources if key.startswith(script_folder)]
    modules = []
    for key in script_keys:
        try:
            script_code = resource_manager.get_script(key)
            module_name = os.path.basename(key).replace('.py', '')
            module = types.ModuleType(module_name)
            exec(script_code, module.__dict__)
            modules.append(module)
        except KeyError as e:
            print(f"Error loading script {key}: {e}")
    return modules

def gather_functions(modules):
    event_handlers = []
    non_event_functions = {}
    for module in modules:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr):
                if 'event' in inspect.signature(attr).parameters:
                    event_handlers.append(attr)
                else:
                    non_event_functions[attr_name] = attr
    return event_handlers, non_event_functions

def handle_event(handler, event, error_logged):
    try:
        handler(event)
    except Exception as e:
        if handler.__name__ not in error_logged:
            print(f"Error when trying to execute {handler.__name__}: {e}")
            error_logged.add(handler.__name__)

def main():
    try:
        pygame.init()
        screen = size.window_size
        data_file = 'data.win'
        resource_manager = ResourceManager(data_file)
        script_folder = 'Scripts'
        modules = load_scripts(resource_manager, script_folder)
        event_handlers, non_event_functions = gather_functions(modules)

        running = True
        clock = pygame.time.Clock()
        error_logged = set()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                for handler in event_handlers:
                    handle_event(handler, event, error_logged)

            pygame.display.flip()
            clock.tick(60)

    except Exception as e:
        print(f"{e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
