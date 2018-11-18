python -m venv .\venv
call venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt

pylint --rcfile=.pylintrc deploy.py game.py jackit2 jackitio/jackitio jackitio/leaderboard jackitio/manage.py
pycodestyle deploy.py game.py jackit2 jackitio/jackitio jackitio/leaderboard jackitio/manage.py
