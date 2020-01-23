import os
import re
import uuid

import IOfile
from dbhandler import dbcursor


def get_lang_mask(char_type):
    chars = {
        'consonants': {
            'rus': 'бвгджзйклмнпрстфхцчшщ',
            'eng': 'bcdfghjklmnpqrstvwxyz',
        },
        'vowels': {
            'rus': 'ауоыиэяюёе',
            'eng': 'aeiou',
        },
        'patterns': {
            'rus': 'а-я',
            'eng': 'a-z',
        }
    }
    return tuple(''.join(chars[char_type].values()))


def get_files_to_index(folder, filetypes):
    allfiles = []
    for root_path, dirs, files in os.walk(folder):
        for file in files:
            file_ext = file.split('.')[-1]
            if file_ext in filetypes:
                abspath = os.path.abspath(root_path) + '/'
                path_to_file = abspath + file
                allfiles.append({
                    '_id': uuid.uuid4().hex,
                    'name': file,
                    'path': abspath,
                    'ext': file_ext,
                    'size': os.path.getsize(path_to_file),
                })
    return allfiles


def count_chars(word, mask):
    counter = 0
    char_mask = get_lang_mask(mask)
    for char in word:
        if char in char_mask:
            counter += 1
    return counter


def get_words_from(file, word_counted):
    res_file = IOfile.read(
        file['path'] + file['name'],
        file['ext']
    )
    if not res_file[0]:
        return res_file
    lang_mask = ''.join(get_lang_mask('patterns'))
    pattern = r'\b(?<![0-9]-)[' + lang_mask + '][-' + lang_mask + ']*'
    words = re.findall(pattern, res_file[1].lower())
    for word in words:
        if word not in word_counted:
            word_counted[word] = {
                "word": word,
                "count": 1,
                "len": len(word),
                "vowel": count_chars(word, 'vowels'),
                "consonant": count_chars(word, 'consonants'),
                "files": {file['_id']: 1},
            }
        else:
            word_counted[word]["count"] += 1
            word_counted[word]["files"][file['_id']] = \
                word_counted[word]["files"].get(file['_id'], 0) + 1
    return word_counted, {'total_words': len(words),
                          'uniq_words': len(set(words))}


def run(cli_args):
    file_list = get_files_to_index(cli_args.d, cli_args.t)
    if not file_list:
        exit(f'There is no {" or ".join(cli_args.t)} files in folder')
    word_counted = {}
    total_words = 0
    res_file_list = []
    for file in file_list:
        res_words = get_words_from(file, word_counted)
        if not res_words[0]:
            print(file['path'] + file['name'], res_words[1], sep=' - ')
        else:
            word_counted = res_words[0]
            file.update(res_words[1])
            res_file_list.append(file)
            total_words += res_words[1]['total_words']
    print(f"Found {len(res_file_list)} files with {total_words} total words.")
    print("Saving to MongoDB...")
    colnames = dbcursor().list_collection_names()
    if 'files' in colnames:
        dbcursor().files.drop()
    if 'words' in colnames:
        dbcursor().words.drop()
    dbcursor().files.insert_many(res_file_list, ordered=False)
    dbcursor().words.insert_many(word_counted.values(), ordered=False)
