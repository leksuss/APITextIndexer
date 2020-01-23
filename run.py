
try:
    import argparse
    import pymongo
    from bson import ObjectId
    from flask import Flask
    from flask_restful import Api, Resource
    from werkzeug.routing import BaseConverter
except ImportError:
    print('You should install packages: argparse, pymongo, flask_restful')


import responces
import folderparser


def dbcursor(database='data_storage'):
    return pymongo.MongoClient()[database]


class ObjectIDConverter(BaseConverter):

    @staticmethod
    def _is_hex(value):
        try:
            int(value, 16)
            return True
        except ValueError:
            return False

    def to_python(self, value):
        if self._is_hex(value) and len(value) == 24:
            return ObjectId(value)
        else:
            return ObjectId('0' * 24)


class HexConverter(BaseConverter):

    @staticmethod
    def _is_hex(value):
        try:
            int(value, 16)
            return True
        except ValueError:
            return False

    def to_python(self, value):
        if self._is_hex(value) and len(value) == 32:
            return value
        else:
            return '0' * 32


app = Flask(__name__)
app.url_map.converters['ObjectID'] = ObjectIDConverter
app.url_map.converters['Hex'] = HexConverter
app.url_map.strict_slashes = False
api = Api(app)


class Word(Resource):
    def get(self, word='', _id=''):
        if _id:
            stat_by_id = responces.word_stat(dbcursor, _id, s_type='_id')
            if stat_by_id:
                return stat_by_id, 200
            return {'error': 'there is no word with this _id'}, 404

        if word:
            stat_by_word = responces.word_stat(dbcursor, word)
            if stat_by_word:
                return stat_by_word, 200
            return {'error': f'there is no word "{word}" in the base'}, 404

        return responces.words_stat(dbcursor), 200


api.add_resource(
    Word,
    "/words/",
    "/words/<ObjectID:_id>",
    "/words/text/<string:word>"
)


class File(Resource):
    def get(self, _id=''):
        if _id:
            file_stat = responces.file_stat(dbcursor, _id)
            if file_stat:
                return file_stat, 200
            return {'error': 'there is no file with this _id'}, 404

        return responces.files_stat(dbcursor), 200


api.add_resource(
    File,
    "/files/",
    "/files/<Hex:_id>"
)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Collect text statistics from given folder with text files \
        in MongoDB with API interface. Support txt and docx file types',
        prog='APITextIndexer',
    )
    parser.add_argument(
        '-d',
        type=str,
        default='.',
        help='path to directory, default is current',
    )
    support_types = ['txt', 'md', 'docx']
    parser.add_argument(
        '-t',
        nargs='*',
        default=['txt'],
        choices=support_types,
        help=f"file types, support {', '.join(support_types)}, default is txt",
    )
    folderparser.run(parser.parse_args())
    print("Okay, now run API server\n================")
    app.run(debug=False)
