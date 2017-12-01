from lgog.game import Game
from lgog.helper import user
from lgog.helper.log import logger


def check_files(library_data, download_directory):
    """Check files of every game and add to list if an update is available."""
    local_games = []
    for game in download_directory.games:

        game_info = library_data.get_game_info(game)
        local_path = download_directory.get_path(game)
        local_files = download_directory.get_files(game)
        game_object = Game(game, game_info, local_path, local_files)
        local_games.append(game_object)

        logger.debug(f"Local files for {game}: {len(local_files)}")
        if local_files == []:  # Empty folder
            prompt = (f"Folder for {game} is empty. Download latest installer? (y/n) ")
            if user.confirm(prompt):
                game_object.update = True
                game_object.conf = True

    games_with_update = [lg for lg in local_games if lg.check_for_update()]
    print("\nGames with outdated setup files:")
    print("\n".join([g.name for g in games_with_update]), end="\n\n")

    logger.debug(f"{len(games_with_update)} games with updates")
    return games_with_update
