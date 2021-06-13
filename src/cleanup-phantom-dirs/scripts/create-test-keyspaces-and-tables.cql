// borrowing sample code from https://docs.datastax.com/en/dse/6.8/cql/cql/cyclist_stats-table.html

// create one keyspace that will be kept as a control, and one that will be a keyspace that is kept, but with some tables removed
CREATE KEYSPACE control_ks WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};

CREATE TABLE control_ks.cyclist_stats ( id UUID PRIMARY KEY, lastname text, birthday timestamp, nationality text, weight text, height text );
// insert one row
insert INTO control_ks.cyclist_stats (id)   VALUES(6ab09bec-e68e-48d9-a5f8-97e6fb4c9b47);

CREATE TABLE control_ks.alt_cyclist_stats ( id UUID PRIMARY KEY, lastname text, birthday timestamp, nationality text, weight text, height text );
// insert one row
insert INTO control_ks.alt_cyclist_stats (id)   VALUES(6ab09bec-e68e-48d9-a5f8-97e6fb4c9b47);

CREATE KEYSPACE phantom_ks WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};
CREATE TABLE phantom_ks.cyclist_stats ( id UUID PRIMARY KEY, lastname text, birthday timestamp, nationality text, weight text, height text );
// insert one row
insert INTO phantom_ks.cyclist_stats (id)   VALUES(6ab09bec-e68e-48d9-a5f8-97e6fb4c9b47);

CREATE TABLE phantom_ks.alt_cyclist_stats ( id UUID PRIMARY KEY, lastname text, birthday timestamp, nationality text, weight text, height text );
// insert one row
insert INTO phantom_ks.alt_cyclist_stats (id)   VALUES(6ab09bec-e68e-48d9-a5f8-97e6fb4c9b47);

CREATE KEYSPACE ks_with_phantoms WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};
CREATE TABLE ks_with_phantoms.cyclist_stats ( id UUID PRIMARY KEY, lastname text, birthday timestamp, nationality text, weight text, height text );
// insert one row
insert INTO ks_with_phantoms.cyclist_stats (id)   VALUES(6ab09bec-e68e-48d9-a5f8-97e6fb4c9b47);

// create one table to be deleted, which becomes a phantom, but then replaced by new table with same name
CREATE TABLE ks_with_phantoms.replaced_phantom_cyclist_stats ( id UUID PRIMARY KEY, lastname text, birthday timestamp, nationality text, weight text, height text );
// insert one row
insert INTO ks_with_phantoms.replaced_phantom_cyclist_stats (id)   VALUES(6ab09bec-e68e-48d9-a5f8-97e6fb4c9b47);
