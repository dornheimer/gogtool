import os
import subprocess


class Game:
    def __init__(self, name, game_info, local_path):
        self.name = name
        self.game_info = game_info
        self.local_path = local_path

        self.update = False
        self.old_files = []
        self.installers = self._get_installers()
        self.platform = 4 if 4 in self.installers else 1

    @property
    def local_files(self):
        file_names = os.listdir(self.local_path)
        return [fn for fn in file_names if fn.startswith(('gog', 'setup', self.name))]

    def _get_installers(self, platforms={4, 1}, id_prefix='en'):
        """Return installers for the game (linux and windows.)"""
        installers = {}
        for inst in self.game_info['installers']:
            if inst['platform'] in platforms and inst['id'].startswith(id_prefix):
                installers.setdefault(inst['platform'], []).append(inst['path'])
        return installers

    def check_for_update(self):
        """Compare local files to those on the server."""
        server_path = self.installers[self.platform]
        server_files = [os.path.basename(sp) for sp in server_path]

        if not all([(sf in self.local_files) for sf in server_files]):
            self.update = True
            self.old_files.append(self.local_files)

        return self.update

    def download(self):
        """Download newer versions of the game's setup files."""
        if self.update:
            if self.platform == 1:
                update_args = ["lgogdownloader", "--platform", "w", "--download", "--game", self.name]
            else:
                update_args = ["lgogdownloader", "--download", "--game", self.name]
            print(f'Downloading file(s) for {self.name}...')
            update_files = subprocess.Popen(update_args, stdout=subprocess.PIPE)
            stdout, _ = update_files.communicate()
            out = stdout.decode('utf-8')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"""{cls.__name__}({self.name}, {self.game_info}, {self.local_path})"""
