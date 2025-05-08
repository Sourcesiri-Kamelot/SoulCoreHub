# Anima Skill Scheduler

The Anima Skill Scheduler allows Anima to schedule skills for future and recurring execution, giving her more autonomy and the ability to plan tasks without constant human intervention.

## Features

- **Schedule skills** to run at specific times or intervals
- **Natural language interface** for scheduling requests
- **Web dashboard** for managing scheduled skills
- **Persistent scheduling** across system restarts
- **Multiple schedule types**:
  - Interval-based (every X minutes/hours/days)
  - Cron-based (specific times/days)
  - One-time execution (specific date and time)

## Installation

1. Run the installation script:
   ```bash
   ./install_scheduler.sh
   ```

2. This will:
   - Install required dependencies
   - Configure the server with scheduling capabilities
   - Create necessary startup scripts
   - Set appropriate file permissions

## Usage

### Starting the Scheduler

Start the SoulCoreHub server with scheduling capabilities:

```bash
./start_scheduler.sh
```

This will start the server and open the Scheduled Skills dashboard in your browser.

### Scheduling Skills via Anima

You can ask Anima to schedule skills using natural language:

```
Schedule the system_info skill to run every hour
```

```
Run the backup_data skill daily at 3 PM
```

```
Execute the send_report skill every Monday at noon
```

### Using the Dashboard

The Scheduled Skills dashboard allows you to:

1. View all scheduled skills
2. Add new scheduled skills
3. Run scheduled skills on demand
4. Delete scheduled jobs

Access the dashboard at: http://localhost:5000/scheduled-skills

### API Endpoints

The following API endpoints are available for programmatic access:

- `POST /api/schedule_skill`: Schedule a skill
- `POST /api/unschedule_skill`: Remove a scheduled skill
- `GET /api/scheduled_skills`: List all scheduled skills
- `POST /api/process_schedule_request`: Process natural language scheduling requests
- `GET /api/skills`: Get all available skills
- `POST /api/execute_skill`: Execute a skill immediately

## Components

The scheduling system consists of the following components:

1. **scheduler.py**: Core scheduling engine using APScheduler
2. **anima_skill_scheduler.py**: Natural language interface for Anima
3. **soulcorehub_server_scheduler.py**: Server with scheduling endpoints
4. **webui/scheduled_skills.html**: Web dashboard for managing scheduled skills

## Future Enhancements

- **Skill chaining**: Run multiple skills in sequence
- **Conditional execution**: Run skills based on conditions
- **Self-repair**: Skills that can debug and fix other skills
- **Autonomous scheduling**: Let Anima decide when to run skills based on context

## Troubleshooting

If you encounter issues:

1. Check the log files in the `logs` directory
2. Ensure APScheduler is installed: `pip install apscheduler`
3. Verify file permissions: `./maintain_permissions.sh`
4. Restart the server: `./start_scheduler.sh`

## License

This project is proprietary and confidential. All rights reserved.
