import os
import paramiko

NGINX = """\
server {
    server_name wing-show.com www.wing-show.com;
    root /home/ubuntu/website;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 10s;
    }
    location /projects/SceneRank/survey/images/ {
        alias /home/ubuntu/website/projects/SceneRank/survey/images/;
    }
    location /projects/SceneRank/survey/assets/ {
        alias /home/ubuntu/website/projects/SceneRank/survey/assets/;
    }
    location /projects/SceneRank/survey/ {
        alias /home/ubuntu/website/projects/SceneRank/survey/;
        index index.html;
        try_files $uri $uri/ /projects/SceneRank/survey/index.html;
    }
    location /projects/SceneRank/ {
        alias /home/ubuntu/website/projects/SceneRank/;
        index index.html;
        try_files $uri $uri/ =404;
    }
    location / {
        try_files $uri $uri/ =404;
    }
    location ~* \\.(exe|zip)$ {
        add_header Content-Type application/octet-stream;
        add_header Content-Disposition attachment;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/wing-show.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wing-show.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    listen 80 default_server;
    server_name _;

    location /survey/api/ {
        proxy_pass http://127.0.0.1:8002/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location /survey/admin/ {
        proxy_pass http://127.0.0.1:8002/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /survey/assets/ {
        alias /home/ubuntu/survey/dist/assets/;
    }
    location /survey/images/ {
        alias /home/ubuntu/survey/dist/images/;
    }
    location /survey/ {
        alias /home/ubuntu/survey/dist/;
        index index.html;
        try_files $uri /survey/index.html;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 10s;
    }
    location /projects/SceneRank/survey/images/ {
        alias /home/ubuntu/website/projects/SceneRank/survey/images/;
    }
    location /projects/SceneRank/survey/assets/ {
        alias /home/ubuntu/website/projects/SceneRank/survey/assets/;
    }
    location /projects/SceneRank/survey/ {
        alias /home/ubuntu/website/projects/SceneRank/survey/;
        index index.html;
        try_files $uri $uri/ /projects/SceneRank/survey/index.html;
    }
    location /projects/SceneRank/ {
        alias /home/ubuntu/website/projects/SceneRank/;
        index index.html;
        try_files $uri $uri/ =404;
    }
    location / {
        root /home/ubuntu/website;
        index index.html;
        try_files $uri $uri/ =404;
    }
    location ~* \\.(exe|zip)$ {
        root /home/ubuntu/website;
        add_header Content-Type application/octet-stream;
        add_header Content-Disposition attachment;
    }
}

server {
    if ($host = www.wing-show.com) {
        return 301 https://$host$request_uri;
    }
    if ($host = wing-show.com) {
        return 301 https://$host$request_uri;
    }
    listen 80;
    server_name wing-show.com www.wing-show.com;
    return 404;
}
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
_host = os.environ.get("SCENERANK_SSH_HOST", "118.25.82.150")
_user = os.environ.get("SCENERANK_SSH_USER", "ubuntu")
_pass = os.environ.get("SCENERANK_SSH_PASS", "")
if not _pass:
    raise SystemExit("请设置环境变量 SCENERANK_SSH_PASS（勿提交到 Git）")
ssh.connect(_host, username=_user, password=_pass)

stdin, stdout, stderr = ssh.exec_command('sudo tee /etc/nginx/sites-enabled/website > /dev/null')
stdin.write(NGINX)
stdin.channel.shutdown_write()
stdout.read()

_, o, _ = ssh.exec_command('sudo nginx -t 2>&1 && sudo systemctl reload nginx && echo reload_ok')
print(o.read().decode())

for path in [
    '/projects/SceneRank/survey/',
    '/projects/SceneRank/survey/images/1031.jpg',
    '/projects/SceneRank/survey/assets/index-CEzARyHU.js',
]:
    _, o, _ = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" http://localhost{path}')
    print(f'{path} -> {o.read().decode()}')

ssh.close()
