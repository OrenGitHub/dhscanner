### dhscanner

Make container scanning great again :smiley:

### Installation

- clone this repo (with its submodules)

```bash
$ git clone --recurse-submodules https://github.com/OrenGitHub/dhscanner
$ cd dhscanner
```

- the software components of dhcanner reside in docker containers<sup>1</sup> <sup>2</sup>

```bash
# for fastest (release) build on x64 systems
$ docker compose -f compose.rel.x64.yaml up -d

# for dev build (also for ARM systems)
$ docker compose -f compose.dev.yaml up -d

# to remove all containers and all images:
# $ docker compose down --rmi local
```

- the dhscanner manager also runs dockerized, for maximal portability

```bash
$ docker build --tag host.dhscanner  --file Dockerfile .
$ docker run --network=host -d -t --name dhscanner host.dhscanner
```

- now let's inspect [CVE-2024-30256][1] disclosed by [CodeQL][2]<sup>3</sup>:

```bash
$ git clone https://github.com/open-webui/open-webui.git
$ cd .\open-webui\
$ git checkout tags/v0.1.111
$ docker build --tag host.open_webui --file Dockerfile .
$ docker save -o open_webui.tar host.open_webui
$ docker cp .\open_webui.tar dhscanner:/
```

- let's jump inside and make sure everything works !

```bash
$ docker exec -it dhscanner bash

# inside our docker !
# let's start scanning !
$ python src/dhscanner.py --input=open_webui.tar --workdir=workdir
[16/06/2024 ( 08:17:58 )] [INFO]: [ start  ] open_webui.tar (3.55 GB) 😃
[16/06/2024 ( 08:18:17 )] [INFO]: [ step 0 ] untar docker image ... : finished 😃
[16/06/2024 ( 08:18:18 )] [INFO]: [ step 1 ] native asts .......... : finished 😃
[16/06/2024 ( 08:18:18 )] [INFO]: [ step 2 ] dhscanner asts ....... : finished 😃
[16/06/2024 ( 08:18:18 )] [INFO]: [ step 3 ] code gen ............. : finished 😃
[16/06/2024 ( 08:18:18 )] [INFO]: [ step 4 ] knowledge base gen ... : finished 😃
[16/06/2024 ( 08:18:18 )] [INFO]: [ step 5 ] prolog file gen ...... : finished 😃
[16/06/2024 ( 08:18:18 )] [INFO]: [  cves  ] ...................... : starting 🙏
[16/06/2024 ( 08:18:18 )] [INFO]: [ cve_2023_37466 ] .............. : looking good 👌
[16/06/2024 ( 08:18:18 )] [INFO]: [ ghsa_97m3      ] .............. : looking good 👌
[16/06/2024 ( 08:18:18 )] [INFO]: [ cve_2024_32022 ] .............. : looking good 👌
[16/06/2024 ( 08:18:18 )] [INFO]: [ cve_2023_45674 ] .............. : looking good 👌
[16/06/2024 ( 08:18:18 )] [INFO]: [ cve_2024_30256 ] .............. : oh no ! it looks bad 😬😬😬
```

---

<sup>1</sup> currently takes 3.5 min. on a modern ( core i9, 32G RAM ) windows machine <br>
<sup>2</sup> currently ARM/v8 support is only through a dev build which takes significantly longer ( 12 min. ) <br>
<sup>3</sup> use a different directory for building the tested image tar

[1]: https://nvd.nist.gov/vuln/detail/CVE-2024-30256
[2]: https://securitylab.github.com/advisories/GHSL-2024-033_open-webui/
