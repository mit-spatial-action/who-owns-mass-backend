# who-owns-mass-backend
Django backend for who owns mass application.

## DB Schema
![mass_evictions schema](./schema.png)

## Setup
Written in Python 3.10.2

Install [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

Create the virtual Python environment:
```shell
pyenv virtualenv 3.10.2 mass-evictions
```
Trigger it automatically upon cd-ing into current dir
```shell
echo "mass-evictions" >> .python-version
```

Install Python dependencies:
```shell
pip install requirements.txt -r
```

To run app:
```shell
./manage.py runserver
```

## Create a local settings file
```shell
cp config/settings/settings_local.example.py config/settings/settings_local.py
```

## Update Database
Run sql file `update_db.sql` either by running file or copy pasting each line and making sure the tables have been updated with an `id` column

```shell
psql \c eviction_db
```
```psql
\dt
\x on;
select * from plaintiffs limit 5;
```

Migrate DB

```shell
./manage.py migrate 
```

to run Django shell (and make it nice)
```
./manage.py shell_plus
```

## To visualize database schema
```shell
pip install pygraphviz
python manage.py graph_models -a -g -o schema.png
```

