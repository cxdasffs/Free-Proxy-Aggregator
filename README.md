# Proxy Admin / 免费代理管理系统 (Free-Proxy-Aggregator)

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## 🌍 Free-Proxy-Aggregator

Proxy Admin is a powerful, full-stack proxy management platform designed for security researchers and penetration testers. It automates the lifecycle of proxies: from fetching massive lists, validating anonymity/speed, to executing real-time simulated attacks.

### 🚀 Key Features

*   **Massive Proxy Pool**: Integrated with 10+ sources (Fate0, TheSpeedX, ProxyList, etc.) to fetch 100,000+ proxies.
*   **Elite Anonymity Check**: Automatically filters `Transparent` proxies to protect your real IP. Distinguishes `Elite` / `Anonymous` proxies.
*   **Anti-Fingerprinting**: Uses `curl_cffi` to simulate **Chrome 110** TLS fingerprints, bypassing Cloudflare WAF.
*   **Real-time Attack Stream**: SSE (Server-Sent Events) based attack module capable of launching high-concurrency requests.
*   **Visualization**: Interactive world map showing global proxy distribution.
*   **Smart Fallback**: Automatically downgrades from `SOCKS5` to `SOCKS5h` (Remote DNS) to maximize connectivity.
*   **Unsafe Mode**: Optional "Brute Force" mode to unleash all 60k+ unverified proxies for massive scale testing.

### 🛠️ Architecture

*   **Backend**: Django 4.2 + Celery + Redis (Async Tasks)
*   **Frontend**: Vue 3 + Vite + TailwindCSS (Modern UI)
*   **Network**: `requests`, `PySocks`, `curl_cffi` (TLS Spoofing)

### 📦 Installation

#### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Redis Server

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### 3. Celery Worker (For Fetching/Validating)
```bash
cd backend
# Windows (requires gevent)
celery -A backend worker --pool=gevent --loglevel=info
```

### 🎮 Usage

1.  **Proxies** -> **Fetch**: Click "Start Scan" to fetch proxies from all sources.
2.  **Dashboard**: Wait for validation tasks to identify "Elite" proxies.
3.  **Attack Test**: 
    *   Enter Target URL.
    *   Select Protocol/Region.
    *   **Strict Mode (Default)**: Uses only verified Elite proxies.
    *   **Unsafe Mode**: Check "取消严选" to use ALL proxies (Warning: May contain transparent proxies).

---

<a name="chinese"></a>
## 🇨🇳 免费代理管理系统

Proxy Admin 是一个专为安全研究人员设计的全栈代理管理平台。它实现了代理的全生命周期管理：从海量源抓取、匿名度/速度验证，到执行实时的模拟攻击测试。

### 🚀 核心功能

*   **海量代理池**：集成 10+ 个免费代理源（Fate0, TheSpeedX, 89ip 等），轻松抓取 5万+ 代理。
*   **高匿筛选验证**：自动识别 `Elite` (高匿) 与 `Transparent` (透明) 代理，确保您的真实 IP 不泄露。
*   **指纹伪装技术**：集成 `curl_cffi`，完美模拟 **Chrome 110** 的 TLS 指纹，有效绕过 Cloudflare 等 WAF 防护。
*   **实时流式攻击**：基于 SSE (Server-Sent Events) 的攻击模块，支持高并发、低延迟的压力测试。
*   **可视化地图**：交互式全球地图，直观展示网络资产分布。
*   **智能协议降级**：遇到 SOCKS 连接问题时，自动尝试 `SOCKS5h` (远程DNS解析)，大幅提高连通率。
*   **暴力模式 (Unsafe Mode)**：提供“取消严选”选项，允许解锁所有未验证代理，实现“人海战术”攻击。

### 🛠️ 技术架构

*   **后端**: Django 4.2 + Celery + Redis (异步任务队列)
*   **前端**: Vue 3 + Vite + TailwindCSS (极简暗黑风 UI)
*   **网络层**: `requests`, `PySocks`, `curl_cffi` (TLS 伪装)

### 📦 安装指南

#### 环境要求
*   Python 3.10+
*   Node.js 18+
*   Redis 服务

#### 1. 后端配置
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### 2. 前端配置
```bash
cd frontend
npm install
npm run dev
```

#### 3. 启动 Celery (用于抓取/验证)
```bash
cd backend
# Windows 用户推荐使用 gevent 模式
celery -A backend worker --pool=gevent --loglevel=info
```

### 🎮 使用说明

1.  **获取代理**：点击页面顶部的 "Start Scan" 按钮，系统将从全网抓取代理。
2.  **自动验证**：后台任务会自动清洗数据，识别出 "Elite" 高匿代理。
3.  **发起压测**：
    *   输入目标 URL。
    *   选择协议（HTTP/SOCKS）或地区。
    *   **严格模式 (默认)**：仅使用经验证的高匿代理，安全无忧。
    *   **取消严选 (Unsafe)**：勾选复选框（需确认风险），即可调用那 6万+ 个未验证的代理进行全覆盖测试。

---
*Disclaimer: This tool is for educational and security research purposes only. Do not use it for illegal activities.*
*免责声明：本工具仅供教学和安全研究使用，请勿用于非法用途。*
