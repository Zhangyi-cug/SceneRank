# SceneRank 场景评估

A web-based pairwise comparison survey platform for street scene perception research.

---

## 简介

SceneRank 是一个用于街道场景感知研究的在线问卷平台，支持图像两两对比（Pairwise Comparison）实验范式。受试者对随机抽取的街道图像对，在安全、美丽、活力、富裕、无聊、压抑等多个维度分别作出偏好判断，数据实时存入后端数据库，管理员可随时导出 CSV 进行分析。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vue Router + Vite |
| 后端 | Django 4 + Django REST Framework |
| 数据库 | SQLite（开发）/ PostgreSQL（生产可选） |
| 部署 | Nginx + Gunicorn + systemd |

---

## 功能

**受试者端**
- 背景调查（年龄、性别、职业等，题目可由管理员自定义）
- 随机图像对比，支持多维度评分
- 进度条显示，支持跳过当前对
- 响应式布局，支持手机端

**管理员端**
- 问卷配置：标题、描述、背景图
- 背景调查题目管理：增删题目、选项、题型（下拉/单选/文本）
- 图像对比配置：对比次数、图片 ID 范围、维度增删
- 数据管理：查看记录、单条删除、清空、导出 CSV
- 简单 Token 鉴权

---

## 项目结构

```
SceneRank/
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── components/     # BackgroundForm, ImageComparison, CompletePage
│   │   ├── pages/          # SurveyPage, AdminPage, AdminLogin
│   │   ├── composables/    # useSurvey.js（API 封装）
│   │   └── main.js
│   ├── public/
│   │   └── images/         # 街道图片（自行放置）
│   └── package.json
├── backend/                # Django 后端
│   ├── api/                # models, views, serializers, urls
│   ├── scenerank/          # settings, urls, wsgi
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── nginx/
│   ├── scenerank.conf      # Nginx 配置
│   └── scenerank.service   # systemd 服务
└── .gitignore
```

---

## 本地开发

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 初始化数据库
python manage.py migrate

# 启动开发服务器（默认 8000 端口）
python manage.py runserver
```

默认管理员 Token：`admin123`（可在 `.env` 中修改 `ADMIN_TOKEN`）

### 前端

```bash
cd frontend
npm install

# 复制环境变量
cp .env.example .env

# 启动开发服务器（默认 5173 端口）
npm run dev
```

访问：
- 问卷：`http://localhost:5173/#/survey`
- 管理后台：`http://localhost:5173/#/admin/login`

---

## 图片资源

将街道图片放入 `frontend/public/images/`，命名格式为 `{id}.jpg`，例如：

```
frontend/public/images/
├── 1001.jpg
├── 1002.jpg
└── ...
```

在管理后台的"图像对比"设置中配置图片 ID 范围（如 min: 1001, max: 2010）。

---

## 部署到服务器

### 1. 构建前端

```bash
cd frontend
npm run build
# 产物在 frontend/dist/
```

### 2. 配置后端环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env，设置 SECRET_KEY、ADMIN_TOKEN、ALLOWED_HOSTS 等
```

### 3. 初始化后端

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

### 4. 配置 Nginx

将 `nginx/scenerank.conf` 复制到 `/etc/nginx/sites-available/`，修改 `server_name` 和路径后启用：

```bash
sudo ln -s /etc/nginx/sites-available/scenerank.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 5. 配置 systemd 服务

将 `nginx/scenerank.service` 复制到 `/etc/systemd/system/`，修改路径和环境变量后启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable scenerank
sudo systemctl start scenerank
```

---

## 环境变量说明（backend/.env）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | Django 密钥 | 开发用默认值 |
| `DEBUG` | 调试模式 | `True` |
| `ALLOWED_HOSTS` | 允许的域名，逗号分隔 | `localhost,127.0.0.1` |
| `ADMIN_TOKEN` | 管理员鉴权 Token | `admin123` |
| `CORS_ORIGINS` | 允许跨域的前端地址 | `http://localhost:5173` |
| `IMAGES_DIR` | 图片目录路径 | `backend/images/` |

---

## API 接口

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/api/config/` | 获取问卷配置 | 无 |
| POST | `/api/config/` | 保存问卷配置 | Admin |
| POST | `/api/config/reset/` | 重置为默认配置 | Admin |
| GET | `/api/results/` | 获取所有结果 | Admin |
| POST | `/api/results/` | 提交一条对比记录 | 无 |
| DELETE | `/api/results/clear/` | 清空所有结果 | Admin |
| DELETE | `/api/results/{id}/` | 删除单条记录 | Admin |
| GET | `/api/results/export/` | 导出 CSV | Admin |
| POST | `/api/auth/login/` | 管理员登录 | 无 |

Admin 鉴权：请求头携带 `X-Admin-Token: <token>`

---

## 作者：wing | zhangyi23@cug.edu.cn
