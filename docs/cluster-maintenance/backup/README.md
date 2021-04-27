# Backups

## Instructions for Specific Backup Tools
- [cassandra-medusa](./maintenance.medusa.md)
- [tablesnap](./maintenance.tablesnap.md)

## Snapshot strategy (future changes)

1. Take / keep a snapshot every 30 min for the latest 3 hours;
2. Keep a snapshot every 6 hours for the last day, delete other snapshots;
3. Keep a snapshot every day for the last month, delete other snapshots;