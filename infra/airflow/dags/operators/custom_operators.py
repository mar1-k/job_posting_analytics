import zipfile
from io import BytesIO
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class UnzipFileOperator(BaseOperator):
    """
    Custom operator to unzip a file in memory.
    """
    template_fields = ('zip_file_path',)

    @apply_defaults
    def __init__(self, zip_file_path, destination_folder, *args, **kwargs):
        super(UnzipFileOperator, self).__init__(*args, **kwargs)
        self.zip_file_path = zip_file_path
        self.destination_folder = destination_folder

    def execute(self, context):
        with open(self.zip_file_path, 'rb') as zip_file:
            zip_data = zip_file.read()
            self.log.info(f'Unzipping file {self.zip_file_path}')
            self.unzip_in_memory(zip_data)

    def unzip_in_memory(self, zip_data):
        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zip_ref:
            zip_ref.extractall(self.destination_folder)
