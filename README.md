# psproxy for perfSONAR pScheduler GUI for on-demand measurement

psGUI in combination with psproxy allows users to start on-demand measurement between two nodes from the MaDDash grid.

## Configuration

Clone repository and edit config.py to configure URLs.

COnfigure with wsgi server

Gunicorn /etc/systemd/system/psproxy.service example:
```
[Unit]
Description=Gunicorn serving psproxy
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/psproxy
Environment="PATH=/var/www/psproxy/venv/bin"
ExecStart=/var/www/psproxy/venv/bin/gunicorn --workers 4 --bind unix:psproxy.sock -m 007 --log-level warning --error-logfile /var/log/gunicorn_error.log --timeout 240 --log-file /var/log/gunicorn.log wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```
