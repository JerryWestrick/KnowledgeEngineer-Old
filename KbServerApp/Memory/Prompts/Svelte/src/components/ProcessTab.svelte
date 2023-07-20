<script>
  import { writable } from 'svelte/store';
  import {process_list} from './GlobalStorage.js'
  import Step from './Step.svelte'

  export function reload_steps() {
    console.log(`Process::reload_steps()...`);
     toggled = !toggled;
  }

  // setup dispatch of SendMessage
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  let selectedProcess = 'test'; // Object.keys(process_list)[0];
  let steps = writable(process_list[selectedProcess]);


  const selectProcess = (event) => {
    selectedProcess = event.target.value;
    steps.set(process_list[selectedProcess]);
  };

  let selectedStep = 0; // Object.keys(process_list)[0];
  let step = writable(process_list[selectedProcess][0]);


  const selectStep = (event) => {
    step.set(steps[selectedStep]);
  };

  function execute_process(event) {
    let msg = {'process': event.selectedProcess};
    dispatch('sendMessage', {cmd: 'exec', object: 'process', cb: 'exec_process_log', record: msg})
  }



function update_steps( ) {
    steps.set(process_list[selectedProcess]);
}



  let toggled = false


</script>

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

<div class="container">
  <div>Process Tab</div>
  <div>Select process:</div>
  <select bind:value={selectedProcess} on:change={selectProcess}>
    {#each Object.keys(process_list) as key}
      <option value={key}>{key}</option>
    {/each}
  </select>
  <button class="edit-button" on:click={() => execute_process({selectedProcess})}>Execute Process</button>
  <button class="edit-button" on:click={() => reload_steps()}>Reload Steps</button>
</div>



  <div>
    <select bind:value={selectedStep} on:change={selectStep}>
      {#each process_list[selectedProcess] as step, step_no}
        <option value={step_no}>{step['name']} {step['prompt_name']}</option>
      {/each}
    </select>
  </div>

  <Step proc_name={selectedProcess} step={process_list[selectedProcess][selectedStep]} />

