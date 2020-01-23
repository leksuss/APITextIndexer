def global_files_stat(cursor):
    return cursor().files.aggregate([
        {'$group': {
            '_id': '',
            'max_size': {'$max': '$size'},
            'min_size': {'$min': '$size'},
            'avg_size': {'$avg': '$size'},
            'max_total_words': {'$max': '$total_words'},
            'min_total_words': {'$min': '$total_words'},
            'avg_total_words': {'$avg': '$total_words'},
            'max_uniq_words': {'$max': '$uniq_words'},
            'min_uniq_words': {'$min': '$uniq_words'},
            'avg_uniq_words': {'$avg': '$uniq_words'},
            'avg_uniq_words': {'$avg': '$uniq_words'},
            'count_files': {'$sum': 1}
        }},
        {'$unset': "_id"}
    ])


def global_filetypes_stat(cursor):
    return cursor().files.aggregate([
        {'$group': {
            '_id': '$ext',
            'count': {'$sum': 1},
        }},
        {'$project': {
            '_id': '',
            'ext': '$_id',
            'count': '$count',
        }},
        {'$unset': "_id"}
    ])


def global_list_files(cursor):
    return cursor().files.aggregate([
        {'$project': {
            '_id': 1,
            'path_name': {'$concat': ['$path', '$name']},
        }},
    ])


def global_frequent_word(cursor):
    frequent_word = cursor().words.find().sort('count', -1).limit(1)
    frequent_word = list(frequent_word)[0]
    frequent_word['_id'] = str(frequent_word['_id'])
    return [{'frequent_word': frequent_word}]


def global_rare_word(cursor):
    rare_word = cursor().words.find().sort('count').limit(1)
    rare_word = list(rare_word)[0]
    rare_word['_id'] = str(rare_word['_id'])
    return [{'rare_word': rare_word}]


def global_count_words(cursor):
    return cursor().files.aggregate([
        {'$group': {
            '_id': '',
            'total_words': {'$sum': '$total_words'},
            'uniq_words': {'$sum': '$uniq_words'}
        }},
        {'$unset': "_id"}
    ])


def global_avglen_word(cursor):
    avglen_words = cursor().words.aggregate([
        {'$project': {
            '_id': 0,
            'len_words': {'$multiply': ['$count', '$len']},
            'count': 1,
        }},
        {'$group': {
            '_id': '',
            'len_total_words': {'$sum': '$len_words'},
            'total_words': {'$sum': '$count'}
        }},
    ])
    res = list(avglen_words)[0]
    return [{'avglen_word': res['len_total_words'] / res['total_words']}]


def global_avglen_uniqword(cursor):
    return cursor().words.aggregate([
        {"$group": {"_id": "", "avglen_uniqword": {"$avg": "$len"}}},
        {'$unset': "_id"}
    ])


def global_vowcon_count(cursor):
    return cursor().words.aggregate([
        {"$group": {
            "_id": "",
            'vowel_count': {
                '$sum': {'$multiply': ['$vowel', '$count']}
            },
            'cons_count': {
                '$sum': {'$multiply': ['$consonant', '$count']}
            }
        }
        },
        {'$unset': "_id"}
    ])


def global_vowcon_count_uniqword(cursor):
    return cursor().words.aggregate([
        {"$group": {
            "_id": "",
            "vowel_count_uniqword": {"$sum": "$vowel"},
            "cons_count_uniqword": {"$sum": "$consonant"}
        }},
        {'$unset': "_id"}
    ])


def file_frequency_word(cursor, file_id, extremum):
    minmax = {'min': 1, 'max': -1}
    freq_word = cursor().words.find({
        'files.' + file_id: {'$exists': True}
    }).sort(
        'files.' + file_id, minmax[extremum]
    ).limit(1)[0]
    return {
        'word': freq_word['word'],
        'count': freq_word['files'][file_id],
    }


def file_avglen_word(cursor, file_id):
    avglen_words = cursor().words.aggregate([
        {'$match': {'files.' + file_id: {'$exists': True}}},
        {'$project': {
            '_id': 0,
            'len_words': {'$multiply': ['$files.' + file_id, '$len']},
            'count_words': '$files.' + file_id
        }},
        {'$group': {
            '_id': '',
            'len_total_words': {'$sum': '$len_words'},
            'total_words': {'$sum': '$count_words'},
        }},
    ])
    res = list(avglen_words)[0]
    return {'avglen_word': res['len_total_words'] / res['total_words']}


def file_avglen_uniqword(cursor, file_id):
    return cursor().words.aggregate([
        {'$match': {'files.' + file_id: {'$exists': True}}},
        {"$group": {"_id": "", "avglen_uniqword": {"$avg": "$len"}}},
        {'$unset': "_id"}
    ])


def file_vowcons_count(cursor, file_id):
    return cursor().words.aggregate([
        {'$match': {'files.' + file_id: {'$exists': True}}},
        {"$group": {
            "_id": "",
            'vowel_count': {
                '$sum': {
                    '$multiply': ['$vowel', '$files.' + file_id]
                }
            },
            'consonant_count': {
                '$sum': {
                    '$multiply': ['$consonant', '$files.' + file_id]
                }
            },
        }
        },
        {'$unset': "_id"}
    ])


def file_vowcons_count_uniqword(cursor, file_id):
    return cursor().words.aggregate([
        {'$match': {'files.' + file_id: {'$exists': True}}},
        {"$group": {
            "_id": "",
            "vowel_count_uniqword": {"$sum": '$vowel'},
            "consonant_count_uniqword": {"$sum": '$consonant'},
        }},
        {'$unset': "_id"}
    ])


def word_stat(cursor, searched, s_type='word'):
    word = cursor().words.find_one({s_type: searched})
    if word:
        files = cursor().files.find({
            '_id': {'$in': list(word['files'].keys())}})
        word['files_stat'] = []
        word_files = word.pop('files')
        for file in files:
            word['_id'] = str(word['_id'])
            word['files_stat'].append({
                '_id': file['_id'],
                'name': file['path'] + file['name'],
                'count': word_files[file['_id']],
            })
    return word


def file_stat(cursor, file_id):
    file = cursor().files.find_one({'_id': file_id})
    if file:
        file['frequent_word'] = file_frequency_word(cursor, file_id, 'max')
        file['rare_word'] = file_frequency_word(cursor, file_id, 'min')
        file.update(file_avglen_word(cursor, file_id))
        file.update(list(file_avglen_uniqword(cursor, file_id))[0])
        file.update(list(file_vowcons_count(cursor, file_id))[0])
        file.update(list(file_vowcons_count_uniqword(cursor, file_id))[0])
    return file


def words_stat(cursor):
    words = {}
    words.update(list(global_count_words(cursor))[0])
    words.update(global_avglen_word(cursor)[0])
    words.update(list(global_avglen_uniqword(cursor))[0])
    words.update(list(global_vowcon_count(cursor))[0])
    words.update(list(global_vowcon_count_uniqword(cursor))[0])
    words.update(list(global_rare_word(cursor))[0])
    words.update(list(global_frequent_word(cursor))[0])
    return words


def files_stat(cursor):
    files = list(global_files_stat(cursor))[0]
    files['ext_stat'] = list(global_filetypes_stat(cursor))
    files['list_files'] = list(global_list_files(cursor))
    return files
