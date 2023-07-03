import colors
from db import DB

if __name__ == '__main__':
    print(colors.SYSTEM + "--- start ---")  #
    Memory = DB('Memory')
    Memory.delete_dynamic_memory()

    #
    # We do this step by steps for debug...
    #
    # step_name = 'Prompts/Use Case Description to Requirements.pe'
    # step_name = 'Prompts/Requirements to Components.pe'
    step_name = 'Prompts/Test Globs.pe'

    print(f"{colors.SYSTEM}--- {step_name} ---")
    messages = Memory[step_name]
    for message in messages:
        print(message)
