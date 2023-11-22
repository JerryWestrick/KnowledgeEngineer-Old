OpenAI_API_Costs = {
    'gpt-4-1106-preview':
        {'model': 'gpt-4-1106-preview', 'title': 'GPT-4 Turbo',
         'RPM': 200, 'TPM': 40000, 'input': 0.0100, 'output': 0.0300},
    'gpt-4':
        {'model': 'gpt-4', 'title': 'GPT-4 (8k)',
         'RPM': 200, 'TPM': 40000, 'input': 0.0300, 'output': 0.0600},
    # 'text-davinci-003':
    #     {'model': 'text-davinci-003', 'title': 'davinci (most powerful)',
    #      'RPM': 3000, 'TPM': 250000, 'input': 0.0200, 'output': 0.0200},
    'gpt-3.5-turbo-16k':
        {'model': 'gpt-3.5-turbo-16k', 'title': 'gpt-3.5-turbo (16K)',
         'RPM': 3500, 'TPM': 90000, 'input': 0.0030, 'output': 0.0040},
    'gpt-3.5-turbo':
        {'model': 'gpt-3.5-turbo', 'title': 'gpt-3.5-turbo (4K)',
         'RPM': 3500, 'TPM': 90000, 'input': 0.0015, 'output': 0.0020},
    # 'text-curie-001':
    #     {'model': 'text-curie-001', 'title': 'curie',
    #      'RPM': 3000, 'TPM': 250000, 'input': 0.0020, 'output': 0.0020},
    # 'text-babbage-001':
    #     {'model': 'text-babbage-001', 'title': 'babbage',
    #      'RPM': 3000, 'TPM': 250000, 'input': 0.0005, 'output': 0.0005},
    # 'text-ada-001':
    #     {'model': 'text-ada-001', 'title': 'ada (fastest)',
    #      'RPM': 3000, 'TPM': 250000, 'input': 0.0004, 'output': 0.0004}
}
