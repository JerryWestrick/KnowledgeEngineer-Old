<script>

  import { writable } from 'svelte/store';
  import {communication_log,  process_list, set_process_list, memory_store, exec_log, DatabaseStore} from './GlobalStorage.js';
  import ProcessTab from './ProcessTab.svelte';
  import MemoryStoreTab from './MemoryStoreTab.svelte';
  import ExecutionLogTab from './ExecutionLogTab.svelte';
  import CommunicationLogTab from './CommunicationLogTab.svelte';


  const store = writable('process');

  function logx(head, text) {
    communication_log.push({'head':head, 'text': text });
    // console.log(`${head}: ${text}`)
  }
  function setTab(tab) {
    store.set(tab);
  }
      let ws;

    const connect = () => {
        ws = new WebSocket('ws://localhost:8090/ws');

        ws.onopen = () => {
            // console.log('WebSocket is open now.');
            logx('sock', 'ws.onopen: WebSocket is open now.' );
        };

        ws.onmessage = (event) => {
            // console.log(`WebSocket message received: ${event.data}`);
            logx('sock', `WebSocket message received: ${event.data}`);

            let msg = JSON.parse(event.data);
            logx('receive', `msg(cmd=${msg.cmd}, object=${msg.object}, rc=${msg.rc}, cb=${msg.cb}, data=...)`)

            if ("cb" in msg) {
                let rtn = msg.cb
                // Update DatabaseStore....
                switch(rtn) {
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
                    case 'process_list_initial_load': process_list_initial_load(msg); break;
                    case 'memory_initial_load': memory_initial_load(msg); break;
                    case 'process_step_update': process_step_update(msg); break;
                  default: logx('fail', `No Such Routine: ${rtn}(msg(cmd=${msg.cmd}, object=${msg.object}, rc=${msg.rc}, cb=${msg.cb}, data=...))`)

                }
                // if (rtn in window) {
                //     logx('call', `${rtn}(msg(cmd=${msg.cmd}, object=${msg.object}, rc=${msg.rc}, cb=${msg.cb}, data=...))`)
                //     self[rtn](msg)
                // } else {
                //     logx('fail', `No Such Routine: ${rtn}(msg(cmd=${msg.cmd}, object=${msg.object}, rc=${msg.rc}, cb=${msg.cb}, data=...))`)
                // }
            } else {
                logx('fail',  `Message Must contain 'cb' property: ${msg}`);
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
    function sendMessage(msg) {
        if (ws && ws.readyState === WebSocket.OPEN) {
            let jmsg = JSON.stringify(msg);

            if (!window.hasOwnProperty(msg.cb)) {
                logx('fail', `Send of message with undefined callback ${msg.cb}`)
            }
                ws.send(jmsg);
                logx('send', `msg(cmd=${msg.cmd}, object=${msg.object}, cb=${msg.cb}, ...)`);
        } else {
            logx("fail","Attempt to sendMessage with WebSocket not open.");
        }
    }

    function process_list_initial_load(msg) {
      logx('call', 'in process_list_initial_load()' )
      let pl = msg['data'];
      for (let key in pl) {
        if (pl.hasOwnProperty(key)) {
          process_list[key] = pl[key];
        }
      }
      set_process_list(process_list)
    }

    function memory_initial_load(msg) {
      logx('call', 'in memory_initial_load()' )
      let mem = msg['data'];
      for (let key in mem) {
        if (mem.hasOwnProperty(key)) {
          memory_store[key] = mem[key];
        }
      }
    }

  let reload_steps

    function process_step_update(msg) {
      // console.log(`In process_step_update(${msg.data.name}...)`)
      let step =  msg['data'];
      let process = process_list[msg.object];
      let i = 0;
      for (; i < process_list[msg.object].length; i++) {
        if (process_list[msg.object][i]['name'] === step.name) {
            process_list[msg.object][i] = step;
            break;
        }
      }
      // console.log('Tabs::process_step_update(msg)')
      reload_steps()
      // set_process_list(process_list)
      // process_list = process_list;

      // process_list[msg.object] = process_list[msg.object];
      // process_list[msg.object][i] = process_list[msg.object][i];

    }




</script>

<style>
  .tabs {
    display: flex;
    justify-content: left;
    padding:  0;
    background-color: #f5f5f5;
    margin-bottom: 1em;
    border-radius: 8px;
  }

  .tab-content {
    padding: 1em;
    border: 1px solid darkBlue;
    border-radius: 8px;
    background: aliceblue;
    color: darkblue;
  }
  .tab-buttons {
    padding: 0.4em;
    border: 1px solid #ccc;
    border-radius: 18px;
    background-color: cornflowerblue;
    color: darkblue;
  }
</style>

<div class="tabs">
  <button class="tab-buttons" on:click={() => setTab('process')}>Process Tab</button>
  <button class="tab-buttons" on:click={() => setTab('memory')}>Memory Store Tab</button>
  <button class="tab-buttons" on:click={() => setTab('execution')}>Execution Log Tab</button>
  <button class="tab-buttons" on:click={() => setTab('communication')}>Communication Log Tab</button>

</div>

<div class="tab-content">
  {#if $store === 'process'}
    <ProcessTab on:sendMessage={sendMessageDispatch} bind:reload_steps={reload_steps}/>
  {:else if $store === 'memory'}
    <MemoryStoreTab />
  {:else if $store === 'execution'}
    <ExecutionLogTab />
  {:else}
    <CommunicationLogTab />
  {/if}
</div>


