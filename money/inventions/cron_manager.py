#!/usr/bin/env python3
"""
Cron Job Service - Automated cron management for customers
"""
from datetime import datetime
import json

class CronService:
    def __init__(self):
        self.jobs = []
        
    def create_job(self, name, schedule, command):
        job = {
            'name': name,
            'schedule': schedule,
            'command': command,
            'ts': datetime.now().isoformat()
        }
        self.jobs.append(job)
        return {'status': 'created', 'job': job}
    
    def list_jobs(self):
        return self.jobs

if __name__ == "__main__":
    c = CronService()
    print(json.dumps(c.create_job('backup', '0 2 * * *', 'backup.sh'), indent=2))
