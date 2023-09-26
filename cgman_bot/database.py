from pymongo import MongoClient
client = 'mongodb+srv://thecgman56:iamragnarok04123@cluster0.amzho9t.mongodb.net/'
connection_string = MongoClient(client)
database_name = connection_string['Wolfonix_media']
collection = database_name['Wolfonix_media']
staff = database_name['Wolfonix_staff']
