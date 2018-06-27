from flask import Flask, redirect, render_template, request, url_for

from gogtool.browser import Args, main

app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('list_games', list_type='installed'))


@app.route('/games/<string:list_type>')
def list_games(list_type='installed'):
    linux_only = request.args.get('linux_only')
    linux_only = {'True': True, 'False': False}.get(linux_only, True)
    platform = 'l' if linux_only else 'w'

    args = Args(list=list_type, debug='debug', platform=platform)
    games = main(args)
    return render_template(
        'list.html',
        list_type=list_type,
        games=games,
        linux_only=linux_only
    )


@app.route('/launch')
def launch_game():
    game = request.args.get('game')
    args = Args(launch=game)
    main(args)
    return redirect(url_for('list_games', list_type='installed'))


@app.route('/download')
def download_games():
    pass


@app.route('/install')
def install_games():
    pass


@app.route('/lgogdownloader/edit_config')
def lgog_edit_config():
    pass


@app.route('/lgogdownloader/refresh')
def lgog_refresh():
    pass
