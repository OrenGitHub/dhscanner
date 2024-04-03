### dhscanner

If you like software problems - please consider contributing to this repo :smiley:

#### Installation

The only things you need in order to use `dhscanner` is [docker][1] and [python][2].

```bash

# let's clone this repo with its dependent submodules !
$ git clone --recurse-submodules https://github.com/OrenGitHub/dhscanner

# now let's build an example docker image !
$ cd dhscanner.examples/cve_2023_37466/example_00
$ docker build --tag host.example --file Dockerfile .
$ docker save --output example_00.tar host.example

# we need to run a couple of dockers listenning on localhost
# ports are assigned serially from 8000 upwards

# 1. first run the esprima js parser
$ cd ../../../ # <--- go back up to the repo root
$ cd dhscanner.front.js
$ docker build --tag host.front.js --file Dockerfile .
$ docker run -p 8000:3000 -d -t --name front.js host.front.js

# 2. now build and run the dhscanner ast generator
$ cd ../ # <--- go back up to the repo root
$ cd dhscanner.parser.js
$ docker build --tag host.parser.js --file Dockerfile .
$ docker run -p 8001:3000 -d -t --name front.js host.front.js

# 3. now setup the python environment and let's scan some dockers !
$ pipenv shell
$ pipenv install
$ python analyze.py
```

[1]: https://docs.docker.com/
[2]: https://www.python.org/