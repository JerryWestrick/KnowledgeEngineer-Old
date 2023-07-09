<script>
  import CommunicationLogTab from './CommunicationLogTab.svelte';

  import { writable } from 'svelte/store';
  import ProcessTab from './ProcessTab.svelte';
  import MemoryStoreTab from './MemoryStoreTab.svelte';
  import ExecutionLogTab from './ExecutionLogTab.svelte';


  const store = writable('process');
  function setTab(tab) {
      store.set(tab);
    }

</script>

<div class="tabs">
  <button class="tab-buttons" on:click={() => setTab('process')}>Process Tab</button>
  <button class="tab-buttons" on:click={() => setTab('memory')}>Memory Store Tab</button>
  <button class="tab-buttons" on:click={() => setTab('execution')}>Execution Log Tab</button>
  <button class="tab-buttons" on:click={() => setTab('communication')}>Communication Log Tab</button>

</div>

<div class="tab-content">
  {#if $store === 'process'}
    <ProcessTab />
  {:else if $store === 'memory'}
    <MemoryStoreTab />
  {:else if $store === 'execution'}
    <ExecutionLogTab />
  {:else}
    <CommunicationLogTab />
  {/if}
</div>


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
    padding: 0;
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

