import json
import urllib.parse
import urllib.request

from utils.utils import Utils


class Database:
    def __init__(self):
        self.db_url = 'http://127.0.0.1:5000/'

    @staticmethod
    def db_post_access(url, data):
        json_data = json.dumps(data).encode()

        req = urllib.request.Request(url, data=json_data)
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())

    def cadastrar(self, email, password):
        data = {
            'email': email,
            'pass': Utils.gethash(password),
            'wallet': Utils.new_uuid(),
            'data': Utils.get_local_date(),
            'currency': 0,
            'tfa': 0
        }
        cad_url = self.db_url + 'cadastro'
        #encoded_data = urllib.parse.urlencode(data).encode('utf-8') -> GET

        success = self.db_post_access(cad_url, data)
        return success

    def transaction(self, swallet, dwallet, value):
        trans_url = self.db_url + 'updatecurrency'
        data = {'operation': 'sub', 'wallet': swallet, 'nvalue': value}
        data2 = {'operation': 'add', 'wallet': dwallet, 'nvalue': value}

        success = self.db_post_access(trans_url, data)
        success2 = self.db_post_access(trans_url, data2)
        self.add_histoy(swallet, dwallet, value)
        return [success, success2]

    def seeinfo(self, wallet, password):
        info_url = self.db_url + 'seeinfos'

        data = {'wallet': wallet, 'pass': password}

        infos = self.db_post_access(info_url, data)
        return infos['infos']

    def getcurrency(self, wallet, password):
        cur_url = self.db_url + 'getcurrency'

        data = {'wallet': wallet, 'pass': Utils.gethash(password)}
        return self.db_post_access(cur_url, data)["currency"]

    def email_exists(self, email):
        email_url = self.db_url + 'email-exists'
        data = {'email': email}

        ex = self.db_post_access(email_url, data)
        if ex['exists'] == 'true':
            return True
        return False

    def atualizar_2fa(self, email, password):
        tfa_url = self.db_url + 'tfaupdate'
        data = {'email': email, 'pass': Utils.gethash(password)}

        success = self.db_post_access(tfa_url, data)
        return success

    def verifica_tfa(self, email, password):
        tfa_url = self.db_url + 'istfaenabled'
        data = {'email': email, 'pass': Utils.gethash(password)}

        result = self.db_post_access(tfa_url, data)
        if result['status'] == 'true':
            return True
        return False

    def login(self, email, password):
        login_url = self.db_url + 'login'
        data = {'email': email, 'pass': Utils.gethash(password)}

        return self.db_post_access(login_url, data)

    def add_histoy(self, swallet, dwallet, value):
        history_url = self.db_url + 'add-history'

        data = {'swallet': swallet, 'dwallet': dwallet, 'date': Utils.getdatenow(True), 'value': value}

        return self.db_post_access(history_url, data)


if __name__ == '__main__':
    '''
    twallet = '4bf2ee7697ed46daac4ca953b100c76a'
    senha = Utils.gethash('vagabunda123')
    db = Database()
    #db.cadastrar('vagabunda@gmail.com', 'vagabunda123')
    db.transaction('sub', twallet, 15, senha)
    db.getcurrency(twallet, senha)
    db.seeinfo(twallet, senha)
    '''
    senha = Utils.gethash('vagabunda123')

    db = Database()
    db.cadastrar('vagabunda@gmail.com', 'vagabunda123')
    db.email_exists('vagabunda@gmail.com')
    db.seeinfo('vagabunda@gmail.com', senha)
    db.atualizar_2fa('vagabunda@gmail.com', senha)
