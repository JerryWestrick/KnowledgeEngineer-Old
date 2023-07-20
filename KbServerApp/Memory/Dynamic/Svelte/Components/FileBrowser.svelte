<script>
  import { onMount } from 'svelte';
  import { memory_store } from './GlobalStorage.js';
  let selectedFile = '';
  let fileContent = '';

  onMount(() => {
    selectedFile = Object.keys(memory_store)[0];
    fileContent = memory_store[selectedFile];
  });

  function selectFile(file) {
    selectedFile = file;
    fileContent = memory_store[file];
  }
</script>

<style>
  .file-browser {
    display: flex;
  }
  .directory-list {
    width: 25%;
    overflow: auto;
  }
  .file-editor {
    width: 75%;
    overflow: auto;
  }
</style>

<div class="file-browser">
  <div class="directory-list">
    <ul>
      {#each Object.keys(memory_store) as file}
        <li on:click={() => selectFile(file)}>{file}</li>
      {/each}
    </ul>
  </div>
  <div class="file-editor">
    <textarea bind:value={fileContent}></textarea>
  </div>
</div>