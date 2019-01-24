import re


def clear_phone(string):
    clear_str = re.sub(r"\D", "", string)

    if clear_str.startswith('+'):
        clear_str = clear_str[1:]
    if clear_str.startswith('8'):
        clear_str = '7' + clear_str[1:]

    return '+' + clear_str[:11]


def format_phone(string):
    return ''.join([
        '+',
        string[:1],
        ' (',
        string[1:4],
        ') ',
        string[4:7],
        '-',
        string[7:9],
        '-',
        string[9:11]
    ])
