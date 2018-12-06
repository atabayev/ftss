def converter_ru_to_lt(text):
    letter = {
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Д": "D",
        "Е": "E",
        "Ё": "E",
        "Ж": "ZH",
        "З": "Z",
        "И": "I",
        "Й": "I",
        "К": "K",
        "Л": "L",
        "М": "M",
        "Н": "N",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "X": "H",
        "Ц": "C",
        "Ч": "CH",
        "Ш": "SH",
        "Щ": "SH",
        "Ы": "I",
        "Ь": "O",
        "Э": "E",
        "Ю": "YU",
        "Я": "YA"
    }
    res = ''
    nums = [str(i) for i in range(10)]
    for symbol in text:
        if symbol.upper() in letter:
            if symbol.upper() not in nums:
                res += letter[symbol.upper()]
        else:
            res += symbol.upper()
    return res


def send_sms_to_client(phone_number):
    # TODO: Через Firebase выполнить отправку СМС на указаный номер
    pass
