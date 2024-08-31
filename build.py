import os
import shutil

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


class NestedDirectoryYAMLDict(dict):
    def __init__(self):
        super().__init__()

    @staticmethod
    def __split_path(path: str):
        parents = []
        while True:
            path, file_system_entity = os.path.split(path)
            if file_system_entity:
                parents.append(file_system_entity)
            else:
                if path:
                    parents.append(path)
                break
        parents.reverse()  # To get the path from root to the file
        return parents

    def __setitem__(self, hierarchical_key, value):
        keys_hierarchy = self.__split_path(hierarchical_key)

        current_level_dict = self
        for i in range(len(keys_hierarchy) - 1):
            key = keys_hierarchy[i]
            if key not in current_level_dict:
                dict.__setitem__(current_level_dict, key, {})
            current_level_dict = current_level_dict[key]

        current_level_dict[keys_hierarchy[-1]] = value


def read_directory_of_yaml(directory_path):
    ndd = NestedDirectoryYAMLDict()

    for dirpath, folders, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.endswith(('.yaml', '.yml')):
                file_path = os.path.join(dirpath, filename)
                dictionary_key = file_path.removesuffix('.yaml').removesuffix('.yml')
                with open(file_path, 'r') as file:
                    yaml_dict = yaml.safe_load(file)
                    ndd[dictionary_key] = yaml_dict
    return ndd


if __name__ == '__main__':
    CONTENT_FOLDER = "data"
    TEMPLATES_FOLDER = "templates"
    OUTPUT_ARTIFACT_FOLDER = 'output'

    INDEX_TEMPLATE_NAME = "index.html.jinja2"

    INDEX_OUTPUT_PATH = os.path.join(OUTPUT_ARTIFACT_FOLDER, 'index.html')


    env = Environment(
        loader=FileSystemLoader(TEMPLATES_FOLDER),
        autoescape=select_autoescape()
    )

    context = read_directory_of_yaml(CONTENT_FOLDER)

    if os.path.exists(OUTPUT_ARTIFACT_FOLDER):
        shutil.rmtree(OUTPUT_ARTIFACT_FOLDER)

    os.makedirs(OUTPUT_ARTIFACT_FOLDER, exist_ok=True)

    index_template = env.get_template(INDEX_TEMPLATE_NAME)
    rendered_index = index_template.render(**context)

    with open(INDEX_OUTPUT_PATH, 'w') as f:
        f.write(rendered_index)

    shutil.copytree("assets", os.path.join(OUTPUT_ARTIFACT_FOLDER, "assets"))