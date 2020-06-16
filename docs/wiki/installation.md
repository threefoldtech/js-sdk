# All in one installation
Installation is as easy as `pip install js-ng`
# Step-by-step installation
## Install requierd packages 
```
apt-get update
apt-get install git python3-venv python3-pip
pip3 install poetry
```
## clone repo 
```
git clone https://github.com/threefoldtech/js-ng.git
```
## User Installation
```
poetry update --no-dev
poetry install --no-dev
```
## developer Installation
```
poetry update
poetry install
```
## Running jsng
```
poetry run jsng
```
## Running usershell for jsng
```
poetry run usershell
```
## Running command on poetry shell, if you want to use package in jsng vnev
```
poetry shell
```
