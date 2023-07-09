// Export Global Information


export let mdt_routines = {};


export let communication_log = [];

function logx(head, text) {
    communication_log.push({'head': head, 'text': text})
    call_mdt({'object':'communication_log'})
    // console.log(`${head}: ${text}`)
}


function call_mdt(ele) {
    for (let mdt_routine in mdt_routines) {
        // console.log(`about to call ${mdt_routine}::mdt(${ele})...`)
        mdt_routines[mdt_routine](ele);
    }
}
export var exec_log = [
    {'time': '2023-06-01 08:30:27', 'system': 'STEP', 'line': 'This is a log message that shows something happened.'},
];


export var memory_store = {};

function memory_initial_load(msg) {
    logx('call', 'in memory_initial_load()')
    let mem = msg['data'];
    for (let key in mem) {
        if (mem.hasOwnProperty(key)) {
            memory_store[key] = mem[key];
        }
    }
    call_mdt({'object':'memory_store'})
}


function memory_update(msg) {
        // console.log(`call memory_update(${msg.data.name}...)`)
        const path = msg['data']['path'];
        const name = msg['data']['name'];
        const content = msg['data']['content'];

        let my_dir = memory_store;
        for (const d of path) {
            my_dir = my_dir[d];
        }
        my_dir[name] = content;
        // call_mdt('memory_store')
        call_mdt({'object': 'File', 'name': name, 'content': content})
    // console.log(`call memory_update(${path}, ${name}, ${content.slice(0,100)}...)`)
        logx('call', `memory_update(${path}, ${name}, ${content.slice(0,100)}...)`)

}

export var process_list = {};

function process_list_initial_load(msg) {
    logx('call', 'in process_list_initial_load()')
    let pl = msg['data'];
    for (let key in pl) {
        if (pl.hasOwnProperty(key)) {
            process_list[key] = pl[key];
        }
    }
    call_mdt({'object':'process_list'})
}

function process_step_update(msg) {
    // console.log(`In process_step_update(${msg.data.name}...)`)
    let step = msg['data'];
    let process = process_list[msg.object];
    let i = 0;
    for (; i < process_list[msg.object].length; i++) {
        if (process_list[msg.object][i]['name'] === step.name) {
            process_list[msg.object][i] = step;
            break;
        }
    }
    logx('call', `process_step_update(Step(name=${step.name}, ...)`)
    call_mdt({'object':'step', 'process_name':msg.object, 'step':step})
}

export var DatabaseStore = {}


let ws;

const connect = () => {
    ws = new WebSocket('ws://localhost:8090/ws');

    ws.onopen = () => {
        // console.log('WebSocket is open now.');
        logx('sock', 'ws.onopen: WebSocket is open now.');
    };

    ws.onmessage = (event) => {
        // console.log(`WebSocket message received: ${event.data}`);
        logx('sock', `WebSocket message received: ${event.data}`);

        let msg = JSON.parse(event.data);
        logx('receive', `msg(cmd=${msg.cmd}, object=${msg.object}, rc=${msg.rc}, cb=${msg.cb}, data=...)`)

        if ("cb" in msg) {
            let rtn = msg.cb
            // Update DatabaseStore....
            switch (rtn) {
                case 'db_initial_load':
                    logx('user', `db_initial_load from server ${msg.cmd} of ${msg.object}`);
                    let mem = msg['data'];
                    for (let key in mem) {
                        if (mem.hasOwnProperty(key)) {
                            memory_store[key] = mem[key];
                        }
                    }
                    break;
                case 'db_async_notification':
                    logx('user', `db_async_notification from server ${msg.cmd} of ${msg.object}`);
                    switch (msg.cmd) {
                        case 'I':
                        case 'U':
                            DatabaseStore[msg.object][msg.id] = msg.record
                            break;

                        case 'D':
                            delete DatabaseStore[msg.object][msg.id]
                            break;
                    }
                    break;
                case 'process_list_initial_load':   process_list_initial_load(msg);             break;
                case 'memory_initial_load':         memory_initial_load(msg);                   break;
                case 'process_step_update':         process_step_update(msg);                   break;
                case 'memory_update':               memory_update(msg);                         break;
                default:
                    logx('fail', `No Such Routine: ${rtn}(msg(cmd=${msg.cmd}, object=${msg.object}, rc=${msg.rc}, cb=${msg.cb}, data=...))`)

            }
        } else {
            logx('fail', `Message Must contain 'cb' property: ${msg}`);
        }

    };

    ws.onerror = (error) => {
        // console.log(`WebSocket error: ${error}`);
        logx('fail', `onerror: ${error}`);
    };

    ws.onclose = (event) => {
        // console.log('WebSocket is closed now.');
        logx('sock', `onclose: ${event}`);
        if (!event.wasClean) {
            // console.log(`WebSocket reconnection attempt: ${event}`);
            logx('sock', `WebSocket reconnection attempt: ${event}`);
            setTimeout(connect, 1000);
        }
    };
};

connect();
let messageToSend = '';


function sendMessageDispatch(event) {
    sendMessage(event.detail)
}

export function sendMessage(msg) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        let jmsg = JSON.stringify(msg);

        if (!window.hasOwnProperty(msg.cb)) {
            logx('fail', `Send of message with undefined callback ${msg.cb}`)
        }
        ws.send(jmsg);
        logx('send', `msg(cmd=${msg.cmd}, object=${msg.object}, cb=${msg.cb}, ...)`);
    } else {
        logx("fail", "Attempt to sendMessage with WebSocket not open.");
    }
}



