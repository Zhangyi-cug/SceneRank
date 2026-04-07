import paramiko, os

HOST = '118.25.82.150'
USER = 'ubuntu'
PASS = 'aP46{DwM%!,jbn'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)
sftp = ssh.open_sftp()

# 上传新构建
DIST = r'C:\Users\26933\Desktop\Agent\project\SceneRank\frontend\dist'
REMOTE_SURVEY = '/home/ubuntu/website/projects/SceneRank/survey'

for f in ['index.html']:
    sftp.put(os.path.join(DIST, f), f'{REMOTE_SURVEY}/{f}')
    print(f'uploaded {f}')

for f in os.listdir(os.path.join(DIST, 'assets')):
    sftp.put(os.path.join(DIST, 'assets', f), f'{REMOTE_SURVEY}/assets/{f}')
    print(f'uploaded assets/{f}')

# 上传 1001-1020 图片
SRC = r'C:\Users\26933\Desktop\wenjuan\new-1000sv\新样本'
REMOTE_IMAGES = f'{REMOTE_SURVEY}/images'

uploaded = 0
for i in range(1001, 1021):
    fname = f'{i}.jpg'
    lpath = os.path.join(SRC, fname)
    if os.path.exists(lpath):
        sftp.put(lpath, f'{REMOTE_IMAGES}/{fname}')
        uploaded += 1
        print(f'uploaded images/{fname}')

print(f'\n{uploaded} images uploaded')
sftp.close()

# 验证
for path in [
    '/projects/SceneRank/survey/',
    '/projects/SceneRank/survey/images/1001.jpg',
    '/projects/SceneRank/survey/images/1020.jpg',
]:
    _, o, _ = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" http://localhost{path}')
    print(f'{path} -> {o.read().decode()}')

ssh.close()
