<script>
    export let proc_name
    export let step

    // console.log(`Steps::my proc_name=${proc_name}`)
    // console.log(`Steps::my step=${step}`)

    export function update_steps(idx) {
        console.log(`Steps::update_steps(${idx})`);
    }


    // const editStep = (step) => {
    //   // Edit step logic here
    //   console.log('Edit step', step);
    // };

  const display_type =
          {'name': 'key_h3',
          'prompt_name': 'key_str',
          'ai': 'key_ai',
          'storage_path': 'key_str',
          'messages': 'key_msg',
          'response': 'key_obj',
          'answer': 'key_pre',
          'files': 'key_obj_pre',
          'prompt_tokens': 'key_str',
          'completion_tokens': 'key_str',
          'total_tokens': 'key_str',
          'elapsed_time': 'key_str',
          };



function toggleContent(id) {
    console.log(`in toggleContent(${id})`)
  var element = document.getElementById(id);
  if (element) {
    element.classList.toggle('expanded');
  }
}

</script>

<style>
    .card {
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
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
        box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2);
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

    pre {
        font-size: x-small;
    }


    .collapsible {
  /*white-space: nowrap;*/
  /*overflow: hidden;*/
  /*text-overflow: ellipsis;*/
  /*cursor: pointer;*/
}
.collapsible.expanded {
  white-space: pre;
}

</style>



<div class="card">

{#each Object.entries(step) as [key, value] }

  {#if display_type[key] === 'key_str'}
    <div><strong>{key}:</strong> {step[key]}</div>
  {:else if display_type[key] === 'key_h3'}
    <h2>{step[key]}</h2>
  {:else if display_type[key] === 'key_ai'}
    <div><strong>{step[key]['model']}</strong>(temp={step[key]['temperature']},max_tokens={step[key]['max_tokens']},mode={step[key]['mode']})</div>
  {:else if display_type[key] === 'key_pre'}
    <div><strong>{key}:</strong><pre>{step[key]}</pre></div>
  {:else if display_type[key] === 'key_obj'}
    <strong>{key}: </strong>
    <ul>
      {#each Object.entries(step[key]) as [subKey, subValue]}
        <li>{subKey}: {JSON.stringify(subValue)}</li>
      {/each}
    </ul>
  {:else if display_type[key] === 'key_msg'}
    <div >
      <strong style="vertical-align: top;font-size: x-small;">Msg: </strong>
      <div style="display: inline-block;font-size: x-small;background-color: lightblue;
    border-radius: 8px;">
        {#each value as msg, msg_no}
          <strong>{msg['role']}:</strong>
<!--            <pre >{msg['content']}</pre>-->
            <pre class="collapsible" id="{`cc-${msg_no}`}" onclick={() => toggleContent("nada")}>
            {msg['content']}
            </pre>


        {/each}
      </div>
    </div>
  {:else if display_type[key] === 'key_obj_pre'}
    <strong>{key}: </strong>
    <ul>
      {#each Object.entries(step[key]) as [subKey, subValue]}
        <li>{subKey}: <pre>{subValue}</pre></li>
      {/each}
    </ul>
  {:else}
    <div><strong>???{key}:</strong> {step[key]}</div>
  {/if}
{/each}
<!--<button class="edit-button" on:click={() => editStep(step)}>Edit</button>-->
</div>


