### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/yandex-praktikum/kittygram_backend.git
```

```
cd foodgram/backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py makemigrations users
python3 manage.py migrate users
python3 manage.py migrate
python3 manage.py load_data --path data/ingredients.csv
```

Запустить проект:

```
python3 manage.py runserver
```

```
Вот вы и запустили бэк проекта.
Простите, но я не умею писать красивые ридмишки.
```