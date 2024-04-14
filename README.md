### dhscanner

Make container scanning great again :smiley:

### Installation

- clone this repo (with its submodules)

```bash
$ git clone --recurse-submodules https://github.com/OrenGitHub/dhscanner
$ cd dhscanner
```

- the software components of dhcanner reside in docker containers<sup>1</sup>

```bash
$ docker build --tag host.front.js  --file dhscanner.front.js/Dockerfile  dhscanner.front.js
$ docker build --tag host.front.rb  --file dhscanner.front.rb/Dockerfile  dhscanner.front.rb
$ docker build --tag host.parser.js --file dhscanner.parser.js/Dockerfile dhscanner.parser.js
$ docker build --tag host.parser.rb --file dhscanner.parser.rb/Dockerfile dhscanner.parser.rb
$ docker build --tag host.codegen   --file dhscanner.codegen/Dockerfile   dhscanner.codegen
```

- local host ports are distributed *consecutively*	

```bash
$ docker run -p 8000:3000 -d -t --name front.js  host.front.js
$ docker run -p 8001:3000 -d -t --name front.rb  host.front.rb
$ docker run -p 8002:3000 -d -t --name parser.js host.parser.js
$ docker run -p 8003:3000 -d -t --name parser.rb host.parser.rb
$ docker run -p 8004:3000 -d -t --name codegen   host.codegen
```

- the dhscanner manager also runs dockerized, for maximal portability

```bash
$ docker build --tag host.dhscanner  --file Dockerfile .
$ docker run --network=host -d -t --name dhscanner host.dhscanner
```

- now let's build a vulnerable express web server:

```bash
$ docker build --tag example --file dhscanner.examples/cve_2023_37466/example_00/Dockerfile dhscanner.examples/cve_2023_37466/example_00
$ docker save -o example.tar example
```

- and copy it inside our dhscanner docker:

```bash
$ docker cp example.tar dhscanner:/
```

- let's jump inside and do a quick health check !

```bash
$ docker exec -it dhscanner bash

# inside our docker !
# let's make sure everyone's ready for work !
$ python health_check_all_components.py
[10/04/2024 ( 11:48:09 )] [INFO]: front.js ---> healthy 😃
[10/04/2024 ( 11:48:09 )] [INFO]: front.rb ---> healthy 😃
[10/04/2024 ( 11:48:09 )] [INFO]: parser.js ---> healthy 😃
[10/04/2024 ( 11:48:09 )] [INFO]: parser.rb ---> healthy 😃

# let's start scanning !
$ python dhscanner.py example.tar
```

---

<sup>1</sup> currently takes around 30 min. (coffee break :coffee: ...)