#!/usr/bin/env python3
"""
Auto Backup Service - Backup data to cloud
"""
from datetime import datetime
import json

class BackupService:
    def __init__(self):
        self.backups = []
        
    def create_backup(self, source, destination):
        backup = {{
            'source': source,
            'destination': destination,
            'status': 'ready',
            'ts': datetime.now().isoformat()
        }}
        self.backups.append(backup)
        return backup
    
    def restore(self, backup_id):
        return {{'status': 'ready', 'method': 'cloud_restore'}}

if __name__ == "__main__":
    b = BackupService()
    print(json.dumps(b.create_backup('/data', 's3://backups'), indent=2))
