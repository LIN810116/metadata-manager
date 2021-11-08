import shutil
from pathlib import Path

import pandas as pd
from xlrd import XLRDError


class Dataset(object):
    def __init__(self):
        self._template_version = "2.0.0"  # default
        self._current_path = Path(__file__).parent.resolve()
        self._resources_path = Path.joinpath(self._current_path, "../resources")
        self._template_dir = Path()

        self._dataset_path = Path()
        self._dataset = dict()
        self._metadata_extensions = [".xlsx"]

        self.set_template()

    def set_dataset_path(self, path):
        """
        Set the path to the dataset
        :param path: path to the dataset directory
        :type path: string
        """
        self._dataset_path = Path(path)

    def set_template_version(self, version):
        """
        Choose a template version
        :param version: template version
        :type version: string
        """
        self._template_version = version

    def set_template(self, version=None):
        """
        Set template version & path
        :param version: template version
        :type version: string
        """
        if version:
            self.set_template_version(version)

        version = self._template_version.replace(".", "_")

        if "_" not in version:
            version = version + "_0_0"

        version = "version_" + version
        template_dir = self._resources_path / "templates" / version / "DatasetTemplate"

        self._template_dir = template_dir

    def load_template(self, version=None):
        """
        Load dataset from template
        :param version: template version
        :type version: string
        :return: loaded dataset
        :rtype: dict
        """
        self.set_template(version)
        dataset = self.load_dataset(self._template_dir)
        return dataset

    def save_template(self, save_dir, version=None):
        """
        Save the template directory locally
        :param save_dir: path to the output folder
        :type save_dir: string
        :param version: template version
        :type version: string
        """
        if version:
            self.set_template(version)

        shutil.copytree(self._template_dir, save_dir)

    def load_dataset(self, dataset_path):
        """
        Load the input dataset into a dictionary
        :param dataset_path: path to the dataset
        :type dataset_path: string
        :return: loaded dataset
        :rtype: dict
        """
        dataset_path = Path(dataset_path)
        for path in dataset_path.iterdir():
            if path.suffix in self._metadata_extensions:
                try:
                    metadata = pd.read_excel(path)
                except XLRDError:
                    metadata = pd.read_excel(path, engine='openpyxl')

                key = path.stem
                value = {
                    "path": path,
                    "metadata": metadata
                }
            else:
                key = path.name
                value = path

            self._dataset[key] = value

        return self._dataset

    def save_dataset(self, save_dir):
        """
        Save dataset
        :param save_dir: path to the dest dir
        :type save_dir: string
        """
        if not self._dataset:
            msg = "Dataset not defined. Please load the dataset or the template dataset in advance."
            raise ValueError(msg)

        save_dir = Path(save_dir)
        if not save_dir.is_dir():
            save_dir.mkdir()

        for key, value in self._dataset.items():
            if isinstance(value, dict):
                file_path = Path(value.get("path"))
                filename = file_path.name
                data = value.get("metadata")
                if isinstance(data, pd.DataFrame):
                    data.to_csv(Path.joinpath(save_dir, filename))

            elif Path(value).is_dir():
                dir_name = Path(value).name
                dir_path = Path.joinpath(save_dir, dir_name)
                shutil.copytree(value, dir_path)

            elif Path(value).is_file():
                filename = Path(value).name
                file_path = Path.joinpath(save_dir, filename)
                shutil.copyfile(value, file_path)
