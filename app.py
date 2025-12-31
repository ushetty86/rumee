"""
Rumee - AI-Powered Personal Assistant
Streamlit UI for notes, meetings, people, reminders, and AI-powered insights
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional
from collections import defaultdict

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

# Session state initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


# API Client Functions
def api_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API request with authentication"""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        st.error(f"Connection error: {e}")
        return {}


def login(email: str, password: str) -> bool:
    """Login user"""
    response = api_request("POST", "/auth/login", {"email": email, "password": password})
    if response and "access_token" in response:
        st.session_state.token = response["access_token"]
        st.session_state.user = response["user"]
        return True
    return False


def register(email: str, password: str, name: str) -> bool:
    """Register new user"""
    response = api_request("POST", "/auth/register", {
        "email": email,
        "password": password,
        "name": name
    })
    if response and "access_token" in response:
        st.session_state.token = response["access_token"]
        st.session_state.user = response["user"]
        return True
    return False


def logout():
    """Logout user"""
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()


# Authentication Page
def auth_page():
    """Login/Register page"""
    st.title("🧠 Cognitive Co-pilot")
    st.caption("Your AI-powered second brain")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if login(email, password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        st.subheader("Register")
        name = st.text_input("Name", key="register_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        
        if st.button("Register"):
            if register(email, password, name):
                st.success("Registered successfully!")
                st.rerun()
            else:
                st.error("Registration failed")


# Dashboard Page - ACT FOCUSED
def dashboard_page():
    """ACT-focused dashboard - What needs your attention NOW"""
    st.title(f"🎯 Focus Mode")
    st.caption("What needs your attention right now")
    
    # Get data
    notes = api_request("GET", "/notes")
    reminders = api_request("GET", "/reminders", params={"status": "pending"})
    meetings = api_request("GET", "/meetings")
    people = api_request("GET", "/people")
    
    # SECTION 1: Immediate Actions (High Priority/Urgency)
    st.subheader("🔴 Needs Immediate Attention")
    urgent_items = []
    
    if reminders:
        high_priority = [r for r in reminders if r.get('priority') == 'high']
        if high_priority:
            for reminder in high_priority[:3]:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"🔥 **{reminder['title']}**")
                    if reminder.get('due_date'):
                        st.caption(f"Due: {reminder['due_date'][:10]}")
                with col2:
                    if st.button("✓ Done", key=f"urgent_{reminder['id']}"):
                        api_request("PUT", f"/reminders/{reminder['id']}", {"status": "completed"})
                        st.rerun()
    
    if not urgent_items:
        st.success("✨ No urgent items! You're on top of things.")
    
    st.divider()
    
    # SECTION 2: Comprehensive AI Brain Insights
    st.subheader("🧠 Your AI Brain is Working")
    
    # Get brain status
    brain_status = api_request("GET", "/ai/brain-status")
    if brain_status and brain_status.get('status') == 'active':
        memory = brain_status.get('memory', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔗 Connections", memory.get('connections_found', 0))
        with col2:
            st.metric("💡 Insights", memory.get('insights_queued', 0))
        with col3:
            st.metric("📊 Patterns", memory.get('patterns_detected', 0))
        with col4:
            st.metric("🎯 Active Topics", memory.get('active_topics', 0))
    
    # Current Context
    context_response = api_request("GET", "/ai/context")
    if context_response:
        context = context_response.get('context', {})
        if context.get('primary_focus'):
            st.info(f"🎯 **Current Focus:** {context['primary_focus']}")
            
            if context.get('active_people'):
                st.caption(f"👥 Working with: {', '.join(context['active_people'][:3])}")
    
    # Proactive Insights
    with st.expander("💡 Proactive Insights from AI Agents", expanded=True):
        insights_response = api_request("GET", "/ai/insights")
        
        if insights_response:
            insights = insights_response.get('insights', [])
            
            if insights:
                for insight in insights[:5]:  # Show top 5
                    priority = insight.get('priority', 'low')
                    emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
                    
                    with st.container():
                        st.write(f"{emoji} **{insight.get('title', 'Insight')}**")
                        st.caption(insight.get('description', ''))
                        st.caption(f"_{insight.get('type', 'general')}_")
                        st.divider()
            else:
                st.write("🤖 AI agents are learning your patterns. Keep capturing notes!")
    
    # Detected Patterns
    with st.expander("📈 Detected Patterns & Trends"):
        patterns_response = api_request("GET", "/ai/patterns")
        
        if patterns_response:
            patterns = patterns_response.get('patterns', {})
            
            time_patterns = patterns.get('time_patterns', {})
            if time_patterns.get('peak_hours'):
                st.write("**⏰ You're most productive at:**")
                for hour, count in time_patterns['peak_hours'][:3]:
                    st.write(f"• {hour}:00 ({count} activities)")
            
            topic_evolution = patterns.get('topic_evolution', {})
            if topic_evolution:
                st.write("\n**📊 Topic Evolution (last 4 weeks):**")
                weeks_labels = ['This week', 'Last week', '2 weeks ago', '3 weeks ago']
                for week_num, topics in sorted(topic_evolution.items()):
                    if int(week_num) < 4:
                        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
                        if top_topics:
                            st.write(f"• **{weeks_labels[int(week_num)]}:** {', '.join([t[0] for t in top_topics])}")
            
            collab_patterns = patterns.get('collaboration_patterns', [])
            if collab_patterns:
                st.write("\n**👥 Frequent Collaborators:**")
                for person, count in collab_patterns[:5]:
                    st.write(f"• {person} ({count} mentions)")
    
    st.divider()
    
    # SECTION 3: Today's Context
    st.subheader("📅 Today's Context")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Tasks", len(reminders) if reminders else 0)
    with col2:
        today_meetings = [m for m in meetings if m.get('scheduled_at', '').startswith(datetime.now().strftime('%Y-%m-%d'))] if meetings else []
        st.metric("Today's Meetings", len(today_meetings))
    with col3:
        recent_notes = [n for n in notes if n.get('created_at', '').startswith(datetime.now().strftime('%Y-%m-%d'))] if notes else []
        st.metric("Notes Today", len(recent_notes))
    
    # Quick stats
    with st.expander("📊 Overall Stats"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Notes", len(notes) if notes else 0)
        with col2:
            st.metric("Your Network", len(people) if people else 0)
        with col3:
            st.metric("All Meetings", len(meetings) if meetings else 0)
        with col4:
            completed = api_request("GET", "/reminders", params={"status": "completed"})
            st.metric("Completed Tasks", len(completed) if completed else 0)


# Brain Dump Page - UNIFIED INBOX
def brain_dump_page():
    """Zero-Sort Brain Dump - capture everything in one place"""
    st.title("🧠 Brain Dump")
    st.caption("Dump everything here. AI will sort it out.")
    
    # Input method selection
    input_method = st.radio("", ["💬 Text", "🎤 Voice", "📷 Photo"], horizontal=True)
    
    if input_method == "💬 Text":
        st.subheader("Just write. Don't organize.")
        content = st.text_area(
            "",
            height=300,
            placeholder="Type or paste anything:\n• Meeting notes\n• Random ideas\n• Tasks\n• People you met\n• Anything on your mind...\n\nThe AI will:\n✓ Extract people, topics, tasks\n✓ Create reminders automatically\n✓ Link to related notes\n✓ Organize everything",
            label_visibility="collapsed"
        )
        
        title = st.text_input("Optional: Give it a title", placeholder="Leave blank for AI to generate")
        
        if st.button("🚀 Capture", type="primary", use_container_width=True):
            if content:
                with st.spinner("AI is processing..."):
                    response = api_request("POST", "/notes", {
                        "title": title if title else "Untitled",
                        "content": content,
                        "tags": []
                    })
                    if response:
                        st.success("✅ Captured! AI is analyzing in the background...")
                        
                        # Show what AI extracted
                        if response.get('entities'):
                            with st.expander("🤖 What AI found"):
                                entities = response['entities']
                                if entities.get('people'):
                                    st.write(f"**People:** {', '.join(entities['people'])}")
                                if entities.get('topics'):
                                    st.write(f"**Topics:** {', '.join(entities['topics'])}")
                                if entities.get('organizations'):
                                    st.write(f"**Organizations:** {', '.join(entities['organizations'])}")
                                if entities.get('tasks'):
                                    st.write(f"**Tasks extracted:** {len(entities.get('tasks', []))} tasks will be created")
                        
                        st.balloons()
                        
                        # Clear after success
                        st.rerun()
            else:
                st.warning("Write something first!")
    
    elif input_method == "🎤 Voice":
        st.subheader("Speak your mind")
        st.info("🎤 Voice capture coming soon! Use text for now.")
        st.write("""
        Voice capture will allow you to:
        - 🗣️ Speak naturally
        - 🎯 No need to organize
        - ⚡ Instant transcription
        - 🤖 AI processes automatically
        """)
        
        # Placeholder for voice capture
        st.text_area("Voice transcript will appear here", height=200, disabled=True)
    
    elif input_method == "📷 Photo":
        st.subheader("Capture visual information")
        uploaded_file = st.file_uploader("Upload image", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            st.info("📷 AI vision processing coming soon!")
            st.write("""
            Photo capture will:
            - 📸 Extract text (OCR)
            - 🧠 Understand context
            - 📝 Create notes automatically
            - 🔗 Link to related information
            """)
            
            if st.button("Process Image"):
                st.warning("Image processing not yet implemented. Use text input for now!")
    
    st.divider()
    
    # Recent captures
    st.subheader("📥 Recent Captures")
    notes = api_request("GET", "/notes")
    
    if notes:
        # Sort by date, most recent first
        sorted_notes = sorted(notes, key=lambda x: x.get('created_at', ''), reverse=True)
        
        for note in sorted_notes[:5]:  # Show last 5
            with st.expander(f"📄 {note['title']} - {note['created_at'][:10]}"):
                st.write(note['content'][:200] + "..." if len(note['content']) > 200 else note['content'])
                if note.get('entities'):
                    st.caption(f"🤖 AI found: {len(note['entities'].get('people', []))} people, {len(note['entities'].get('topics', []))} topics")
    else:
        st.info("No captures yet. Start dumping your thoughts above!")


# Notes Page
def notes_page():
    """Notes management page"""
    st.title("📝 Notes")
    
    # Create new note
    with st.expander("✨ Create New Note"):
        title = st.text_input("Title")
        content = st.text_area("Content", height=200)
        tags = st.text_input("Tags (comma-separated)")
        
        if st.button("Create Note"):
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            response = api_request("POST", "/notes", {
                "title": title,
                "content": content,
                "tags": tag_list
            })
            if response:
                st.success("Note created with AI linking!")
                st.rerun()
    
    # Search notes
    st.subheader("🔍 Search Notes")
    search_query = st.text_input("Semantic search (AI-powered)")
    if search_query and st.button("Search"):
        results = api_request("POST", "/notes/search", params={"query": search_query})
        if results:
            for result in results:
                with st.expander(f"📄 {result['title']} (similarity: {result['similarity']:.2f})"):
                    st.write(result['content'])
                    st.caption(f"Created: {result['created_at']}")
    
    # Display notes
    st.subheader("All Notes")
    notes = api_request("GET", "/notes")
    
    if notes:
        for note in notes:
            with st.expander(f"📄 {note['title']}"):
                st.write(note['content'])
                
                if note.get('tags'):
                    st.write("**Tags:**", ", ".join(note['tags']))
                
                if note.get('entities'):
                    st.write("**AI-Extracted Entities:**")
                    entities = note['entities']
                    if entities.get('people'):
                        st.write(f"People: {', '.join(entities['people'])}")
                    if entities.get('topics'):
                        st.write(f"Topics: {', '.join(entities['topics'])}")
                
                # Show AI-discovered connections
                connections_response = api_request("GET", f"/ai/connections/{note['id']}")
                if connections_response and connections_response.get('connections'):
                    connections = connections_response['connections']
                    if connections:
                        st.write("\n**🔗 AI-Discovered Connections:**")
                        for conn in connections[:3]:  # Show top 3
                            strength_emoji = '🔴' if conn['strength'] > 0.8 else '🟡' if conn['strength'] > 0.6 else '🟢'
                            st.write(f"{strength_emoji} **{conn['connection_type']}** → [{conn['target_title']}]")
                            st.caption(f"_{conn['reason']}_")
                
                st.caption(f"Created: {note['created_at']}")
                
                if st.button(f"Delete", key=f"delete_note_{note['id']}"):
                    api_request("DELETE", f"/notes/{note['id']}")
                    st.success("Note deleted!")
                    st.rerun()
    else:
        st.info("No notes yet. Create your first note above!")


# People Page
def people_page():
    """People/Contacts management"""
    st.title("👥 People")
    
    # Add new person
    with st.expander("➕ Add New Person"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        company = st.text_input("Company")
        role = st.text_input("Role")
        tags = st.text_input("Tags (comma-separated)")
        notes = st.text_area("Notes")
        
        if st.button("Add Person"):
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            response = api_request("POST", "/people", {
                "name": name,
                "email": email if email else None,
                "phone": phone if phone else None,
                "company": company if company else None,
                "role": role if role else None,
                "tags": tag_list,
                "notes": notes if notes else None
            })
            if response:
                st.success("Person added!")
                st.rerun()
    
    # Display people
    people = api_request("GET", "/people")
    
    if people:
        for person in people:
            with st.expander(f"👤 {person['name']}"):
                if person.get('email'):
                    st.write(f"📧 {person['email']}")
                if person.get('company'):
                    st.write(f"🏢 {person['company']}")
                if person.get('role'):
                    st.write(f"💼 {person['role']}")
                if person.get('tags'):
                    st.write("🏷️", ", ".join(person['tags']))
                
                if st.button(f"Delete", key=f"delete_person_{person['id']}"):
                    api_request("DELETE", f"/people/{person['id']}")
                    st.success("Person deleted!")
                    st.rerun()
    else:
        st.info("No contacts yet. Add your first contact above!")


# Meetings Page
def meetings_page():
    """Meetings management"""
    st.title("📅 Meetings")
    
    # Create new meeting
    with st.expander("➕ Schedule New Meeting"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        meeting_date = st.date_input("Date")
        meeting_time = st.time_input("Time")
        duration = st.number_input("Duration (minutes)", min_value=15, value=60)
        location = st.text_input("Location")
        
        if st.button("Create Meeting"):
            scheduled_at = datetime.combine(meeting_date, meeting_time)
            response = api_request("POST", "/meetings", {
                "title": title,
                "description": description,
                "scheduled_at": scheduled_at.isoformat(),
                "duration_minutes": duration,
                "location": location if location else None
            })
            if response:
                st.success("Meeting created!")
                st.rerun()
    
    # Display meetings
    meetings = api_request("GET", "/meetings")
    
    if meetings:
        for meeting in meetings:
            scheduled = datetime.fromisoformat(meeting['scheduled_at'].replace('Z', '+00:00'))
            with st.expander(f"📅 {meeting['title']} - {scheduled.strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"**Status:** {meeting['status']}")
                if meeting.get('duration_minutes'):
                    st.write(f"**Duration:** {meeting['duration_minutes']} minutes")
                
                st.caption(f"Created: {meeting['created_at']}")
                
                if st.button(f"Delete", key=f"delete_meeting_{meeting['id']}"):
                    api_request("DELETE", f"/meetings/{meeting['id']}")
                    st.success("Meeting deleted!")
                    st.rerun()
    else:
        st.info("No meetings scheduled. Create your first meeting above!")


# Reminders Page
def reminders_page():
    """Reminders/Tasks management"""
    st.title("⏰ Reminders")
    
    # Create new reminder
    with st.expander("➕ Create New Reminder"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        due_date = st.date_input("Due Date")
        due_time = st.time_input("Due Time")
        priority = st.selectbox("Priority", ["low", "medium", "high"])
        
        if st.button("Create Reminder"):
            due_datetime = datetime.combine(due_date, due_time)
            response = api_request("POST", "/reminders", {
                "title": title,
                "description": description,
                "due_date": due_datetime.isoformat(),
                "priority": priority
            })
            if response:
                st.success("Reminder created!")
                st.rerun()
    
    # Display reminders
    tab1, tab2 = st.tabs(["Pending", "Completed"])
    
    with tab1:
        reminders = api_request("GET", "/reminders", params={"status": "pending"})
        if reminders:
            for reminder in reminders:
                due = datetime.fromisoformat(reminder['due_date'].replace('Z', '+00:00'))
                priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{priority_emoji[reminder['priority']]} **{reminder['title']}**")
                    st.caption(f"Due: {due.strftime('%Y-%m-%d %H:%M')}")
                with col2:
                    if st.button("✓", key=f"complete_{reminder['id']}"):
                        api_request("PUT", f"/reminders/{reminder['id']}", {"status": "completed"})
                        st.rerun()
        else:
            st.info("No pending reminders!")
    
    with tab2:
        reminders = api_request("GET", "/reminders", params={"status": "completed"})
        if reminders:
            for reminder in reminders:
                st.write(f"✅ {reminder['title']}")
                st.caption(f"Completed: {reminder.get('completed_at', 'N/A')}")
        else:
            st.info("No completed reminders yet!")


# Knowledge Graph Page
def knowledge_graph_page():
    """Knowledge Graph - THE BRAIN - visualization and exploration"""
    st.title("🕸️ Knowledge Graph - The Brain")
    st.caption("Your entire world, connected")
    
    # Get graph stats
    stats_response = api_request("GET", "/graph/stats")
    
    if stats_response:
        stats = stats_response.get('stats', {})
        
        # Stats overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔵 Total Nodes", stats.get('total_nodes', 0))
        with col2:
            st.metric("🔗 Total Edges", stats.get('total_edges', 0))
        with col3:
            node_types = stats.get('node_types', {})
            st.metric("📊 Node Types", len(node_types))
        with col4:
            density = stats.get('density', 0)
            st.metric("🎯 Density", f"{density:.2%}")
        
        # Node type breakdown
        with st.expander("📊 Graph Composition", expanded=True):
            node_types = stats.get('node_types', {})
            if node_types:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Nodes by Type:**")
                    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"• {node_type}: {count}")
                
                with col2:
                    st.write("**Relationships by Type:**")
                    edge_types = stats.get('edge_types', {})
                    for edge_type, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                        st.write(f"• {edge_type}: {count}")
        
        # Central nodes (most connected)
        st.subheader("⭐ Most Connected Entities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**👥 Central People:**")
            people_response = api_request("GET", "/graph/central-nodes?node_type=person&limit=5")
            if people_response and people_response.get('central_nodes'):
                for node in people_response['central_nodes']:
                    st.write(f"🔵 **{node['label']}** - {node['connections']} connections")
            else:
                st.caption("No people yet")
        
        with col2:
            st.write("**🎯 Central Topics:**")
            topics_response = api_request("GET", "/graph/central-nodes?node_type=topic&limit=5")
            if topics_response and topics_response.get('central_nodes'):
                for node in topics_response['central_nodes']:
                    st.write(f"🔵 **{node['label']}** - {node['connections']} connections")
            else:
                st.caption("No topics yet")
        
        # Topic clusters
        st.subheader("🌐 Topic Clusters")
        clusters_response = api_request("GET", "/graph/clusters?node_type=topic")
        if clusters_response and clusters_response.get('clusters'):
            clusters = clusters_response['clusters']
            st.write(f"Found {len(clusters)} topic clusters")
            
            for cluster_id, nodes in list(clusters.items())[:3]:
                with st.expander(f"Cluster {cluster_id.split('_')[1]} ({len(nodes)} topics)"):
                    topic_names = [n['label'] for n in nodes]
                    st.write(", ".join(topic_names))
        
        # Path finder
        st.subheader("🔍 Connection Explorer")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            start_entity = st.text_input("From entity (e.g., person:John)", key="path_start")
        with col2:
            end_entity = st.text_input("To entity (e.g., topic:AI)", key="path_end")
        with col3:
            st.write("")
            st.write("")
            find_path = st.button("Find Path")
        
        if find_path and start_entity and end_entity:
            path_response = api_request("GET", f"/graph/path?start={start_entity}&end={end_entity}")
            if path_response and path_response.get('paths'):
                paths = path_response['paths']
                st.success(f"Found {len(paths)} path(s)!")
                
                for i, path in enumerate(paths[:3]):
                    st.write(f"**Path {i+1}:**")
                    path_str = " → ".join([f"{node['label']} ({node['type']})" for node in path])
                    st.write(path_str)
            else:
                st.info("No path found between these entities")
        
        # Graph visualization (simple text-based for now)
        st.subheader("🎨 Visualization")
        viz_response = api_request("GET", "/graph/visualize?limit=50")
        
        if viz_response and viz_response.get('graph'):
            graph_data = viz_response['graph']
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            
            st.write(f"Showing {len(nodes)} nodes and {len(edges)} edges")
            
            # Group by type
            with st.expander("View Graph Structure"):
                by_type = defaultdict(list)
                for node in nodes:
                    by_type[node['type']].append(node['label'])
                
                for node_type, labels in by_type.items():
                    st.write(f"**{node_type.capitalize()}s:** {', '.join(labels[:10])}")
                    if len(labels) > 10:
                        st.caption(f"...and {len(labels) - 10} more")
        
        # Entity timeline
        st.subheader("📅 Entity Timeline")
        entity_id = st.text_input("Enter entity ID (e.g., person:Sarah)", key="timeline_entity")
        
        if entity_id and st.button("Show Timeline"):
            timeline_response = api_request("GET", f"/graph/timeline/{entity_id}")
            if timeline_response and timeline_response.get('timeline'):
                timeline = timeline_response['timeline']
                
                st.write(f"Found {len(timeline)} activities")
                for event in timeline[:10]:
                    st.write(f"**{event['date'][:10]}** - {event['type']}: {event['title']}")
                    st.caption(f"_{event['relationship']}_: {event['content']}")
                    st.divider()
            else:
                st.info("No timeline found for this entity")
    
    else:
        st.info("Your knowledge graph is building. Add more notes to see connections!")


# Main App
def main():
    """Main application"""
    st.set_page_config(
        page_title="Cognitive Co-pilot",
        page_icon="🧠",
        layout="wide"
    )
    
    # Sidebar
    if st.session_state.user:
        with st.sidebar:
            st.title("🧠 Cognitive Co-pilot")
            st.caption(f"Hello, **{st.session_state.user['name']}**")
            
            st.divider()
            st.subheader("⚡ Quick Capture")
            page = st.radio(
                "Main",
                ["🎯 Focus", "🧠 Brain Dump", "🤖 Ask AI"]
            )
            
            st.divider()
            st.subheader("📂 Organize")
            detail_page = st.radio(
                "View Details",
                ["📝 Notes", "👥 People", "📅 Meetings", "⏰ Tasks", "🌐 Knowledge Graph"]
            )
            
            # Combine page selections
            if page == "🎯 Focus":
                selected_page = "Focus"
            elif page == "🧠 Brain Dump":
                selected_page = "Brain Dump"
            elif page == "🤖 Ask AI":
                selected_page = "Ask AI"
            else:
                # Extract name from emoji selection
                page_map = {
                    "📝 Notes": "Notes",
                    "👥 People": "People",
                    "📅 Meetings": "Meetings",
                    "⏰ Tasks": "Tasks",
                    "🌐 Knowledge Graph": "Knowledge"
                }
                selected_page = page_map.get(detail_page, "Notes")
            
            st.divider()
            if st.button("🚪 Logout"):
                logout()
        
        # Route to pages
        if selected_page == "Focus":
            dashboard_page()
        elif selected_page == "Brain Dump":
            brain_dump_page()
        elif selected_page == "Ask AI":
            ask_ai_page()
        elif selected_page == "Notes":
            notes_page()
        elif selected_page == "People":
            people_page()
        elif selected_page == "Meetings":
            meetings_page()
        elif selected_page == "Tasks":
            reminders_page()
        elif selected_page == "Knowledge":
            knowledge_graph_page()
    else:
        auth_page()


def ask_ai_page():
    """Ask AI about your data"""
    st.title("🤖 Ask AI Assistant")
    
    st.write("Ask questions about your notes, get insights, and discover connections!")
    
    # Query interface
    query = st.text_input("What would you like to know?", placeholder="e.g., Who did I meet last week? What tasks do I have?")
    
    if st.button("Ask") and query:
        with st.spinner("🤔 Thinking..."):
            response = api_request("POST", "/query", {"message": query})
            
            if response and response.get("status") == "success":
                st.success("✅ Answer:")
                st.write(response["answer"])
                st.caption(f"Based on {response['sources']} notes")
            else:
                st.error("Could not generate answer")
    
    # Quick insights
    st.divider()
    st.subheader("💡 Quick Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Summarize all my notes"):
            with st.spinner("Analyzing..."):
                response = api_request("POST", "/query", {"message": "Summarize all my notes and tell me the main themes"})
                if response and response.get("answer"):
                    st.write(response["answer"])
    
    with col2:
        if st.button("👥 Who have I mentioned?"):
            with st.spinner("Searching..."):
                response = api_request("POST", "/query", {"message": "List all the people mentioned in my notes"})
                if response and response.get("answer"):
                    st.write(response["answer"])
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("📅 What's coming up?"):
            with st.spinner("Checking..."):
                response = api_request("POST", "/query", {"message": "What tasks or events do I have coming up?"})
                if response and response.get("answer"):
                    st.write(response["answer"])
    
    with col4:
        if st.button("🔗 Find connections"):
            with st.spinner("Analyzing..."):
                response = api_request("POST", "/query", {"message": "Find interesting connections or patterns in my notes"})
                if response and response.get("answer"):
                    st.write(response["answer"])


if __name__ == "__main__":
    main()
