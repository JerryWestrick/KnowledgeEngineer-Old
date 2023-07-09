<script>

  import {exec_log} from './GlobalStorage.js'
  // let exec_log = [
  //   {'time': '2023-06-01 08:30:27', 'system': 'STEP', 'line': 'This is a log message that shows something happened.'},
  //   {'time': '2023-06-01 08:30:27', 'system': 'STEP', 'line': 'This is another log message.'}
  // ];

  let expandedLogs = new Set();

  function toggleExpanded(index) {
    if (expandedLogs.has(index)) {
      expandedLogs.delete(index);
    } else {
      expandedLogs.add(index);
    }
    // Trigger reactivity
    expandedLogs = new Set([...expandedLogs]);
  }
</script>

<style>
  .log-line {
    border: 1px solid #ddd;
    padding: 10px;
    margin-bottom: 10px;
    cursor: pointer;
    font-size: 0.8rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .log-line:hover {
    background-color: #f5f5f5;
  }

  .log-content {
    display: flex;
    justify-content: space-between;
  }

  .log-content p {
    margin: 0;
  }

  .log-details {
    flex-grow: 1;
    margin-left: 10px;
  }
</style>

<div>
  <h2>Execution Log</h2>
  {#each exec_log as log, index (index)}
    <div class="log-line" on:click={() => toggleExpanded(index)}>
      <div class="log-content">
        <p><strong>{log.time} [{log.system}]</strong></p>
        {#if expandedLogs.has(index)}
          <p class="log-details">{log.line}</p>
        {:else}
          <p class="log-details">{log.line.split('\n')[0]}...</p>
        {/if}
      </div>
    </div>
  {/each}
</div>
