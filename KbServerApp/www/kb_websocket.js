/*
** Resume Application websocket implementation
**
 */


let sock = null;
let CB = null;


function logx(head, msg ){
    if (window.ellog == null) {
        window.ellog = document.getElementById('LOG');
        window.msgline = document.getElementById('msgline');
    }
    let hd = head.padEnd(8, '.');
    let txt = ': ' + msg;
    let divhtml = `<div class="${head}"><div class="${head} head">${hd}</div>${txt}</div>`;
    ellog.innerHTML += divhtml;
    ellog.scrollTop = ellog.scrollHeight;
    msgline.innerHTML = divhtml;
}

function initialize() {
    // Open up a WebSocket connection via the default connection to the website
    let wsuri;
    let wsproto;

    // What protocol are we using?
    if (window.location.protocol === "https:") {
        wsproto = "wss";        // https
    } else {
        wsproto = "ws";         // http
    }

    // Is this a debug session loaded directly from file?
    if (window.location.protocol === "file:") {
        wsuri = wsproto + "://127.0.0.1:8080/ws";
    } else {
        wsuri = wsproto + "://" + window.location.hostname + ":" + window.location.port + "/ws";
    }

    if ("WebSocket" in window) {
        sock = new WebSocket(wsuri);
    } else if ("MozWebSocket" in window) {
        sock = new MozWebSocket(wsuri);
    } else {
        console.error("Browser does not support WebSocket!");
        return null;
    }

    if (sock) {
        sock.onopen = function () {
            logx("open","Connected to " + wsuri);
            if (window.hasOwnProperty('on_socket_open')){
                window.on_socket_open()
            }
        };

        sock.onclose = function (e) {
            logx(`close`, `Connection (wasClean = ${e.wasClean}, code = ${e.code}, reason = '${e.reason}')`);
            sock = null;
            if (window.hasOwnProperty('on_socket_close')) {
                window.on_socket_close()
            }
        };

        sock.onmessage = receive
    }
}

// setup call back hooks for initialization
window.onload = initialize;

let DatabaseStore = {}

function receive(e) {
    let msg = JSON.parse(e.data);
    logx('receive', `msg(cmd=${msg.cmd}, object=${msg.object}, rc=${msg.rc}, cb=${msg.cb}, data=...)`)
    if ("cb" in msg) {
        let rtn = msg.cb
        // Update DatabaseStore....
        switch(rtn) {
            case 'db_initial_load':
                window.logx('user', `db_initial_load from server ${msg.cmd} of ${msg.object}`);
                DatabaseStore = msg.data;
                if ('on_data_loaded' in window) {
                    logx('call', 'on_data_loaded(...)');
                    window['on_data_loaded'](DatabaseStore);
                }
                break;
            case 'db_async_notification':
                window.logx('user', `db_async_notification from server ${msg.cmd} of ${msg.object}`);
                switch (msg.cmd) {
                    case 'I':
                    case 'U':
                        DatabaseStore[msg.object][msg.id] = msg.record
                        break;

                    case 'D':
                        delete DatabaseStore[msg.object][msg.id]
                        break;
                }
        }
        if (rtn in window) {
            logx('call', `${rtn}(msg(cmd=${msg.cmd}, object=${msg.object}, rc=${msg.rc}, cb=${msg.cb}, data=...))`)
            window[rtn](msg)
        } else {
            logx('fail', `No Such Routine: ${rtn}(msg(cmd=${msg.cmd}, object=${msg.object}, rc=${msg.rc}, cb=${msg.cb}, data=...))`)
        }
    } else {
        logx('fail',  `Message Must contain 'cb' property: ${e.data}`);
    }
}


function send_msg(msg) {
    let jmsg = JSON.stringify(msg);
    if (!window.hasOwnProperty(msg.cb)) {
        logx('error', `Send of message with undefined callback ${msg.cb}`)
    }
    if (sock) {
        sock.send(jmsg);
        logx('send', `msg(cmd=${msg.cmd}, object=${msg.object}, cb=${msg.cb}, ...)`);
    } else {
        logx("error","Not connected.");
    }
}