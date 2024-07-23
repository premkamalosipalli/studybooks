# Deploying the StudyBooks Application to AWS EC2

This guide provides instructions for deploying the StudyBooks application on an AWS EC2 instance running Ubuntu.

## 1. SSH into EC2 Instance

1. Connect to your EC2 instance via SSH:
    ```bash
    ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
    ```

## 2. Configure Firewall

1. List available applications:
    ```bash
    sudo ufw app list
    ```

2. Allow OpenSSH:
    ```bash
    sudo ufw allow OpenSSH
    ```

3. Enable UFW (Uncomplicated Firewall):
    ```bash
    sudo ufw enable
    ```

4. Check UFW status:
    ```bash
    sudo ufw status
    ```

## 3. Install Required Packages

1. Update package list and install required software:
    ```bash
    sudo apt update
    sudo apt install python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl virtualenv
    ```

## 4. Configure PostgreSQL Database

1. Switch to the PostgreSQL user:
    ```bash
    sudo -u postgres psql
    ```

2. Create the database and user:
    ```sql
    CREATE DATABASE studybooks;
    CREATE USER admin WITH PASSWORD 'password';
    ALTER ROLE admin SET client_encoding TO 'utf8';
    ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
    ALTER ROLE admin SET timezone TO 'utc';
    GRANT ALL PRIVILEGES ON DATABASE studybooks TO admin;
    ```

3. Exit PostgreSQL:
    ```sql
    \q
    ```

## 5. Clone the Project

1. Clone the Git repository:
    ```bash
    git clone https://github.com/premkamalosipalli/studybooks.git
    ```

2. Navigate to the project directory:
    ```bash
    cd studybooks
    ```

## 6. Set Up Python Virtual Environment

1. Create and activate a virtual environment:
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

2. Install dependencies:
    ```bash
    pip install Django gunicorn psycopg2-binary pillow djangorestframework
    ```

## 7. Apply Migrations and Create Superuser

1. Run migrations:
    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```

2. Create a superuser:
    ```bash
    python3 manage.py createsuperuser
    ```

3. Collect static files:
    ```bash
    python3 manage.py collectstatic
    ```

## 8. Run the Development Server

1. Allow port 8000 through the firewall:
    ```bash
    sudo ufw allow 8000
    ```

2. Run the server:
    ```bash
    python3 manage.py runserver
    ```

   Your application should now be accessible at `http://your-ec2-public-ip:8000`.

## 9. Set Up Gunicorn

1. Create Gunicorn socket file:
    ```bash
    sudo nano /etc/systemd/system/gunicorn.socket
    ```

    Add the following configuration:
    ```ini
    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/gunicorn.sock

    [Install]
    WantedBy=sockets.target
    ```

2. Create Gunicorn service file:
    ```bash
    sudo nano /etc/systemd/system/gunicorn.service
    ```

    Add the following configuration:
    ```ini
    [Unit]
    Description=gunicorn service
    Requires=gunicorn.socket
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/studybooks
    ExecStart=/home/ubuntu/studybooks/env/bin/gunicorn \
        --access-logfile - \
        --workers 3 \
        --bind unix:/run/gunicorn.sock studybooks.wsgi:application

    [Install]
    WantedBy=multi-user.target
    ```

3. Start and enable Gunicorn socket:
    ```bash
    sudo systemctl start gunicorn.socket
    sudo systemctl enable gunicorn.socket
    ```

4. Check Gunicorn status:
    ```bash
    sudo systemctl status gunicorn.socket
    ```

5. If there are errors, view logs:
    ```bash
    sudo journalctl -u gunicorn.socket
    ```

   Reload systemd and restart Gunicorn if needed:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart gunicorn
    ```

6. Test Gunicorn with:
    ```bash
    sudo systemctl status gunicorn
    curl --unix-socket /run/gunicorn.sock localhost
    ```

## 10. Configure Nginx

1. Create an Nginx configuration file:
    ```bash
    sudo nano /etc/nginx/sites-available/studybooks
    ```

    Add the following configuration:
    ```nginx
    server {
        listen 80;
        server_name your-ip domain-name;

        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
            root /home/ubuntu/studybooks;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:/run/gunicorn.sock;
        }
    }
    ```

2. Enable the Nginx site configuration:
    ```bash
    sudo ln -s /etc/nginx/sites-available/studybooks /etc/nginx/sites-enabled
    ```

3. Test Nginx configuration:
    ```bash
    sudo nginx -t
    ```

4. Restart Nginx:
    ```bash
    sudo systemctl restart nginx
    ```

5. Remove port 8000 allowance:
    ```bash
    sudo ufw delete allow 8000
    ```

6. Allow Nginx full access:
    ```bash
    sudo ufw allow 'Nginx Full'
    ```

## 11. Fix CSS Issues (if any)

1. Edit Nginx configuration to use the `ubuntu` user:
    ```bash
    sudo nano /etc/nginx/nginx.conf
    ```

    Change `user www-data;` to `user ubuntu;` in the first line.

2. Restart Nginx:
    ```bash
    sudo systemctl restart nginx
    ```

Your Django application should now be up and running on your EC2 instance, served by Gunicorn and Nginx.

