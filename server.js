const express = require("express"),
    es6Renderer = require('express-es6-template-engine')
    app = express();
const port = 9999;
var path = require('path');

var indexRouter = require('./routes/index');

app.engine('html', es6Renderer);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'html');

app.use(express.static(path.join(__dirname, 'views')));

app.get('/', function (req, res, next) {
    res.render('index.html', {locals: {title:'Hello World!'}});
});

app.listen(port, function() {
    console.log('Server listening on port ${port}')
});