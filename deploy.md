# Super OPC Hub — 部署指南

## 项目结构回顾

本项目由三部分组成，部署时需要把它们放到互联网上：

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   前端        │    │   后端        │    │   外部依赖     │
│   React SPA  │───►│   FastAPI    │───►│   Supabase   │
│   (静态文件)  │    │   (Python)   │    │   LLM API    │
└──────────────┘    └──────────────┘    └──────────────┘
   需要托管 HTML/       需要运行 Python        已在云端运行
   JS/CSS 文件          进程的服务器          只需配置密钥
```

**前端**是 React 打包后的纯静态文件（一个 `index.html` + 一堆 JS/CSS），只需要一个能"分发文件"的服务。
**后端**是一个需要持续运行的 Python 程序（FastAPI），需要一台能跑 Python 的服务器。
**Supabase** 和 **LLM API** 已经是别人托管好的云服务，我们只需要告诉后端它们的地址和密钥。

---

## 方案对比

| 方案 | 前端 | 后端 | 月费 | 适合 |
|------|------|------|------|------|
| **A. 零运维平台** | Vercel（免费） | Railway（$5/月起） | $5-10 | 个人开发者快速上线 |
| **B. Docker 单机** | Nginx | Docker 容器 | ￥50-100 | 已有 VPS、想完全控制 |
| **C. 阿里云全家桶** | OSS + CDN | ECS + Docker | ￥100-300 | 国内用户访问为主 |

---

## 方案 A：Vercel + Railway —— 零运维、最快上线

### 通俗理解

想象你要开一家店——

- **Vercel** 就像一个商场里的**展示柜**。你把做好的网页文件（HTML/JS/CSS）放进去，它就自动展示给全世界看。你不用管柜子怎么维护、怎么通电，商场全包了。

- **Railway** 就像一个**后厨**。你的 Python 程序在这里运行，处理用户请求。你告诉它"我的代码在 GitHub 上，启动命令是这个"，它就自动帮你运行。也不用管厨房设备维护。

- 用户打开你的网页 → 网页调用后端 API → 后端调用 LLM 和数据库 → 返回结果。

```
用户浏览器 ──► Vercel (前端页面)
     │
     │ 页面中的 JS 代码调用 API
     ▼
Railway (后端 Python) ──► Supabase (数据库)
     │
     └──► OpenAI / DeepSeek (AI 大模型)
```

### 为什么选这个？

- **零服务器管理**：不用 SSH 登录服务器，不用装 Docker，不用配防火墙
- **自动部署**：代码 push 到 GitHub，自动上线
- **免费额度大**：Vercel 个人项目免费，Railway 有 $5 免费额度
- **适合阶段**：MVP 验证、个人项目、小团队

### 缺点

- Railway 冷启动较慢（闲置后首次请求需 5-10 秒唤醒）
- 后端延迟可能比自建 VPS 高
- 超过免费额度后按用量计费

---

## 方案 B：Docker 单机部署 —— 一台 VPS 搞定一切

### 通俗理解

- **VPS（云虚拟机）**就像你在云端**租了一台电脑**。这台电脑 24 小时开机，有固定的 IP 地址。你在这台电脑上装软件、跑程序，完全归你管。

- **Docker** 就像一个**集装箱**。你把 Python 程序、依赖包、运行环境全部打包进一个箱子，这个箱子拿到任何装了 Docker 的机器上都能原样跑起来。不用纠结"这台机器 Python 版本对不对"之类的问题。

- **Nginx** 就像大楼的**前台接待员**。所有用户请求先到它这里：
  - 要页面的（`/`）→ 它直接给静态文件
  - 要数据的（`/api/`）→ 它转发给后端处理

```
用户浏览器
     │
     ▼
VPS (你的云电脑)
  │
  ▼
Nginx (前台接待员)
  ├──► 请求页面 → 返回 web/dist/ 里的静态文件
  └──► 请求 /api/ → 转发给 Docker 容器的 8000 端口
                         │
                         ▼
                    FastAPI 后端 ──► Supabase / LLM
