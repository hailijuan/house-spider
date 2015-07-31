import datetime
from pymongo import MongoClient

ANTI_SPAM_PERIOD = 7

def within_anti_spam_period(older_time, recent_time):
    #do not save the same item in database
    return True
    older_date = datetime.datetime.strptime(older_time, "%Y-%m-%d %H:%M:%S")
    recent_date = datetime.datetime.strptime(recent_time, "%Y-%m-%d %H:%M:%S")
    return recent_date - older_date < datetime.timedelta(days = ANTI_SPAM_PERIOD)

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "house"

client = MongoClient(MONGODB_SERVER, MONGODB_PORT)
db = client[MONGODB_DB]

def recent_crawled_house(owner_mobile, resblock):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for doc in db['house_detail'].find({"owner_mobile": owner_mobile, "resblock": resblock}):
        if within_anti_spam_period(doc["create_time"], current_time):
            return True
    return False
