"""
Updates to the SoulCoreHub server to support skill scheduling.

This script adds the necessary API endpoints to the SoulCoreHub server
for managing scheduled skills.
"""

import os
import json
from typing import Dict, Any

def update_server_file():
    """Update the soulcorehub_server.py file with scheduling endpoints."""
    server_path = "soulcorehub_server.py"
    
    # Read the current content
    with open(server_path, 'r') as f:
        content = f.read()
    
    # Check if scheduling endpoints are already added
    if 'schedule_skill' in content:
        print("Scheduling endpoints already exist in the server file.")
        return
    
    # Import statements to add
    imports_to_add = """
from scheduler import AnimaScheduler
from anima_skill_scheduler import AnimaSkillScheduler
"""
    
    # Find the import section
    import_end = content.find("\n\n", content.find("import"))
    if import_end == -1:
        print("Could not find the import section. Manual update required.")
        return
    
    # Add imports
    updated_content = content[:import_end] + imports_to_add + content[import_end:]
    
    # Initialize scheduler in the server class
    init_code = """
        # Initialize the skill scheduler
        self.skill_scheduler = AnimaSkillScheduler(self.skill_engine, self.conversation_state)
"""
    
    # Find the __init__ method
    init_end = updated_content.find("def __init__", 0)
    if init_end == -1:
        print("Could not find the __init__ method. Manual update required.")
        return
    
    # Find the end of the __init__ method
    init_body_start = updated_content.find(":", init_end)
    init_body_end = find_method_end(updated_content, init_body_start + 1)
    
    # Add scheduler initialization
    updated_content = (
        updated_content[:init_body_end] + 
        init_code + 
        updated_content[init_body_end:]
    )
    
    # API endpoints to add
    endpoints_code = """
    def schedule_skill(self):
        '''Schedule a skill for execution.'''
        data = request.get_json()
        skill_name = data.get('skill_name')
        schedule = data.get('schedule')
        args = data.get('args', {})
        
        if not skill_name or not schedule:
            return jsonify({
                'success': False,
                'message': 'Skill name and schedule are required'
            })
        
        try:
            # Add args to the schedule config if provided
            if args:
                schedule['args'] = args
                
            job_id = self.skill_scheduler.scheduler.schedule_skill(skill_name, schedule)
            
            return jsonify({
                'success': True,
                'message': f'Skill {skill_name} scheduled successfully',
                'job_id': job_id
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            })
    
    def unschedule_skill(self):
        '''Unschedule a skill.'''
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({
                'success': False,
                'message': 'Job ID is required'
            })
        
        result = self.skill_scheduler.unschedule_skill(job_id)
        return jsonify(result)
    
    def get_scheduled_skills(self):
        '''Get all scheduled skills.'''
        scheduled_skills = self.skill_scheduler.list_scheduled_skills()
        return jsonify(scheduled_skills)
    
    def process_schedule_request(self):
        '''Process a natural language scheduling request.'''
        data = request.get_json()
        request_text = data.get('request')
        
        if not request_text:
            return jsonify({
                'success': False,
                'message': 'Request text is required'
            })
        
        result = self.skill_scheduler.process_scheduling_request(request_text)
        return jsonify(result)
"""
    
    # Find a good place to add the endpoints
    last_method_end = updated_content.rfind("def ")
    last_method_end = find_method_end(updated_content, last_method_end)
    
    # Add endpoints
    updated_content = (
        updated_content[:last_method_end] + 
        endpoints_code + 
        updated_content[last_method_end:]
    )
    
    # Routes to add
    routes_code = """
    # Scheduling routes
    app.route('/api/schedule_skill', methods=['POST'])(server.schedule_skill)
    app.route('/api/unschedule_skill', methods=['POST'])(server.unschedule_skill)
    app.route('/api/scheduled_skills', methods=['GET'])(server.get_scheduled_skills)
    app.route('/api/process_schedule_request', methods=['POST'])(server.process_schedule_request)
"""
    
    # Find the routes section
    routes_start = updated_content.find("if __name__ == '__main__':")
    if routes_start == -1:
        print("Could not find the routes section. Manual update required.")
        return
    
    # Find a good place to add the routes
    server_start = updated_content.find("server = ", routes_start)
    routes_end = updated_content.find("\n\n", server_start)
    if routes_end == -1:
        routes_end = len(updated_content)
    
    # Add routes
    updated_content = (
        updated_content[:routes_end] + 
        routes_code + 
        updated_content[routes_end:]
    )
    
    # Write the updated content
    with open(server_path, 'w') as f:
        f.write(updated_content)
    
    print("Successfully updated soulcorehub_server.py with scheduling endpoints.")

