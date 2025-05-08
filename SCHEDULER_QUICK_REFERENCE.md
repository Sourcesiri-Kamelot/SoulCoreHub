# Anima Scheduler Quick Reference Guide

## Installation

```bash
# Install the scheduler system
./install_scheduler.sh

# Start the scheduler server
./start_scheduler.sh
```

## Web Dashboard

Access the Scheduled Skills dashboard at:
```
http://localhost:5000/scheduled-skills
```

## Natural Language Commands

### Schedule a skill at intervals:
```
Schedule the system_info skill every 30 minutes
Schedule backup_data to run every 2 hours
Run log_cleaner every day
Execute database_backup every week
```

### Schedule a skill at specific times:
```
Schedule system_report to run at 9 AM
Run daily_summary every day at 5 PM
Schedule weekly_report every Monday at noon
Execute monthly_backup on the 1st of every month at midnight
```

### Schedule a one-time execution:
```
Schedule send_report to run once tomorrow at 3 PM
Run data_export one time on Friday
Execute notification_sender once on May 10th
```

### Unschedule a skill:
```
Unschedule system_info
Stop running backup_data
Remove the schedule for log_cleaner
Cancel the weekly_report schedule
```

## API Endpoints

### Schedule a skill
```bash
curl -X POST http://localhost:5000/api/schedule_skill \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "system_info",
    "schedule": {
      "type": "interval",
      "hours": 1
    }
  }'
```

### Unschedule a skill
```bash
curl -X POST http://localhost:5000/api/unschedule_skill \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "system_info_1234567890"
  }'
```

### List scheduled skills
```bash
curl http://localhost:5000/api/scheduled_skills
```

### Process a natural language scheduling request
```bash
curl -X POST http://localhost:5000/api/process_schedule_request \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Schedule system_info to run every hour"
  }'
```

### Execute a skill immediately
```bash
curl -X POST http://localhost:5000/api/execute_skill \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "system_info",
    "args": {}
  }'
```

## Schedule Types

### Interval Schedule
```json
{
  "type": "interval",
  "seconds": 30
}
```
Options: `seconds`, `minutes`, `hours`, `days`, `weeks`

### Cron Schedule
```json
{
  "type": "cron",
  "hour": "9",
  "minute": "0",
  "day_of_week": "0-4"
}
```
Options: `year`, `month`, `day`, `week`, `day_of_week`, `hour`, `minute`, `second`

### One-time Schedule
```json
{
  "type": "date",
  "run_date": "2025-05-10T15:00:00"
}
```
Required: `run_date` (ISO format)

## Dashboard Features

1. **View Scheduled Skills**
   - List of all scheduled skills
   - Schedule details and descriptions
   - Creation timestamps

2. **Add New Schedule**
   - Select skill from dropdown
   - Choose schedule type
   - Configure schedule parameters
   - Add optional arguments

3. **Manage Existing Schedules**
   - Run skills on demand
   - Delete schedules
   - View execution history

## Troubleshooting

### Check scheduler logs
```bash
cat logs/scheduler.log
```

### Check skill execution logs
```bash
cat logs/skill_executions.log
```

### Restart the scheduler
```bash
./start_scheduler.sh
```

### Reset scheduler (removes all schedules)
```bash
rm -f skills/skills.json.bak
cp skills/skills.json skills/skills.json.bak
python -c "import json; f=open('skills/skills.json','r'); data=json.load(f); f.close(); [data[k].pop('schedule', None) for k in data]; f=open('skills/skills.json','w'); json.dump(data, f, indent=2); f.close()"
```
