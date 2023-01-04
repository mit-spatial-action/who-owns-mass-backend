# mass-evictions
Ongoing MIT DUSP research into housing precarity in Massachusetts.

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
pip install requirements.txt
```

```shell
./manage.py migrate 
```
