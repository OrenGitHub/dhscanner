### dhscanner

Make container scanning great again :smiley:

#### Installation

The only things you need in order to use `dhscanner` is [docker][1].

```bash

# let's clone this repo with its dependent submodules !
$ git clone --recurse-submodules https://github.com/OrenGitHub/dhscanner
$ cd dhscanner

# the software components of dhcanner reside in docker containers.
# let's build them ! it should take anywhere between 5 and 15 min
# on a modern laptop ( coffee break :coffee: !)
# this is a single time thing, and would surely improve soon
$ cd dhscanner.front.js  && docker build --tag host.front.js  --file Dockerfile . && cd ../
$ cd dhscanner.parser.js && docker build --tag host.parser.js --file Dockerfile . && cd ../

# now let's run our docker containers, distributing local ports incrementally.
$ docker run -p 8000:3000 -d -t --name front.js  host.front.js
$ docker run -p 8001:3000 -d -t --name parser.js host.parser.js

# finally, let's build dhscanner, which also runs from a docker container
$ docker build --tag host.front.js  --file Dockerfile .
$ docker run --network=host -d -t --name dhscanner host.dhscanner

# everything seems ready - let's do a quick health check
# what are you waiting for ? just jump inside !
$ docker exec -it dhscanner bash

# inside our cozy and comfy docker !
# let's make sure everyone's ready for work !
$ python health_check_all_components.py
```

[1]: https://docs.docker.com/
[2]: https://www.python.org/