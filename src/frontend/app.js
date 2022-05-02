const express = require('express');
const app = express();
const path = require('path');
const router = express.Router();

app.use(express.static(__dirname));
router.get('/',function(req,res){
  res.sendFile(path.join(__dirname+'/index.html'));
  //__dirname : It will resolve to your project folder.
});

router.get('/login',function(req,res){
  res.sendFile(path.join(__dirname+'/login.html'));
  //__dirname : It will resolve to your project folder.
});

router.get('/register',function(req,res){
  res.sendFile(path.join(__dirname+'/register.html'));
  //__dirname : It will resolve to your project folder.
});

router.get('/history',function(req,res){
  res.sendFile(path.join(__dirname+'/history.html'));
  //__dirname : It will resolve to your project folder.
});

//add the router
app.use('/', router);
app.listen(process.env.port || 3000);

console.log('Running at Port 3000');