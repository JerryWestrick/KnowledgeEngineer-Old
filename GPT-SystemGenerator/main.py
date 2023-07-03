import argparse
import time

from ai import AI
from db import DB
import colors

from logger import Logger
from step import Step
from OpenAI_API_Costs import OpenAI_API_Costs

from Processes import ProcessList

_ = Logger('Memory/Logs/TestRun.log')  # Is a singleton, so ignore result.


def schedule(pname: str):
    tasklist = ProcessList[pname]
    start_time = time.time()
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    p_cost = 0.0
    c_cost = 0.0
    total = 0.0

    for step in tasklist:
        ai_model = step.ai.model
        pricing = OpenAI_API_Costs[ai_model]
        step.run()
        prompt_tokens += step.prompt_tokens
        completion_tokens += step.completion_tokens
        total_tokens += step.total_tokens
        sp_cost = pricing['input'] * (step.prompt_tokens / 1000)
        sc_cost = pricing['output'] * (step.completion_tokens / 1000)
        s_total = sp_cost + sc_cost
        p_cost += sp_cost
        c_cost += sc_cost
        total += p_cost + c_cost
        Logger.log('STEP', f'Cost Estimate: Total: {s_total:.4f} ('
                           f' Prompt: {sp_cost:.4f}'
                           f' Completion: {sc_cost:.4f})')

    elapsed = time.time() - start_time
    Logger.log('RUN', f'Elapsed: {elapsed:.2f}s'
                      f' Cost Estimate: Total: {total:.4f} ('
                      f' Prompt: {p_cost:.4f}'
                      f' Completion: {c_cost:.4f})')

    # Logger.log('RUN', f'Estimated Cost: Total: ${total:.4f}, (Prompt: ${p_cost:.4f}, Completion: ${c_cost:.4f})')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='main.py',
        description='Uses OpenAI LLM models to generate system from description',
        epilog='good luck'
    )
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo', help='model (see --list_models)')
    parser.add_argument('--temperature', type=float, default=0.0, help='temperature')
    parser.add_argument('--max_tokens', type=int, default=2000, help='max tokens')
    parser.add_argument('--list_models', action='store_true', help='list available models')
    parser.add_argument('--target', type=str, default='php', help='target technology: test, php or flask')
    # parser.add_argument('--log_file', type=str, default='Memory/Logs/Some Freaking Run',
    #                     help='Log File Name (Memory/Logs/Some Freaking Run)')
    parser.add_argument('--log', nargs='+',
                        choices=['SYSTEM', 'LLM', 'PROMPT', 'REPLY', 'EXEC', 'ERROR', 'INFO', 'DEBUG', 'WARNING', 'RUN',
                                 'STEP', 'MEMORY', 'RESPONSE'],
                        help='Enable logging for the specified subsystems')
    parser.add_argument('--no_log', nargs='+',
                        choices=['SYSTEM', 'LLM', 'PROMPT', 'REPLY', 'EXEC', 'ERROR', 'INFO', 'DEBUG', 'WARNING', 'RUN',
                                 'STEP', 'MEMORY', 'RESPONSE'],
                        help='Disable logging for the specified subsystems')
    args = parser.parse_args()

    if args.list_models:
        print(colors.SYSTEM + "Available models:")
        for model in sorted(AI.list_models()):
            print(f"{colors.SYSTEM}{model}")
        exit()

    process_name = args.target
    if process_name not in ProcessList:
        print(colors.ERROR + f"Invalid Target Technology {process_name}")
        print(colors.ERROR + f"Expected {ProcessList.keys()}")
        exit()

    mode = 'chat'
    if 'davinci' in args.model:
        mode = 'complete'

    # if args.model is not None:
    #     for i in range(len(process)):
    #         process[i].ai.model = args.model
    #         process[i].ai.mode = mode

    if args.log:
        for log in args.log:
            Logger.enable_logging(log)

    if args.no_log:
        for log in args.no_log:
            Logger.disable_logging(log)

    Memory = DB('Memory')

    Logger.log('RUN', f"--- start {process_name} ---")  #
    Memory.delete_dynamic_memory(process_name)
    schedule(process_name)
    Logger.log('RUN', f"{args.target} Generated")

    Logger.log('RUN', f"--- end of run ---")
