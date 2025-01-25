### dhscanner

Make file system scanning great again :smiley:

### Installation

- clone this repo (with its submodules)

```bash
$ git clone --recurse-submodules https://github.com/OrenGitHub/dhscanner
$ cd dhscanner
```

- the dhscanner services are dockerized

```bash
# for fastest (release) build on x64 systems
$ docker compose -f compose.rel.x64.yaml up -d

# for fastest (release) build on ARM64 systems
$ docker compose -f compose.rel.aarch64.yaml up -d

# to experiment and customize dhscanner
$ docker compose -f compose.dev.yaml up -d
```

- take any directory you want to scan (say the [frappe][1] code base)
- refer to [the API documentation](./QUERIES.md) for writing queries

```bash
$ git clone https://github.com/frappe/frappe
$ cp <your.dhscanner.queries.file> frappe/.dhscanner.queries # <--- one file for all queries
$ tar -cz frappe | curl -X POST -H "Content-Type: application/octet-stream" -H "Authorization: Bearer ${BEARER_TOKEN}" -H "X-Directory-Name: frappe" --data-binary @- http://127.0.0.1:443/scan --insecure
```

- look at the logs of the `entrypoint` service (see example from docker desktop)
  
![צילום מסך 2025-01-24 192201](https://github.com/user-attachments/assets/ee1156b7-9c43-42b3-ad6e-1532a74682dd)

[1]: https://github.com/frappe/frappe
