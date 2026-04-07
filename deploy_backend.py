import paramiko, os, stat

HOST = '118.25.82.150'
USER = 'ubuntu'
PASS = 'aP46{DwM%!,jbn'

LOCAL_BACKEND = r'C:\Users\26933\Desktop\Agent\project\SceneRank\backend'
REMOTE_BASE = '/home/ubuntu/scenerank'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)
sftp = ssh.open_sftp()

def upload_dir(local_dir, remote_dir):
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
    for item in os.listdir(local_dir):
        if item in ('__pycache__', '.env', 'db.sqlite3', 'staticfiles', 'images'):
            continue
        lpath = os.path.join(local_dir, item)
        rpath = remote_dir + '/' + item
        if os.path.isdir(lpath):
            upload_dir(lpath, rpath)
        else:
            sftp.put(lpath, rpath)
            print(f'  {rpath}')

upload_dir(LOCAL_BACKEND, REMOTE_BASE)
sftp.close()

# 写 .env
env_content = """SECRET_KEY=scenerank-prod-secret-key-2024
DEBUG=False
ALLOWED_HOSTS=118.25.82.150,wing-show.com,www.wing-show.com
ADMIN_TOKEN=scenerank_admin_2024
IMAGES_DIR=/home/ubuntu/website/projects/SceneRank/survey/images
CORS_ORIGINS=http://118.25.82.150,https://wing-show.com
"""
_, o, _ = ssh.exec_command(f'cat > {REMOTE_BASE}/.env << \'EOF\'\n{env_content}\nEOF')
o.read()

# 创建 venv 并安装依赖
cmds = [
    f'cd {REMOTE_BASE} && python3 -m venv venv',
    f'cd {REMOTE_BASE} && venv/bin/pip install -q -r requirements.txt',
    f'cd {REMOTE_BASE} && venv/bin/python manage.py migrate --noinput',
    f'cd {REMOTE_BASE} && venv/bin/python manage.py collectstatic --noinput',
]
for cmd in cmds:
    print(f'\n$ {cmd}')
    _, o, e = ssh.exec_command(cmd)
    out = o.read().decode()
    err = e.read().decode()
    if out: print(out)
    if err: print('ERR:', err)

ssh.close()
print('\ndone')
