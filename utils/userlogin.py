from flask_pymongo import PyMongo

def getUser(user_id, mongo):
    users = mongo.db.users
    res = users.find_one({"id":user_id})
    return res

class UserLogin():
    def fromDB(self, user_id, mongo):
        self.__user = getUser(user_id, mongo)
        return self

    def create(self, user):
        self.__user=user
        return self

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return (self.__user['id'])
    
    def get_user(self):
        return self.__user['username']

    def get_pass(self):
        return self.__user['password']
    
    def has_avatar(self):
        try:
            return self.__user['has_avatar']
        except:
            return None
    def has_summary(self):
        try:
            return self.__user['summary']
        except:
            return None
