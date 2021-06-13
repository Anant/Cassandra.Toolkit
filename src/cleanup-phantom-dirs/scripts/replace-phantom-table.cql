// replace with new table of same name. Changing primary key, because why not, and it replicates the common use case
CREATE TABLE ks_with_phantoms.replaced_phantom_cyclist_stats ( id UUID, lastname text, birthday timestamp, nationality text, weight text, height text, PRIMARY KEY (id, lastname));
// insert one row
insert INTO ks_with_phantoms.replaced_phantom_cyclist_stats (id, lastname) VALUES(6ab09bec-e68e-48d9-a5f8-97e6fb4c9b47, 'fake-last-name');
