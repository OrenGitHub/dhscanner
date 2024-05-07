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
$ docker build --tag example --file examples/cve_2023_37466/example_00/Dockerfile examples/cve_2023_37466/example_00
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
# let's start scanning !
$ python src/dhscanner.py --input=example.tar --workdir=workdir
[07/05/2024 ( 04:59:02 )] [INFO]: [ start  ] example.tar (1.06 GB) 😃
[07/05/2024 ( 04:59:05 )] [INFO]: [ step 0 ] untar docker image ... : finished 😃
[07/05/2024 ( 04:59:05 )] [INFO]: [ step 1 ] native asts .......... : finished 😃
[07/05/2024 ( 04:59:05 )] [INFO]: [ step 2 ] dhscanner asts ....... : finished 😃
[07/05/2024 ( 04:59:05 )] [INFO]: [ step 3 ] code gen ............. : finished 😃
[07/05/2024 ( 04:59:05 )] [INFO]: [ step 4 ] knowledge base gen ... : finished 😃
[07/05/2024 ( 04:59:05 )] [INFO]: [ step 5 ] prolog file gen ...... : finished 😃
[07/05/2024 ( 04:59:05 )] [INFO]: [  cves  ] ...................... : starting 🙏
[07/05/2024 ( 04:59:06 )] [INFO]: [ cve_2023_37466 ] .............. : oh no ! it looks bad 😬😬😬
[07/05/2024 ( 04:59:06 )] [INFO]: [ ghsa_97m3      ] .............. : looking good 👌
```

---

<sup>1</sup> currently takes around 15 min. (coffee break :coffee: ... )