## Setting up ci using github actions
```
name: Build jsng 
on:
  push:
    branches: [ development ]
  pull_request:
    branches: [ development ]
```
the above part is the first part of the workflow 
* `name` defines a name to you workflow can be any name of your choice 
* `on` defines on which event this workflow should be triggered. in the above example it will be triggered on each push to master and on each pr as well
```
jobs:
  build:
    
    runs-on: ubuntu-latest
    steps: 
      - uses: actions/checkout@master 
      - uses: jpetrucciani/black-check@master
      - name: Gathering deps #defining another step with a name
        run: | # commands to be run in this step
          sudo apt-get update
          sudo apt-get install git python3-pip python3-venv python3-setuptools tmux -y
          sudo pip3 install poetry 
      - name: Install
        uses: abatilo/actions-poetry@v1.5.0 
        with:
          python_version: 3.6 
          poetry_version: 1.0.5 
          args: install 

      - name: Run tests
        uses: abatilo/actions-poetry@v1.5.0
        with:
          python_version: 3.6
          poetry_version: 1.0.5
          args: run python -m pytest tests -s

      - name: Run covarage tests
        uses: abatilo/actions-poetry@v1.5.0
        with:
          python_version: 3.6
          poetry_version: 1.0.5
          args: run python -m pytest tests -s --cov=jumpscale

```
* `jobs` workflow run is made up of one or more jobs. Jobs run in parallel by default. you can control if you want them to run sequentially by using jobs.<job_id>.need
* `runs-on` Each job runs in an environment specified by runs-on. 
* `steps` #A job contains a sequence of tasks called steps.
* `uses` Selects an action to run as part of a step in your job. An action is a reusable unit of code. You can use an action defined in the same repository as the workflow, a public repository, or in a published Docker container image.
* `uses: actions/checkout@master` This used to checkout the repo in the workspace
* `uses: jpetrucciani/black-check@master` using action black-check to check if code is blacked or not 
* `run` defines commands to be run on this step, can be bash commands or python...etc. check the github actions docs for more on this 
```
- name: Install
  uses: abatilo/actions-poetry@v1.5.0 
  with:
    python_version: 3.6 
    poetry_version: 1.0.5 
    args: install 
```
in the above step we are using poetry action, ready in market place
`with` defines the versions and commands to be done on poetry `install` in this example