```

### 为什么选这个？

- **完全控制**：服务器是你的，想怎么配怎么配
- **固定成本**：VPS 按月付费，不随流量暴增
- **性能可控**：没有冷启动问题，延迟最低
- **适合阶段**：有一定用户量后迁移、需要定制化部署

### 缺点

- 需要自己维护服务器（更新系统、看日志、处理故障）
- 需要配置域名、HTTPS 证书
- 需要懂一些 Linux 命令行

---

## 方案 C：阿里云全家桶 —— 国内访问最快

### 通俗理解

这是我之前开发的成都网站。

- **OSS（对象存储）** = 阿里云的**超级网盘**。你把前端文件传上去，它就像一个网盘一样存着。但它比网盘厉害的地方是，它能直接当网站用——别人访问一个网址就能看到你的网页。

- **CDN（内容分发网络）** = 在全国各地建了**无数个自动复印机**。你的文件上传到 OSS 后，CDN 会在北京、上海、广州、成都……各个城市自动复制一份。北京的用戶访问时从北京取文件，上海的用戶从上海取，速度极快。

- **ECS（云服务器）** = 和方案 B 的 VPS 一样，阿里云牌子的**租用电脑**。之所以用阿里云的，是因为它和 OSS、CDN 天然互通，延迟低、带宽大。

```
北京用户 ──► 北京 CDN 节点 (前端文件)
上海用户 ──► 上海 CDN 节点 (前端文件)
广州用户 ──► 广州 CDN 节点 (前端文件)
     │
     │ 页面中的 JS 调用 API
     ▼
阿里云 ECS (后端 Python) ──► Supabase / LLM API
```

### 为什么选这个？

- **国内访问极快**：CDN 在全国有节点，延迟通常 < 20ms
- **无需备案烦恼**（如用香港节点）：省去 ICP 备案流程
- **生态完善**：OSS + CDN + ECS 天然集成，管理方便
- **合规性**：数据存储在国内，符合监管要求
- **适合阶段**：面向国内用户的正式产品

### 缺点

- 费用较高（OSS 按存储和流量计费、ECS 按月付费）
- 需要实名认证、可能需要 ICP 备案（用国内节点时）
- 控制台配置相对复杂

---

## 三种方案选型建议

```
项目阶段          推荐方案

开发测试 ─────► 本地跑（pnpm dev + uvicorn）
MVP 验证 ─────► 方案 A：Vercel + Railway
            （最便宜、最快、零运维）
     │
     │ 用户多了、需要优化性能
     ▼
国内用户为主 ───► 方案 C：阿里云
海外用户为主 ───► 方案 B：VPS + Docker
```

如果做的是面向国内用户的正式产品，也可以跳过方案 A 直接从方案 C 开始。

---

## 事前准备

### 1. 准备 API 密钥（组合模式）

项目采用**组合模式**：DeepSeek 原生 API 做对话推理 + SiliconFlow 做向量运算。

- **DeepSeek API Key**：在 [platform.deepseek.com](https://platform.deepseek.com) 的 API Keys 页面获取
- **SiliconFlow API Key**：去 [cloud.siliconflow.cn](https://cloud.siliconflow.cn) 注册获取（新用户送免费额度，向量运算完全够用）

### 2. 注册 Supabase（数据库）

1. 打开 [supabase.com](https://supabase.com)，用 GitHub 登录
2. 创建新项目 → 起名（如 `opc-hub`）→ 选区域（建议 Southeast Asia）→ 设置数据库密码（记下来）
3. 等 1-2 分钟项目创建完成
4. 进入 SQL Editor → 粘贴 `api/migrations/001_init.sql` 的内容 → 点击 Run
5. Project Settings → API → 复制 `Project URL` 和 `service_role key`

### 3. 配置后端环境变量

```bash
# 后端环境变量 -- 创建 api/.env
cp api/.env.example api/.env
```

编辑 `api/.env`，填入真实值：

```env
# ─── DeepSeek 原生 API（对话推理）────────
LLM_API_KEY=sk-你的DeepSeek密钥
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# ─── SiliconFlow（向量运算）───────────────
EMBEDDING_API_KEY=sk-你的SiliconFlow密钥
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=BAAI/bge-m3