def find_method_end(content, start_pos):
    """Find the end of a method definition."""
    # Find the indentation level of the method
    method_line_end = content.find("\n", start_pos)
    next_line_start = method_line_end + 1
    
    # Find the indentation of the method body
    method_indent = 0
    while next_line_start < len(content) and content[next_line_start].isspace():
        method_indent += 1
        next_line_start += 1
    
    # Find where the indentation level decreases
    pos = next_line_start
    while pos < len(content):
        line_start = pos
        line_end = content.find("\n", line_start)
        if line_end == -1:
            line_end = len(content)
        
        # Skip empty lines
        if line_start == line_end or content[line_start:line_end].strip() == "":
            pos = line_end + 1
            continue
        
        # Count indentation
        indent = 0
        while indent < line_end - line_start and content[line_start + indent].isspace():
            indent += 1
        
        # If indentation is less than or equal to the method's indentation, we've found the end
        if indent <= method_indent:
            return line_start
        
        pos = line_end + 1
    
    return len(content)

def update_server_html():
    """Update the server.js file to serve the scheduled_skills.html page."""
    server_js_path = "server.js"
    
    # Read the current content
    with open(server_js_path, 'r') as f:
        content = f.read()
    
    # Check if the scheduled skills route is already added
    if 'scheduled-skills' in content:
        print("Scheduled skills route already exists in server.js.")
        return
    
    # Find the routes section
    routes_start = content.find("app.get('/'")
    if routes_start == -1:
        print("Could not find the routes section in server.js. Manual update required.")
        return
    
    # Route to add
    route_code = """
app.get('/scheduled-skills', (req, res) => {
    res.sendFile(path.join(__dirname, 'webui', 'scheduled_skills.html'));
});
"""
    
    # Find a good place to add the route
    next_route = content.find("app.get('", routes_start + 10)
    if next_route == -1:
        next_route = content.find("app.listen", routes_start)
    
    # Add the route
    updated_content = (
        content[:next_route] + 
        route_code + 
        content[next_route:]
    )
    
    # Write the updated content
    with open(server_js_path, 'w') as f:
        f.write(updated_content)
    
    print("Successfully updated server.js with scheduled skills route.")

def update_dashboard_html():
    """Update the dashboard HTML to include a link to the scheduled skills page."""
    dashboard_path = "webui/soulcore_dashboard.html"
    
    # Read the current content
    with open(dashboard_path, 'r') as f:
        content = f.read()
    
    # Check if the scheduled skills link is already added
    if 'Scheduled Skills' in content:
        print("Scheduled skills link already exists in the dashboard.")
        return
    
    # Find the navigation section
    nav_start = content.find("<nav")
    if nav_start == -1:
        print("Could not find the navigation section in the dashboard. Manual update required.")
        return
    
    nav_end = content.find("</nav>", nav_start)
    if nav_end == -1:
        print("Could not find the end of the navigation section. Manual update required.")
        return
    
    # Link to add
    link_code = """
                <a href="/scheduled-skills" class="nav-link">
                    <i class="fas fa-clock"></i>
                    <span>Scheduled Skills</span>
                </a>
"""
    
    # Find a good place to add the link
    last_link = content.rfind("</a>", nav_start, nav_end)
    if last_link == -1:
        print("Could not find a good place to add the link. Manual update required.")
        return
    
    # Find the end of the list item containing the last link
    li_end = content.find("</li>", last_link)
    if li_end == -1:
        li_end = last_link + 4
    
    # Add the link
    updated_content = (
        content[:li_end + 5] + 
        "            <li>" + 
        link_code + 
        "            </li>" + 
        content[li_end + 5:]
    )
    
    # Write the updated content
    with open(dashboard_path, 'w') as f:
        f.write(updated_content)
    
    print("Successfully updated the dashboard with a link to scheduled skills.")

if __name__ == "__main__":
    update_server_file()
    update_server_html()
    update_dashboard_html()
    print("Server updates completed successfully.")
