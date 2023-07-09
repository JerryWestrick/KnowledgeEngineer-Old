<script>
  import { onMount, onDestroy } from 'svelte';
  import { communication_log, mdt_routines } from './GlobalStorage.js'

  const __file_name__ = 'CommunicationLogTab.svelte'

  let redraw_communication_log = false;
  function mdt(ele) {
    // console.log(`${__file_name__}::mdt(${ele})`)
    if (ele.object === 'communication_log') {
      redraw_communication_log = !redraw_communication_log
    }
  };

  onMount(() =>{
    mdt_routines[__file_name__] = mdt;
  });

  onDestroy(() => {
    delete mdt_routines[__file_name__];
  });
</script>


<div>
  <h2>Communication Log</h2>
  {#key redraw_communication_log}
    {#each communication_log as log, index (index)}
      <div class="comm-line">
        <div class="comm-content log_{log.head}"><div><strong>{log.head} </strong></div><div class="comm-details">:&nbsp;{log.text}</div></div>
      </div>
    {/each}
  {/key}
</div>

<style>
  .comm-line {
    border: 1px solid lightgrey;
    cursor: pointer;
    font-size: 0.8rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    background-color: white;
    border-radius: 4px;
  }

  .comm-line:hover {
    background-color: #f5f5f5;
  }

  .comm-content {
    display: flex;
    justify-content: space-between;
  }

  .comm-content div {
    margin: 0;
  }

  .comm-details {
    flex-grow: 1;
    margin-left: 10px;
  }

  .log_fail {
    color: darkRed;
  }
  .log_receive {
    color: darkGreen;
  }
  .log_sock {
    color: darkCyan;
  }
</style>
