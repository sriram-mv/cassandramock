cassandramock
=============

A Mock Implementation of Cassandra's Python Driver

Installation
------------

To Install Cassandra mock

```bash
pip install -e .
```

Example
-------

The Examples below show following cases

```bash
 * Everything is Upserts
 * where clause with primary key not present
 * where clause with an index key
 * where clause with an index key and a primary key
```


```python

In [1]: from cassandramock import cluster

In [2]: mock_cluster = cluster.Cluster(contact_points=['127.0.0.1'],
   ...:                                        auth_provider=None,
   ...:                                        ssl_options=False)

In [3]: mock_session = mock_cluster.connect('mykeyspace')

In [4]: query = '''CREATE TABLE vaults(
    ...:   projectid TEXT,
    ...:   vaultid TEXT,
    ...:   mycoolnumber TEXT,
    ...:   PRIMARY KEY(projectid)
    ...: );'''

In [5]: mock_session.execute(query, '')
Out[5]: []

In [6]: mock_session.mappings
Out[6]: {'VAULTS': {'primary': ['PROJECTID'], 'index': None}}

 In [7]: CQL_CREATE_VAULT = '''
    ...:     INSERT INTO vaults (projectid, vaultid, mycoolnumber)
    ...:     VALUES (%(projectid)s, %(vaultid)s, %(mycoolnumber)s)
    ...: '''

In [8]: query_args = {'PROJECTID':'56', 'VAULTID':'67', 'MYCOOLNUMBER': '8'}

In [9]: mock_session.execute(CQL_CREATE_VAULT, query_args)
Out[9]: []

In [10]: mock_session.execute('SELECT * FROM VAULTS', '')
Out[10]: [('56', '67', '8')]

In [11]: query_args = {'PROJECTID':'56', 'VAULTID':'67', 'MYCOOLNUMBER': '9'}

In [12]: mock_session.execute(CQL_CREATE_VAULT, query_args)
Out[12]: []

In [13]: mock_session.execute('SELECT * FROM VAULTS', '')
Out[13]: [('56', '67', '9')]

In [14]: mock_session.execute('SELECT PROJECTID FROM VAULTS', '')
Out[14]: [('56',)]

In [15]: mock_session.execute('SELECT PROJECTID FROM VAULTS WHERE VAULTID>=3', '')
---------------------------------------------------------------------------
InvalidRequest                            Traceback (most recent call last)
<ipython-input-15-ae3ff7653c0a> in <module>()
----> 1 mock_session.execute('SELECT PROJECTID FROM VAULTS WHERE VAULTID>=3', '')

/Users/srir6369/cassandramock/cassandramock/cluster.py in execute(self, query, queryargs)
    140                     missed_prim_keys = set(self.mappings[table_name]['primary']) - set(prim_keys_present)
    141                     if missed_prim_keys != set():
--> 142                         raise InvalidRequest('Primary key(s): {0} are missing from where clause'.format(missed_prim_keys))
    143                     else:
    144                         if len(query_builder) > prim_count:

InvalidRequest: Primary key(s): {'PROJECTID'} are missing from where clause

In [16]: mock_session.execute('SELECT VAULTID FROM VAULTS WHERE PROJECTID>=3', '')
Out[16]: [('67',)]

In [17]: mock_session.execute('CREATE INDEX VAULTID_INDEX ON VAULTS (VAULTID)','')
Out[17]: []

In [18]: mock_session.execute('SELECT PROJECTID FROM VAULTS WHERE VAULTID>=3', '')
Out[18]: [('56',)]

In [19]: mock_session.execute('SELECT VAULTID FROM VAULTS WHERE PROJECTID>=3 AND MYCOOLNUMBER>=1', '')
---------------------------------------------------------------------------
InvalidRequest                            Traceback (most recent call last)
<ipython-input-19-fb2ba0d8dea9> in <module>()
----> 1 mock_session.execute('SELECT VAULTID FROM VAULTS WHERE PROJECTID>=3 AND MYCOOLNUMBER>=1', '')

/Users/srir6369/cassandramock/cassandramock/cluster.py in execute(self, query, queryargs)
    143                     else:
    144                         if len(query_builder) > prim_count:
--> 145                             raise InvalidRequest('Non primary key present in where clause')
    146                 else:
    147                     if prim_count == 0:

InvalidRequest: Non primary key present in where clause

In [20]: mock_session.execute('SELECT MYCOOLNUMBER FROM VAULTS WHERE PROJECTID>=3 AND VAULTID>=1', '')
---------------------------------------------------------------------------
InvalidRequest                            Traceback (most recent call last)
<ipython-input-20-0985407572c2> in <module>()
----> 1 mock_session.execute('SELECT MYCOOLNUMBER FROM VAULTS WHERE PROJECTID>=3 AND VAULTID>=1', '')

/Users/srir6369/cassandramock/cassandramock/cluster.py in execute(self, query, queryargs)
    148                         pass
    149                     else:
--> 150                         raise InvalidRequest('Query will require explicit filtering')
    151
    152

InvalidRequest: Query will require explicit filtering

```
