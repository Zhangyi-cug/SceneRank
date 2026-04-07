import paramiko, os

HOST = '118.25.82.150'
USER = 'ubuntu'
PASS = 'aP46{DwM%!,jbn'
LOCAL = r'C:\Users\26933\Desktop\Agent\project\SceneRank\frontend\public\images'
REMOTE = '/home/ubuntu/website/projects/SceneRank/survey/images'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)
sftp = ssh.open_sftp()

for f in os.listdir(LOCAL):
    lpath = os.path.join(LOCAL, f)
    rpath = f'{REMOTE}/{f}'
    sftp.put(lpath, rpath)
    print(f'uploaded {rpath}')

sftp.close()

# 读取当前 nginx 配置，加入 images 路由
_, o, _ = ssh.exec_command('cat /etc/nginx/sites-enabled/website')
nginx = o.read().decode()

old = '    location /projects/SceneRank/survey/assets/ {'
new = '''    location /projects/SceneRank/survey/images/ {
        alias /home/ubuntu/website/projects/SceneRank/survey/images/;
    }
    location /projects/SceneRank/survey/assets/ {'''

if '/projects/SceneRank/survey/images/' not in nginx:
    nginx = nginx.replace(old, new, 1)
    # 同样修复 80 server block
    old2 = '    location /projects/SceneRank/survey/assets/ {\n        alias /home/ubuntu/website/projects/SceneRank/survey/assets/;\n    }\n    location /projects/SceneRank/survey/ {'
    new2 = '''    location /projects/SceneRank/survey/images/ {
        alias /home/ubuntu/website/projects/SceneRank/survey/images/;
    }
    location /projects/SceneRank/survey/assets/ {
        alias /home/ubuntu/website/projects/SceneRank/survey/assets/;
    }
    location /projects/SceneRank/survey/ {'''
    nginx = nginx.replace(old2, new2, 1)

    stdin, stdout, stderr = ssh.exec_command('sudo tee /etc/nginx/sites-enabled/website > /dev/null')
    stdin.write(nginx)
    stdin.channel.shutdown_write()
    stdout.read()
    print('nginx updated')

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
