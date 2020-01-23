try:
    import pymongo
except ImportError:
    exit('You should install packages: pymongo')


def dbcursor(database='data_storage'):
    return pymongo.MongoClient()[database]
