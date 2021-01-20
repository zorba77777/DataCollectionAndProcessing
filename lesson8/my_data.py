class MyVkData:

    my_user_id = '296612364'

    app_id = 6350686

    @staticmethod
    def get_login():
        f = open('./login.txt', 'r')
        login = f.read().rstrip()
        f.close()
        return login

    @staticmethod
    def get_password():
        f = open('./pass.txt', 'r')
        passw = f.read().rstrip()
        f.close()
        return passw

    @staticmethod
    def get_token():
        f = open('./token.txt', 'r')
        token = f.read().rstrip()
        f.close()
        return token
