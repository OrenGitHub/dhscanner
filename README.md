### dhscanner

Make container scanning great again :smiley:

### Installation ( only [docker][1] is needed )

- let's clone this repo with its dependent submodules !

```bash
$ git clone --recurse-submodules https://github.com/OrenGitHub/dhscanner
$ cd dhscanner
```

- the software components of dhcanner reside in docker containers
- being dev-oriented, those images currently take around 30 min. to build ( coffee break :coffee: !)

```bash
$ docker build --tag host.front.js  --file dhscanner.front.js/Dockerfile  dhscanner.front.js
$ docker build --tag host.front.rb  --file dhscanner.front.rb/Dockerfile  dhscanner.front.rb
$ docker build --tag host.parser.js --file dhscanner.parser.js/Dockerfile dhscanner.parser.js
$ docker build --tag host.parser.rb --file dhscanner.parser.rb/Dockerfile dhscanner.parser.rb
```

- local host ports are distributed *consecutively* from `8000` upward

```bash
$ docker run -p 8000:3000 -d -t --name front.js  host.front.js
$ docker run -p 8001:3000 -d -t --name front.rb  host.front.rb
$ docker run -p 8002:3000 -d -t --name parser.js host.parser.js
$ docker run -p 8003:3000 -d -t --name parser.rb host.parser.rb
```

- the dhscanner manager also runs dockerized, for maximal portability

```bash
$ docker build --tag host.dhscanner  --file Dockerfile .
$ docker run --network=host -d -t --name dhscanner host.dhscanner
```

- let's jump inside and do a health check !

```bash
$ docker exec -it dhscanner bash

# inside our docker !
# let's make sure everyone's ready for work !
$ python health_check_all_components.py
```

[1]: https://docs.docker.com/