# ─── Supabase ──────────────────────────
SUPABASE_URL=https://你的项目ID.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOi...（service_role key，不是 anon key）
```

### 4. 构建前端

```bash
cd web
pnpm install
pnpm run build
# 输出在 web/dist/
```

---

## 方案 A 操作步骤：Vercel + Railway

### 第一步：部署前端到 Vercel

1. 将项目代码推送到 GitHub（如果没有，先在 github.com 创建仓库）
2. 打开 [vercel.com](https://vercel.com)，用 GitHub 账号登录
3. 点击 "New Project" → 选择你的仓库
4. 配置构建参数：
   - **Root Directory**: `web`
   - **Framework Preset**: Vite（一般自动识别）
5. 添加环境变量（在项目 Settings → Environment Variables）：

   | 变量名 | 值 | 说明 |
   |--------|-----|------|
   | `VITE_SUPABASE_URL` | `https://xxx.supabase.co` | Supabase 项目地址 |
   | `VITE_SUPABASE_ANON_KEY` | `eyJhbGci...` | Supabase 匿名密钥 |
   | `VITE_API_URL` | `https://xxx.railway.app` | 后端地址（部署完 Railway 后填入） |

6. 点击 Deploy。首次需等待构建完成（约 1-2 分钟）。
7. 部署成功后获得域名 `https://xxx.vercel.app`

### 第二步：部署后端到 Railway

