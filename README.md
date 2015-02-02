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

```python

In [1]: from cassandramock import cluster

In [2]: mock_cluster = cluster.Cluster(contact_points=['127.0.0.1'], 
                                       auth_provider=None,
                                       ssl_options=False)

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
Out[6]: {'VAULTS': {'index': None, 'primary': ['PROJECTID']}}

In [7]: CQL_CREATE_VAULT = '''
   ...:     INSERT INTO vaults (projectid, vaultid, mycoolnumber)
   ...:     VALUES (%(projectid)s, %(vaultid)s, %(mycoolnumber)s)
   ...: '''
   
In [8]: query_args = {'PROJECTID':'56', 'VAULTID':'67', 'MYCOOLNUMBER': '8'}

In [9]: mock_session.execute(CQL_CREATE_VAULT, query_args)
Out[9]: []

In [10]: mock_session.execute('SELECT * FROM VAULTS', '')
Out[10]: [('56', '67', '8')]

In [11]: mock_session.execute('SELECT PROJECTID FROM VAULTS', '')
Out[11]: [('56',)]

In [12]: mock_session.execute('SELECT PROJECTID FROM VAULTS WHERE VAULTID>=3', '')
---------------------------------------------------------------------------
Exception                                 Traceback (most recent call last)
<ipython-input-14-ae3ff7653c0a> in <module>()
----> 1 mock_session.execute('SELECT PROJECTID FROM VAULTS WHERE VAULTID>=3', '')

/Users/srir6369/cassandramock/cassandramock/cluster.py in execute(self, query, queryargs)
    137                     missed_prim_keys = set(self.mappings[table_name]['primary']) - set(prim_keys_present)
    138                     if missed_prim_keys != set():
--> 139                         raise Exception('Primary key(s): {0} are missing from where clause'.format(missed_prim_keys))
    140                     else:
    141                         if len(query_builder) > prim_count:

Exception: Primary key(s): {'PROJECTID'} are missing from where clause

In [13]: mock_session.execute('SELECT VAULTID FROM VAULTS WHERE PROJECTID>=3', '')
Out[13]: [('67',)]

In [14]: mock_session.execute('CREATE INDEX VAULTID_INDEX ON VAULTS (VAULTID)','')
Out[14]: []

In [15]: mock_session.execute('SELECT PROJECTID FROM VAULTS WHERE VAULTID>=3', '')
Out[15]: [('56',)]

```
