#!/usr/bin/env python3
"""
SceneRank 一键部署脚本
- 上传落地页到 /home/ubuntu/website/projects/SceneRank/
- 上传前端 dist 到 /home/ubuntu/website/projects/SceneRank/survey/
- 修改主页 index.html 中的"图像成对比较问卷平台"卡片，添加跳转链接
"""
import os
import paramiko
from pathlib import Path

HOST = '118.25.82.150'
USER = 'ubuntu'
PASS = 'aP46{DwM%!,jbn'

BASE = Path(__file__).parent
LANDING = BASE / 'landing' / 'index.html'
DIST    = BASE / 'frontend' / 'dist'

def connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PASS)
    return c

def run(ssh, cmd):
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err: print('[err]', err)
    return out

def upload_dir(sftp, local_dir, remote_dir):
    """递归上传目录"""
    for item in Path(local_dir).rglob('*'):
        if item.is_file():
            rel = item.relative_to(local_dir)
            remote_path = remote_dir + '/' + str(rel).replace('\\', '/')
            remote_parent = remote_path.rsplit('/', 1)[0]
            sftp.mkdir_p(remote_parent)
            print(f'  upload {rel}')
            sftp.put(str(item), remote_path)

# 给 SFTPClient 加 mkdir_p
def mkdir_p(sftp, remote_dir):
    dirs = remote_dir.split('/')
    path = ''
    for d in dirs:
        if not d:
            path = '/'
            continue
        path = path.rstrip('/') + '/' + d
        try:
            sftp.stat(path)
        except FileNotFoundError:
            sftp.mkdir(path)

import types

def main():
    print('=== 连接服务器 ===')
    ssh = connect()
    sftp = ssh.open_sftp()
    sftp.mkdir_p = types.MethodType(lambda self, p: mkdir_p(self, p), sftp)

    # 1. 创建目录
    print('\n=== 创建目录 ===')
    run(ssh, 'mkdir -p /home/ubuntu/website/projects/SceneRank/survey')

    # 2. 上传落地页
    print('\n=== 上传落地页 ===')
    sftp.put(str(LANDING), '/home/ubuntu/website/projects/SceneRank/index.html')
    print('  landing/index.html -> /home/ubuntu/website/projects/SceneRank/index.html')

    # 3. 上传前端 dist
    print('\n=== 上传前端 dist ===')
    for item in DIST.rglob('*'):
        if item.is_file():
            rel = item.relative_to(DIST)
            remote_path = '/home/ubuntu/website/projects/SceneRank/survey/' + str(rel).replace('\\', '/')
            remote_parent = remote_path.rsplit('/', 1)[0]
            mkdir_p(sftp, remote_parent)
            print(f'  {rel}')
            sftp.put(str(item), remote_path)

    # 4. 修改主页 index.html：给"图像成对比较问卷平台"卡片加链接
    print('\n=== 修改主页卡片 ===')
    old_card = '''      <div class="card">
        <div class="card-icon">📊</div>
        <div class="card-title">图像成对比较问卷平台</div>
        <div class="card-desc">Vue + Django + MySQL，图像两两对比评分，用于街道感知研究。</div>
        <div class="card-tags">
          <span class="card-tag">Vue</span>
          <span class="card-tag">Django</span>
          <span class="card-tag">MySQL</span>
        </div>
      </div>'''

    new_card = '''      <a class="card" href="/projects/SceneRank/">
        <div class="card-icon">📊</div>
        <div class="card-title">图像成对比较问卷平台</div>
        <div class="card-desc">Vue + Django，图像两两对比评分，用于街道感知研究。</div>
        <div class="card-tags">
          <span class="card-tag">Vue</span>
          <span class="card-tag">Django</span>
          <span class="card-tag">Python</span>
        </div>
        <span class="card-arrow">→</span>
      </a>'''

    # 读取远程 index.html
    with sftp.open('/home/ubuntu/website/index.html', 'r') as f:
        content = f.read().decode('utf-8')

    if old_card in content:
        content = content.replace(old_card, new_card)
        with sftp.open('/home/ubuntu/website/index.html', 'w') as f:
            f.write(content.encode('utf-8'))
        print('  主页卡片已更新 ✓')
    else:
        print('  [warn] 未找到原始卡片内容，请手动检查')

    sftp.close()
    ssh.close()
    print('\n=== 部署完成 ===')
    print('落地页: http://118.25.82.150/projects/SceneRank/')
    print('Demo:   http://118.25.82.150/projects/SceneRank/survey/')

if __name__ == '__main__':
    main()
