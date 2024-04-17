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
$ docker compose up -d
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
$ python dhscanner.py --input=example.tar --workdir=workdir
```

---

<sup>1</sup> currently takes around 15 min. (coffee break :coffee: ...)