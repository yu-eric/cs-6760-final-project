

fs = require('fs');
request = require('request');

function walk(currentDirPath, callback) {
    var fs = require('fs'), path = require('path');
    fs.readdirSync(currentDirPath).forEach(function(name) {
        var filePath = path.join(currentDirPath, name);
        var stat = fs.statSync(filePath);
        if (stat.isFile()) {
            callback(filePath, stat);
        } else if (stat.isDirectory()) {
            walk(filePath, callback);
        }
    });
}

var files = [];
var totalTime = 0;

walk('./out', function(filename) {

    console.log(filename)

    files.push(filename);
});

var i = 0;

function next() {

    var filename = files[i];
    i++;

    request({
        method: 'POST',
        time: true,    // timing request
        //Virtuoso url: 'http://localhost:8890/sparql-graph-crud-auth/?graph-uri=https://synbiohub.org/public',
        //url: 'http://synbiohub.org:8080/openrdf-sesame/repositories/synbiohub/statements',
        url: 'http://localhost:8889/bigdata/sparql?default-graph-uri=https://synbiohub.org/public',
        //auth:  {
        //    user: 'dba',
        //    pass: 'dba',
        //    sendImmediately: false
        //},
        headers: {
            'Content-Type': 'application/rdf+xml'
        },
        body: fs.readFileSync(filename) + ''
    }, function(err, response, body) {

        //console.log('submitted ' + filename + ' with err ' + err + ' and response ' + response.statusCode);
        //console.log(body)
        if(err) {
            console.log('error! ' + err);
        } else {
            fs.writeFileSync('last', i + '');
            totalTime += response.elapsedTime;
            console.log(totalTime);
        }

        next();

        //callback(null, body);
    });
}

next();



