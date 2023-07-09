<script>
  import TreeView from './TreeView.svelte'
  import { onMount, onDestroy } from 'svelte';
  import { memory_store, mdt_routines } from './GlobalStorage.js'

  const __file_name__ = 'MemoryStoreTab.svelte';
  onMount(() =>{
    mdt_routines[__file_name__] = mdt;
  });

  onDestroy(() => {
    delete mdt_routines[__file_name__];
  });

  let selectedFile = '';
  let selectedContent = '';
  let originalContent = '';

  const selectFile = (file, content) => {
    selectedFile = file;
    selectedContent = content;
    originalContent = content;
    // console.log(`${__file_name__}::selectFile(file=${file}, content=${content})`);
  }

  let redraw_file_browser = false;
  let redraw_file_content = false;

  export function mdt(ele) {
    // console.log(`${__file_name__}::mdt(${ele})`)

    if (ele.object === 'memory_store') {
      redraw_file_browser = !redraw_file_browser;
    } else if (ele.object === 'File') {
      selectFile(ele.name, ele.content)
    }
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
    height: 90vh;
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
  {#key redraw_file_browser}
      <TreeView label="Memory" tree={memory_store} {selectFile} />
  {/key}
    </div>
    <div class="file-editor">
    <div>Selected File: {selectedFile}</div>
      <textarea class="editor-content" bind:value={selectedContent}></textarea>
      <button class="save-button" on:click={() => console.log(`${selectedFile} contents were changed`)} disabled={!isModified}>Save</button>
    </div>
</div>
