from step import Step
from ai import AI

ProcessList = {
    'flask': [
        Step(name='Step 1', prompt_name='Prompts/Flask/Use Case Description to Requirements.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/Requirements'
             ),
        Step(name='Step 2', prompt_name='Prompts/Flask/Requirements to Components.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/System Components'
             ),
        Step(name='Step 3', prompt_name='Prompts/Flask/Database Component Requirements to DDL.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/System Specifications'
             ),
        Step(name='Step 4', prompt_name='Prompts/Flask/Generate Database Test Data.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/System Specifications'
             ),
        Step(name='Step 5', prompt_name='Prompts/Flask/Generate flask Rest API.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/Flask Code'
             ),
        Step(name='Step 6', prompt_name='Prompts/Flask/Generate User GUI.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/Flask Code/www'
             ),
    ],

    'php': [
        Step(name='Step 1', prompt_name='Prompts/PHP/Use Case Description to Requirements.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/Requirements'
             ),
        Step(name='Step 2', prompt_name='Prompts/PHP/Requirements to Components.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/System Components'
             ),
        Step(name='Step 3', prompt_name='Prompts/PHP/Database Component Requirements to DDL.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/System Specifications'
             ),
        Step(name='Step 4', prompt_name='Prompts/PHP/Generate Database Test Data.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/System Specifications'
             ),
        Step(name='Step 5', prompt_name='Prompts/PHP/Generate PHP Application.pe',
             ai=AI(model='gpt-3.5-turbo', mode='complete', temperature=0, max_tokens=3000),
             storage_path='Dynamic/Flask Code'
             ),
    ],

    'test': [
        Step(name='Step 1', prompt_name='Prompts/Test Prompt.pe',
             ai=AI(model='gpt-3.5-turbo', mode='chat', temperature=0, max_tokens=3000),
             storage_path='Dynamic/Requirements'
             ),
        Step(name='Step 2', prompt_name='Prompts/Test Prompt 2.pe',
             ai=AI(model='gpt-4', mode='chat', temperature=0, max_tokens=3000),
             storage_path='Dynamic/Components'
             ),
    ],

}