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

# to remove all containers and all images:
# $ docker compose down --rmi local
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
[27/04/2024 ( 18:11:13 )] [INFO]: front.js ---> healthy 😃
[27/04/2024 ( 18:11:13 )] [INFO]: parser.js ---> healthy 😃
[27/04/2024 ( 18:11:13 )] [INFO]: codegen ---> healthy 😃
[27/04/2024 ( 18:11:13 )] [INFO]: kbgen ---> healthy 😃
[27/04/2024 ( 18:11:13 )] [INFO]: query.engine ---> healthy 😃

# let's start scanning !
$ python dhscanner.py --input=example.tar --workdir=workdir
[27/04/2024 ( 18:11:49 )] [INFO]: [ start  ] example.tar (1.06 GB) 😃
[27/04/2024 ( 18:11:52 )] [INFO]: [ step 0 ] untar docker image ... : finished 😃
[27/04/2024 ( 18:11:53 )] [INFO]: [ step 1 ] native asts .......... : finished 😃
[27/04/2024 ( 18:11:53 )] [INFO]: [ step 2 ] dhscanner asts ....... : finished 😃
[27/04/2024 ( 18:11:53 )] [INFO]: [ step 3 ] code gen ............. : finished 😃
[27/04/2024 ( 18:11:53 )] [INFO]: [ step 4 ] knowledge base gen ... : finished 😃
[27/04/2024 ( 18:11:53 )] [INFO]: [ step 5 ] prolog file gen ...... : finished 😃
[27/04/2024 ( 18:11:53 )] [INFO]: [  cves  ] ...................... : starting 🙏
[27/04/2024 ( 18:11:53 )] [INFO]: [ cve_2023_37466 ] .............. : oh no ! it looks bad 😬😬😬
```

---

<sup>1</sup> currently takes around 15 min. (coffee break :coffee: ... )