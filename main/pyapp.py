from flask import Flask, render_template, request, jsonify, redirect, url_for
import subprocess
import psutil
import shutil
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
from loguru import logger
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

load_dotenv()


@app.route('/')
def mainpage():
    autostart_tasks = load_autostart_tasks()
    return render_template('mainpage.html', autostart_tasks=autostart_tasks)

@app.route('/menu')
def mainmenu():
    return render_template('mainmenu.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/developers')
def developers():
    return render_template('developers.html')

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/run_task', methods=['POST'])
def run_task():
    task = request.form.get('task')  # Получаем задачу из формы
    tasks_mapping = {
        'check_ports': check_ports,
        'monitor_network': monitor_network,
        'monitor_processes': monitor_processes,
        'scan_nikto': scan_nikto,
        'create_backup': create_backup,
        'start_scan': start_scan,
    }
    if task in tasks_mapping:
        result = tasks_mapping[task]()
    else:
        result = f"Unknown task: {task}"
    return render_template('result.html', result=result)

@app.route('/toggle_autostart', methods=['POST'])
def toggle_autostart():
    task = request.form.get('task')
    autostart_tasks = load_autostart_tasks()
    if task in autostart_tasks:
        autostart_tasks.remove(task)
    else:
        autostart_tasks.append(task)
    save_autostart_tasks(autostart_tasks)
    return redirect(url_for('mainmenu'))

def load_autostart_tasks():
    try:
        with open('autostart.conf', 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []

def save_autostart_tasks(tasks):
    with open('autostart.conf', 'w') as f:
        f.write('\n'.join(tasks))

def run_with_sudo(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        return f"Error: {e}"

def check_ports():
    return run_with_sudo(['nmap', '-p-', 'localhost'])

def nmap():
    return run_with_sudo(['nmap', '-A', 'localhost'])

def monitor_network():
    return run_with_sudo(['netstat', '-antu'])

def monitor_processes():
    try:
        processes = [psutil.Process(pid) for pid in psutil.pids()]
        result = "\n".join([str(proc) for proc in processes])
        return result
    except Exception as e:
        logger.error(f"Error monitoring processes: {e}")
        return f"Error: {e}"

def scan_nikto():
    return run_with_sudo(['nikto', '-h', 'localhost'])

def create_backup():
    src_dir = '/var/www/critical_files'
    backup_dir = '/path/to/backup'
    try:
        shutil.copytree(src_dir, backup_dir)
        result = f"Backup created at {backup_dir}"
        send_backup_email(backup_dir)
    except Exception as e:
        logger.error(f"Backup creation error: {e}")
        result = f"Error creating backup: {e}"
    return result

if __name__ == '__main__':
    app.run(debug=False)
