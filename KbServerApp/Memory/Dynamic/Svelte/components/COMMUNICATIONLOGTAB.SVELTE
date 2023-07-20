<script>
    import {communication_log} from './GlobalStorage.js'
</script>

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

<div>
  <h2>Communication Log</h2>
  {#each communication_log as log, index (index)}
    <div class="comm-line">
      <div class="comm-content log_{log.head}"><div><strong>{log.head} </strong></div><div class="comm-details">:&nbsp;{log.text}</div></div>
    </div>
  {/each}
</div>