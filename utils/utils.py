import uuid
import datetime
import hashlib
import random

class Utils:
    @classmethod
    def new_uuid(cls):
        new_id = uuid.uuid4().hex
        return new_id

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