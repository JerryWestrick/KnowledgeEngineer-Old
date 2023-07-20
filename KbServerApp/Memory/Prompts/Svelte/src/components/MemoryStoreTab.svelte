<script>
  import { memory_store } from './GlobalStorage.js';
  import TreeView from './TreeView.svelte'

  let selectedFile = '';
  let selectedContent = '';
  let originalContent = '';

  const selectFile = (file, content) => {
    selectedFile = file;
    selectedContent = content;
    originalContent = content;
    // console.log('File selected: ', file);
  }

  $: isModified = originalContent !== selectedContent;
</script>

<style>
  .container {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    font-size: 0.8em;
    color: blue;
    height: 100vh;
    overflow: hidden;
  }

  .file-browser {
    flex: 1;
    overflow-y: auto;
    white-space: nowrap;
  }

  .file-editor {
    flex: 3;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: auto;
    background: white;
    color: black;
    font-size: 0.8em;
  }

  .editor-content {
    flex-grow: 1;
    overflow: auto;
  }

  .save-button {
    align-self: flex-end;
    display: inline-block;
    border-radius: 12px;
    padding: 10px 20px;
    background: blue;
    color: white;
    font-size: 1em;
    cursor: pointer;
    margin: 1em 0;
  }

  .save-button:disabled {
    background: grey;
    cursor: not-allowed;
  }
</style>

<div class="container">
  <div class="file-browser">
    <TreeView label="Memory" tree={memory_store} {selectFile} />
  </div>

  <div class="file-editor">
    <h2>Selected File: {selectedFile}</h2>
    <textarea class="editor-content" bind:value={selectedContent}></textarea>
    <button class="save-button" on:click={() => console.log(`${selectedFile} contents were changed`)} disabled={!isModified}>Save</button>
  </div>
</div>
