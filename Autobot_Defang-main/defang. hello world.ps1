const http = require('file:///C:/Users/(*name)/AutoScan-4/frontEnd/src/schedule.html')

const server = http.createServer((req,res) => {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');
    res.end('Welcome to defang/n');
});

server.listen(3000, '0.0.0.0',() => {
console.log('Server running at http://IP*/');
});