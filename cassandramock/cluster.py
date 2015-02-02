import sqlite3
import uuid

class Future(object):

    def __init__(self, result):
        self._result = result

    def result(self):
        return [element for element in self._result] if self._result else []

    def add_callbacks(self, callback=None, errback=None, callback_args=(),
                      callback_kwargs={}):
        try:
            callback(self.result(), **callback_kwargs)
        except Exception as ex:
            errback(ex)

class Session(object):

    def __init__(self, conn, keyspace):

        self.conn = conn
        self.keyspace = keyspace
        self.mappings = {}
        self.tokens = ['AND', 'OR']

    def execute(self, query, queryargs):
        # Health check.
        if 'system.local' in query:
            return 'true'

        original_query = query
        res = None
        query = query.upper()
        query = query.replace('false', '0')
        query = query.replace('true', '1')

        if isinstance(queryargs, tuple):

            # convert UUID to string
            queryargs = tuple([str(s) if isinstance(s, uuid.UUID)
                           else s for s in queryargs])

            # sqlite prefers ? over %s for positional args
            query = query.replace('%S', '?')

        elif isinstance(queryargs, dict):

            # If the user passed dictionary arguments, assume that they
            # used that cassandra %(fieldname)s and convert to sqlite's
            # :fieldname

            for k, v in queryargs.items():
                cass_style_arg = "%({0})S".format(k)
                sqlite_style_arg = ":{0}".format(k)
                query = query.replace(cass_style_arg, sqlite_style_arg)

                # Convert UUID parameters to strings
                if isinstance(v, uuid.UUID):
                    queryargs[k] = str(v)

        if query.strip().startswith("INSERT"):
            # It's all upserts in Cassandra
            query = query.replace("INSERT", "INSERT OR REPLACE")

        if query.strip().startswith("CREATE TABLE"):
            # create a mapping of table_name and associated primary key
            cluster_key = False
            table_name = query.split()[2][:-1]
            self.mappings[table_name] = {}
            primary_key_present = query.rfind('PRIMARY KEY')
            if primary_key_present == -1:
                raise Exception('Primary key not present for {0}'.format(table_name))
            primary_key_builder = query.rsplit('PRIMARY KEY')[1].strip()[1:][:-4]
            if ('('  in primary_key_builder) and (')' in primary_key_builder):
                cluster_key = True

            primary_key_builder = primary_key_builder.replace('(','')
            primary_key_builder = primary_key_builder.replace(')','')
            primary_key_builder = primary_key_builder.replace(',','')

            all_keys = primary_key_builder.split()
            if cluster_key:
                self.mappings[table_name]['primary'] = all_keys[:-1]
                self.mappings[table_name]['clustering'] = all_keys[-1:]
            else:
                self.mappings[table_name]['primary'] = all_keys

            self.mappings[table_name]['index'] = None


        if query.strip().startswith("CREATE INDEX"):
            # create a mapping of table_name and associated index key
            index_builder = query.strip().split('ON')[1].strip()[:-1]
            index_builder = index_builder.replace('(','')
            index_builder = index_builder.replace(')','')
            table_name , index_key = index_builder.split()

            self.mappings[table_name]['index'] = index_key

        if query.strip().startswith("SELECT"):

            # when querying with a where clause, the primary key must be supplied
            prim_count = 0
            prim_keys_present = []
            index_count = 0
            index_keys_present = False
            where_clause_present = query.rfind('WHERE')
            if where_clause_present == -1:
                pass
            else:
                table_name = query.rsplit('FROM')[1].rsplit("WHERE")[0].strip()

                query_builder =  query.strip().rsplit("WHERE")[1].split()

                for token in self.tokens:
                    try:
                        query_builder.remove(token)
                    except ValueError:
                        pass

                for key in query_builder:
                    for prim_key in self.mappings[table_name]['primary']:
                        if key.startswith(prim_key):
                            prim_keys_present.append(prim_key)
                            prim_count+=1

                if self.mappings[table_name]['index']:
                    for key in query_builder:
                        for index_key in self.mappings[table_name]['index']:
                            if key.startswith(index_key):
                                index_keys_present = True
                                index_count+=1

                if not index_keys_present:
                    missed_prim_keys = set(self.mappings[table_name]['primary']) - set(prim_keys_present)
                    if missed_prim_keys != set():
                        raise Exception('Primary key(s): {0} are missing from where clause'.format(missed_prim_keys))
                    else:
                        if len(query_builder) > prim_count:
                            raise Exception('Non primary key present in where clause')
                else:
                    if prim_count == 0:
                        pass
                    else:
                        raise Exception('Query will require explicit filtering')


        res = self.conn.execute(query, queryargs)
        res = list(res)

        return res


    def execute_async(self, query, queryargs):

        res = self.execute(query, queryargs)

        return Future(res)

class Cluster(object):

    def __init__(self, contact_points, auth_provider, ssl_options):
        self.cluster_contact_points = contact_points

    @property
    def contact_points(self):
        return self.cluster_contact_points

    def connect(self, keyspace):
        self._sqliteconn = sqlite3.connect(':memory:')
        return Session(self._sqliteconn, keyspace)