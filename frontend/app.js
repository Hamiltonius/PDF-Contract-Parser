// LifeOS Frontend JavaScript

const API_BASE = '/api';

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabId = button.getAttribute('data-tab');
        switchTab(tabId);
    });
});

function switchTab(tabId) {
    // Update buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');

    // Load data for specific tabs
    if (tabId === 'dashboard') {
        loadDashboard();
    } else if (tabId === 'tasks') {
        loadTasks();
    } else if (tabId === 'calendar') {
        loadCalendarEvents();
    }
}

// Loading indicator
function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// API helper
async function apiCall(endpoint, method = 'GET', body = null) {
    showLoading();
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'API request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        alert(`Error: ${error.message}`);
        return null;
    } finally {
        hideLoading();
    }
}

// Dashboard functions
async function loadDashboard() {
    loadUpcomingTasks();
}

async function loadUpcomingTasks() {
    const data = await apiCall('/tasks/due-soon?days=3');
    if (data) {
        const html = data.tasks && data.tasks.length > 0
            ? data.tasks.map(task => `
                <div style="padding: 8px; border-left: 3px solid #667eea; margin-bottom: 8px;">
                    <strong>${task.title}</strong><br>
                    <small>Due: ${task.due_date || 'TBD'} | Priority: ${task.priority}</small>
                </div>
            `).join('')
            : '<p>No upcoming tasks</p>';
        document.getElementById('upcoming-tasks').innerHTML = html;
    }
}

async function createDailyPlan() {
    const data = await apiCall('/planner/daily-plan', 'POST');
    if (data && data.plan) {
        document.getElementById('daily-overview').innerHTML = `<div class="content-area">${data.plan}</div>`;
        document.getElementById('planner-output').innerHTML = `<h3>Daily Plan</h3><div class="content-area">${data.plan}</div>`;
    }
}

// Calendar functions
async function syncCalendar() {
    const data = await apiCall('/calendar/sync?days_ahead=7', 'POST');
    if (data) {
        alert(`Synced ${data.event_count} calendar events`);
        displayCalendarEvents(data.events);
    }
}

function displayCalendarEvents(events) {
    const html = events && events.length > 0
        ? events.map(event => `
            <div style="padding: 10px; border-left: 3px solid #764ba2; margin-bottom: 10px;">
                <strong>${event.summary}</strong><br>
                <small>${event.start_time} - ${event.end_time}</small><br>
                ${event.location ? `<small>📍 ${event.location}</small>` : ''}
            </div>
        `).join('')
        : '<p>No calendar events found</p>';

    document.getElementById('calendar-events').innerHTML = html;
    document.getElementById('upcoming-events').innerHTML = events.slice(0, 3).map(event => `
        <div style="padding: 5px; margin-bottom: 5px;">
            <strong>${event.summary}</strong><br>
            <small>${event.start_time}</small>
        </div>
    `).join('') || '<p>No upcoming events</p>';
}

async function loadCalendarEvents() {
    const data = await apiCall('/calendar/sync?days_ahead=7', 'POST');
    if (data && data.events) {
        displayCalendarEvents(data.events);
    }
}

async function findFreeTime() {
    const duration = prompt('Duration in minutes:', '60');
    if (!duration) return;

    const data = await apiCall('/calendar/find-free-time', 'POST', {
        action: 'find_free_time',
        params: { duration: parseInt(duration) }
    });

    if (data && data.suggestions) {
        alert(`Free Time Suggestions:\n\n${data.suggestions}`);
    }
}

// Task functions
async function loadTasks() {
    const data = await apiCall('/tasks/due-soon?days=30');
    if (data && data.tasks) {
        const html = data.tasks.length > 0
            ? data.tasks.map(task => `
                <div style="padding: 12px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px;">
                    <strong>${task.title}</strong><br>
                    <small>Status: ${task.status} | Priority: ${task.priority} | Due: ${task.due_date || 'TBD'}</small>
                </div>
            `).join('')
            : '<p>No tasks found</p>';
        document.getElementById('tasks-list').innerHTML = html;
    }
}

function showCreateTaskForm() {
    document.getElementById('create-task-form').style.display = 'block';
}

function hideCreateTaskForm() {
    document.getElementById('create-task-form').style.display = 'none';
}

async function createTask(event) {
    event.preventDefault();

    const taskData = {
        title: document.getElementById('task-title').value,
        description: document.getElementById('task-description').value,
        priority: parseInt(document.getElementById('task-priority').value),
        due_date: document.getElementById('task-due-date').value || null,
    };

    const data = await apiCall('/tasks/create', 'POST', taskData);
    if (data && data.success) {
        alert('Task created successfully!');
        hideCreateTaskForm();
        event.target.reset();
        loadTasks();
    }
}

async function prioritizeTasks() {
    const data = await apiCall('/tasks/prioritize', 'POST');
    if (data && data.ai_suggestions) {
        alert(`AI Task Prioritization:\n\n${data.ai_suggestions}`);
        loadTasks();
    }
}

// Email functions
async function syncEmails() {
    const data = await apiCall('/email/sync?limit=50', 'POST');
    if (data) {
        alert(`Synced ${data.email_count} emails`);
        displayEmails(data.emails);
    }
}

function displayEmails(emails) {
    const html = emails && emails.length > 0
        ? emails.slice(0, 20).map(email => `
            <div style="padding: 10px; border-bottom: 1px solid #ddd; margin-bottom: 10px;">
                <strong>${email.subject}</strong><br>
                <small>From: ${email.sender}</small><br>
                <small>${email.received_date}</small>
            </div>
        `).join('')
        : '<p>No emails found</p>';
    document.getElementById('email-list').innerHTML = html;
}

async function extractTasksFromEmails() {
    const data = await apiCall('/email/extract-tasks', 'POST', []);
    if (data) {
        alert(`Extracted ${data.task_count} tasks from emails`);
        if (data.tasks.length > 0) {
            const tasksHtml = data.tasks.map(t => `- ${t.title}`).join('\n');
            alert(`Tasks:\n${tasksHtml}`);
        }
    }
}

async function summarizeEmails() {
    const data = await apiCall('/email/summarize-unread');
    if (data && data.summary) {
        document.getElementById('email-summary').innerHTML = `<div class="content-area">${data.summary}</div>`;
    }
}

// Planner functions
async function createWeeklyPlan() {
    const data = await apiCall('/planner/weekly-plan', 'POST');
    if (data && data.plan) {
        document.getElementById('planner-output').innerHTML = `<h3>Weekly Plan</h3><div class="content-area">${data.plan}</div>`;
    }
}

async function optimizeSchedule() {
    const data = await apiCall('/planner/optimize-schedule', 'POST', {
        action: 'optimize_schedule',
        params: {}
    });
    if (data && data.suggestions) {
        document.getElementById('planner-output').innerHTML = `<h3>Schedule Optimization</h3><div class="content-area">${data.suggestions}</div>`;
    }
}

// Document upload
async function uploadDocument() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showLoading();
    try {
        const response = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('document-result').innerHTML = `
                <h3>Document Processed</h3>
                <p><strong>Filename:</strong> ${data.filename}</p>
                <p><strong>Pages:</strong> ${data.page_count || 'N/A'}</p>
                <p><strong>Text Length:</strong> ${data.text_length || 'N/A'} characters</p>
            `;
            alert('Document uploaded and processed successfully!');
        } else {
            alert('Error processing document');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Initialize dashboard on load
window.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
