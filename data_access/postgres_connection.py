import psycopg2

PG_SET_SEARCH_PATH = "SET SEARCH_PATH TO %s"


class PostgresConnection(object):
    def __init__(self, db_host=None, db_port=None, db_name=None, db_user=None, db_password=None):
        self.init(db_host, db_port, db_name, db_user, db_password)

    def init(self, db_host, db_port, db_name, db_user, db_password):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.pg_conn = None

    def connect(self):
        try:
            self.pg_conn = psycopg2.connect(database=self.db_name, user=self.db_user, port=self.db_port, host=self.db_host, password=self.db_password)
        except Exception as e:
            print "Postgres Connection failure", e
            raise Exception()

    def get_cursor(self):
        return self.pg_conn.cursor()

    def commit(self):
        self.pg_conn.commit()

    def disconnect(self):
        if self.pg_conn:
            self.pg_conn.close()

    def connect_to_schema(self, schema_name):
        cur = self.pg_conn.cursor()
        cur.execute(PG_SET_SEARCH_PATH, (schema_name,))
        self.pg_conn.commit()

    def get_conn(self):
        return self.pg_conn