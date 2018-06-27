import csv
import io
import logging
import os
import requests
import zipfile

logger = logging.getLogger(__name__)

GOGDB_BASE_URL = 'https://www.gogdb.org/backups/'


class GOGDB:
    def __init__(self):
        self.db_archive = self.download_latest()
        self.csv_data = self.read_csv_from_zip(self.db_archive, 'products.csv')

    def get_file_list(self):
        res = requests.get(GOGDB_BASE_URL + 'filelist.txt')
        res_str = res.content.decode('utf-8')
        return res_str.split('\n')[:-1]

    def download_latest(self):
        file_list = self.get_file_list()
        latest_backup_url = file_list[-1]
        file_name = latest_backup_url.split('/')[1]

        if os.path.exists(file_name):
            logger.info("latest gogdb archive already downloaded")
        else:
            logger.info("retrieving latest gogdb archive")
            res = requests.get(GOGDB_BASE_URL + latest_backup_url)
            with open(file_name, 'wb') as f:
                f.write(res.content)

        return file_name

    def read_csv_from_zip(self, file_name, csv_file):
        with zipfile.ZipFile(file_name) as archive:
            csv_bytes = archive.read(csv_file)
            byte_stream = io.BytesIO(csv_bytes)
            byte_stream_decoded = (b.decode('utf-8') for b in byte_stream)
            csv_reader = csv.DictReader(byte_stream_decoded)
            return list(csv_reader)

    def get_game(self, slug):
        for game in self.csv_data:
            if game['slug'] != slug:
                continue
            return game

    def get_game_img(self, slug):
        game = self.get_game(slug)
        return game['image_logo']
