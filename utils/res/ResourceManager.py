import pygame
import pickle
import io
from io import BytesIO
import logging

class ResourceManager:
    def __init__(self, data_file):
        self.resources = {}
        self.cache = {}
        self.load_resources(data_file)

    def load_resources(self, data_file):
        try:
            with open(data_file, 'rb') as f:
                self.resources = pickle.load(f)
            logging.info(f"Loaded resources from {data_file}")
        except FileNotFoundError:
            logging.error(f"Resource file {data_file} not found")
        except pickle.UnpicklingError:
            logging.error(f"Failed to unpickle data from {data_file}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def get_resource(self, key, resource_type):
        if key in self.cache:
            return self.cache[key]

        if key in self.resources:
            data = self.resources[key]
            if resource_type == 'Images':
                resource = pygame.image.load(BytesIO(data))
            elif resource_type == 'Sounds':
                resource = pygame.mixer.Sound(BytesIO(data))
            elif resource_type == 'Fonts':
                resource = BytesIO(data)
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")

            self.cache[key] = resource
            return resource
        else:
            raise KeyError(f"Resource {key} not found")

    def get_image(self, key):
        return self.get_resource(key, 'Images')

    def get_sound(self, key):
        return self.get_resource(key, 'Sounds')

    def get_font(self, key, size):
        font_data = self.get_resource(key, 'Fonts')

        if isinstance(font_data, (bytes, bytearray)):
            return pygame.font.Font(io.BytesIO(font_data), size)

        elif isinstance(font_data, io.BytesIO):
            return pygame.font.Font(io.BytesIO(font_data.getvalue()), size)

        else:
            raise TypeError("Expected bytes-like object or BytesIO, got {}".format(type(font_data)))
    def clear_cache(self):
        self.cache.clear()
        logging.info("Resource cache cleared")
resource_manager = ResourceManager('data.win')
