import uuid
import datetime
import hashlib
import random

class Utils:
    @classmethod
    def new_uuid(cls, hexornot=1):
        if hexornot == 1:
            return uuid.uuid4().hex
        return str(uuid.uuid4())

    @classmethod
    def get_local_date(cls):
        return datetime.datetime.now().strftime("%d/%m/%Y")

    @classmethod
    def gethash(cls, data):
        hash_obj = hashlib.sha256(data.encode())
        return hash_obj.hexdigest()

    @classmethod
    def generate_code(cls):
        return str(random.randint(0, 9999)).zfill(4)

    @classmethod
    def linha(cls):
        return '[+]' + ('=' * 30) + '[+]'

    @classmethod
    def getdatenow(cls, hora=False):
        atual = datetime.datetime.now()
        dia = atual.strftime('%d/%m/%Y')
        hora = atual.strftime('%H:%M:%S')
        if hora:
            return f'{dia} - {hora}'
        return dia
