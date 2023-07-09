<script>

  import Step from './Step.svelte'
  import { onMount, onDestroy } from 'svelte';
  import { process_list, mdt_routines, sendMessage } from './GlobalStorage.js'

  const __file_name__ = 'ProcessTab.svelte';
  onMount(() =>{
    mdt_routines[__file_name__] = mdt;
  });

  onDestroy(() => {
    delete mdt_routines[__file_name__];
  });


 let redraw_process_list = false;
  function mdt(ele) {
    // console.log(`${__file_name__}::mdt(${ele})`)
      if (ele.object === 'process_list') {
          redraw_process_list = !redraw_process_list;
          selectedProcess = selectedProcess;
          selectedStep = selectedStep;
      } else if (ele.object === 'step'){
          if (ele.process_name === selectedProcess && ele.step.name === step.name) {
              step = ele.step;
          }
      }
  }

 // setup dispatch of SendMessage
  let selectedProcess = null; // Object.keys(process_list)[0];
  let steps = null;


  const selectProcess = (event) => {
    selectedProcess = event.target.value;
    steps = process_list[selectedProcess];
  };

  let selectedStep = null; // Object.keys(process_list)[0];
  let step = null;


  const selectStep = (event) => {
    step = steps[selectedStep];
  };


    function execute_process(process_name) {
        let msg = {'process': selectedProcess};
        sendMessage({cmd: 'exec', object: 'process', cb: 'exec_process_log', record: msg})
    }



</script>


{#key redraw_process_list}
    {#if process_list !== null}
  <div class="container">
      <div>Process Tab </div>
      <div>Select process:</div>
      <select bind:value={selectedProcess} on:change={selectProcess}>
        {#each Object.keys(process_list) as key}
          <option value={key}>{key}</option>
        {/each}
      </select>
      <button class="edit-button" on:click={() => execute_process({selectedProcess})}>Execute Process</button>
<!--      <button class="edit-button" on:click={() => reload_steps()}>Reload Steps</button>-->
      <button class="edit-button" >Reload Steps</button>
  </div>
{/if}
  <div>
      {#if steps !== null}
    <select bind:value={selectedStep} on:change={selectStep}>
      {#each steps as step, step_no}
        <option value={step_no}>{step['name']} {step['prompt_name']}</option>
      {/each}
    </select>
          {/if}
  </div>
    {#if step !== null}
  <Step proc_name={selectedProcess} step={step} />

    {/if}
{/key}
<style>
   .card {
      box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
      transition: 0.3s;
      width: 90%;
      /*max-width: 600px;*/
      margin: 10px;
      border-radius: 8px;
      padding: 5px;
      font-size: 0.8rem;
      background-color: lightsteelblue;
      color: darkblue;
    }

    .card:hover {
      box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }

    .edit-button {
      background-color: #4CAF50;
      color: white;
      padding: 5px 12px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 0.7rem;
      margin: 4px 2px;
      transition-duration: 0.4s;
      cursor: pointer;
      border-radius: 5px;
    }

    .edit-button:hover {
      background-color: white;
      color: black;
      border: 2px solid #4CAF50;
    }

    .head-line {
      display: inline-block;
    }

   li {
    font-size: 0.7rem;
  }

  ul {
    margin: 0;
    padding-left: 20px;
  }

  pre {
    font-size: x-small;
  }


  .msg {
    display: inline-block;
  }
  .flex {
    display: inline-block;
  }

  .container {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    text-align: center;
    margin-left: auto;
  }

  .container > * {
    margin: 10px;
  }

  .edit-button {
    padding: 5px 10px;
  }
</style>