1. 打开 [railway.app](https://railway.app)，用 GitHub 账号登录
2. 点击 "New Project" → "Deploy from GitHub" → 选择同一仓库
3. 配置：
   - **Root Directory**: `api`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. 在 Variables 页面添加 `api/.env` 中的所有环境变量
5. 部署，Railway 会自动：
   - 检测 `requirements.txt` 并安装 Python 依赖
   - 运行启动命令
6. 获得后端地址 `https://xxx.railway.app`

### 第三步：连接前后端

回到 Vercel 项目设置，将 `VITE_API_URL` 改为 Railway 的实际地址，然后重新部署（Vercel 会自动 rebuild）。

### 第四步：绑定自定义域名

**三种方案都支持你自己的域名。** 以你注册的 `www.superopchub.com` 为例，在 Vercel 上配置步骤如下：

#### 4.1 在 Vercel 后台添加域名

1. 打开 Vercel 项目 → Settings → Domains
2. 输入 `www.superopchub.com` → 点击 Add
3. Vercel 会提示你需要配置 DNS 记录

#### 4.2 在域名 DNS 控制台添加记录

去你注册域名的平台（阿里云 DNS、Cloudflare、GoDaddy 等），添加一条 DNS 记录：

| 类型 | 主机记录 | 记录值 |
|------|----------|--------|
| CNAME | `www` | `cname.vercel-dns.com` |

> **注意**：如果想把根域名 `superopchub.com`（不带 www）也指向网站，添加一条 A 记录指向 `76.76.21.21`。Vercel 后台会给出详细指引。

#### 4.3 验证生效

- DNS 生效通常需要 **几分钟到几小时**（全球 DNS 缓存刷新）
- 生效后，Vercel 会自动为你的域名申请并配置 **SSL 证书**（Let's Encrypt），全程无需手动操作
- 最终访问 `https://www.superopchub.com` 就能看到你的网站

#### 4.4 后端也绑定子域名（可选）

如果你想让后端用 `api.superopchub.com` 这个"好看"的地址而非 `xxx.railway.app`：

1. 在 DNS 控制台添加：`CNAME` → 主机记录 `api` → 记录值填 Railway 给你的域名（Railway 后台 Settings → Domains 可查）
2. 回到 Vercel 把 `VITE_API_URL` 改成 `https://api.superopchub.com` 并重新部署

```
最终效果：
  https://www.superopchub.com        → Vercel（前端页面）
  https://api.superopchub.com        → Railway（后端 API）
```

---

## 方案 B 操作步骤：Docker 单机

### 第一步：购买并登录 VPS

推荐最低配置：2核CPU、4GB 内存、40GB 硬盘（阿里云/腾讯云/AWS 均可）。

```bash
# 登录服务器
ssh root@你的服务器IP
```

### 第二步：安装 Docker

```bash
curl -fsSL https://get.docker.com | sh
```

这条命令会自动检测系统版本并安装 Docker（包括 `docker compose`）。

### 第三步：上传代码到服务器

方式一：从 GitHub 拉取
```bash
git clone <你的仓库地址> /opt/opc-hub
cd /opt/opc-hub
```

方式二：从本地上传
```bash
# 在本地执行
scp -r /Users/xiaguanghui/code/SuperOPCHub root@服务器IP:/opt/opc-hub
```

### 第四步：配置并启动

```bash
cd /opt/opc-hub

# 编辑环境变量，填入真实的 LLM API Key 和 Supabase 密钥
vi api/.env

# 构建并启动后端
docker compose up -d --build

# 验证后端运行正常
curl http://localhost:8000/api/health
# 应返回 {"status":"ok"}
```

### 第五步：部署前端 + Nginx

```bash
# 安装 nginx
apt install -y nginx

# 创建配置
cat > /etc/nginx/sites-available/opc-hub << 'EOF'
server {
    listen 80;
    server_name 你的域名或IP;

    # 前端静态文件
    root /opt/opc-hub/web/dist;
    index index.html;

    # SPA 路由支持：所有找不到的文件都返回 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 请求转发给后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/opc-hub /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

此时访问服务器 IP 就能看到网站了。

### 第六步：配置域名和 HTTPS

```bash
# 安装 certbot
apt install -y certbot python3-certbot-nginx

# 自动配置 HTTPS
certbot --nginx -d 你的域名.com

# 证书会在到期前自动续期
```

---

## 方案 C 操作步骤：阿里云全家桶

### 第一步：部署后端到 ECS

1. 购买 ECS 实例（建议 2核4G，CentOS 或 Ubuntu）
2. 按照上方方案 B 的步骤 2-4 部署 Docker 后端
3. 在安全组中开放 8000 端口

### 第二步：部署前端到 OSS + CDN

1. 进入阿里云 OSS 控制台，创建一个 Bucket
2. 开启"静态网站托管"，设置默认首页为 `index.html`
3. 将本地 `web/dist/` 目录下的所有文件上传到 Bucket
4. 进入 CDN 控制台，添加加速域名，源站选择刚才的 OSS Bucket
5. **重要**：CDN 设置中添加"回源规则"——状态码 404 时返回 200，指向 `/index.html`（SPA 路由必需）
6. 构建前端前，先修改 `VITE_API_URL` 为 ECS 的公网地址 + 8000 端口

### 第三步：配置域名

1. 在 CDN 控制台绑定自定义域名
2. 在域名 DNS 解析中添加 CNAME 记录，指向 CDN 提供的 CNAME 地址
3. CDN 中申请免费 SSL 证书

---

## 常见问题

### LLM API 调用超时怎么办？

对话生成通常需要 3-8 秒（大模型思考需要时间）。确保 Nginx 的 `proxy_read_timeout` 不小于 120 秒，否则用户会收到 504 错误。

### 前端改了环境变量但没生效？

Vite 的 `VITE_` 前缀环境变量是在 **`pnpm run build` 构建时** 注入到代码中的，不是运行时读取的。修改后必须重新构建并部署。

### Supabase 报权限错误？

- 后端 `api/.env` 中的 `SUPABASE_SERVICE_KEY` 必须是 **service_role key**（不是 anon key）。service_role key 拥有绕过 RLS 策略的完整权限。
- 前端 `.env.local` 中的 `VITE_SUPABASE_ANON_KEY` 是 **anon key**，权限受限。

### 国内服务器访问不了 OpenAI API？

改用国内可访问的替代方案：

| 替代 | `LLM_BASE_URL` | 模型名 |
|------|----------------|--------|
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| Moonshot | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |

所有方案都兼容 OpenAI API 格式，只需改 `LLM_BASE_URL` 和 `LLM_MODEL` 两个变量。

### Railway 冷启动慢？

Railway 免费计划在服务 30 分钟无请求后会自动休眠，下次请求需要 5-10 秒启动。解决方式：
1. 升级到付费计划（$5/月起，无休眠）
2. 使用 UptimeRobot 等免费服务每 5 分钟访问一次 `/api/health` 保持唤醒
