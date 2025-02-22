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

- Let's find [CVE-2024-53995][1] ( open redirect[^1] ) discovered by [CodeQL][2], are you ready? 😃

```bash
$ git clone https://github.com/SickChill/sickchill.git
$ cd sickchill

# vulnerable version
$ git checkout tags/2024.3.1
$ cd ../

# remove, update or add queries as you wish
$ echo "user_input_might_reach_function('tornado.web.RequestHandler.redirect')." > sickchill/.dhscanner.queries

# send the entire repo
$ tar -cz sickchill | curl -X POST -H "Content-Type: application/octet-stream" -H "Authorization: Bearer ${BEARER_TOKEN}" -H "X-Directory-Name: sickchill" -H "Ignore-Testing-Code: true" --data-binary @- http://127.0.0.1:443/${APPROVED_URL} --insecure

# expected output ( sarif format ) with the vulnerability discovered
{"runs":[{"tool":{"driver":{"name":"dhscanner"}},"results":[{"ruleId":"dataflow","message":{"text":"open redirect"},"locations":[{"physicalLocation":{"artifactLocation":{"uri":"sickchill"},"resgion":{"lineStart":33,"lineEnd":33,"colStart":8,"colEnd":65}}}]}]}]}
```

- look at the logs of the `entrypoint` service (see example from docker desktop)

[^1]: look at [the API for writing dhscanner queries](QUERIES.md) to learn how to write other queries

[1]: https://nvd.nist.gov/vuln/detail/CVE-2024-53995
[2]: https://securitylab.github.com/advisories/GHSL-2024-283_GHSL-2024-291_sickchill_sickchill/
