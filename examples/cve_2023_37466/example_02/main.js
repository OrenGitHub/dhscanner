const express = require('express')

const app = express()
const port = 3000

app.get('/status', (req, res) => {
  res.send(`Everything seems fine\n`);
})

app.post('/vuln', (req, res) => {
  res.send(`I didn't do it\n`);
})

app.listen(port, () => {
  console.log(`Express server listening on port ${port}`)
})
