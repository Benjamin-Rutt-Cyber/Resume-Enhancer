# Resume Deployment Guide - Oracle Cloud to re-vsion.com

**Last Updated:** January 12, 2026
**Status:** Waiting for Oracle Cloud ARM capacity
**Goal:** Deploy Resume Enhancement Tool to https://re-vsion.com

---

## 📌 Current Status

✅ **Completed:**
- Code pushed to GitHub: https://github.com/Benjamin-Rutt-Cyber/Resume-Enhancer
- .gitignore configured (sensitive data excluded)
- Docker configurations ready
- Deployment guides created

⏳ **Next Step:**
- Get Oracle Cloud ARM instance (VM.Standard.A1.Flex)
- Capacity currently full - retry later

---

## 🕐 When to Try Again

**Best times to get Oracle Cloud free tier capacity:**

### High Success Rate Times:
- **Early Morning:** 6:00 AM - 9:00 AM (your timezone)
- **Late Night:** 11:00 PM - 2:00 AM (your timezone)
- **Weekday Mornings:** Less demand than weekends

### Strategy:
1. Try **AD-2** first (Availability Domain 2)
2. If full, try **AD-3**
3. If all full, wait 30-60 minutes and try again
4. Keep the browser tab open and retry every 10-15 minutes

---

## 🚀 Quick Start: Create Oracle Cloud Instance

### Step 1: Go to Oracle Cloud Console
https://cloud.oracle.com/

### Step 2: Create Instance

**Navigation:**
- Click ☰ menu → Compute → Instances → Create Instance

**Configuration:**

1. **Name:**
   ```
   resume-enhancer-prod
   ```

2. **Placement:**
   - **Availability Domain:** AD-2 or AD-3 (try different ones if full)
   - Leave fault domain as default

3. **Image and Shape:**
   - Click "Change Image"
   - Select: **Rocky Linux 9 (aarch64)** OR **AlmaLinux 9 (aarch64)**
   - Click "Change Shape"
   - Select: **VM.Standard.A1.Flex**
   - **OCPUs:** 4 (max it out)
   - **Memory:** 24 GB (max it out)

4. **Networking:**
   - ✅ Create new virtual cloud network
   - Name: `vcn-resume-enhancer`
   - ✅ Create new public subnet
   - Name: `subnet-resume-enhancer`
   - ✅ **Assign a public IPv4 address** ← CRITICAL!

5. **Add SSH Keys:**
   - Select: "Generate a key pair for me"
   - Click "Save Private Key" → Save as `oracle-resume-key.key`
   - Click "Save Public Key" → Save as `oracle-resume-key.key.pub`
   - **SAVE THESE FILES SECURELY!**

6. **Boot Volume:**
   - Size: 50 GB (or up to 200 GB if you want)

7. **Click "Create"**

---

## 📝 After Instance is Created (Write These Down!)

Once your instance shows **"Running"** status:

### 1. Public IP Address:
```
Write here: ___.___.___.___
```

### 2. SSH Username:
```
rocky    (if using Rocky Linux)
almalinux (if using AlmaLinux)
```

### 3. SSH Key Location:
```
Write path: C:\Users\...\oracle-resume-key.key
```

---

## 🔓 Step 3: Open Firewall Ports

**IMPORTANT:** Oracle Cloud blocks ports by default. You must open them!

### On Oracle Cloud Console:

1. **Go to your instance details page**
2. **Scroll down to "Primary VNIC"**
3. **Click the Subnet name** (e.g., subnet-resume-enhancer)
4. **Click the Security List name** (e.g., Default Security List)
5. **Click "Add Ingress Rules"**

### Add Rule 1 (HTTP):
- **Source Type:** CIDR
- **Source CIDR:** `0.0.0.0/0`
- **IP Protocol:** TCP
- **Destination Port Range:** `80`
- **Description:** Allow HTTP
- Click "Add Ingress Rule"

### Add Rule 2 (HTTPS):
- **Source Type:** CIDR
- **Source CIDR:** `0.0.0.0/0`
- **IP Protocol:** TCP
- **Destination Port Range:** `443`
- **Description:** Allow HTTPS
- Click "Add Ingress Rule"

---

## 💻 Step 4: SSH into Your Server

### Windows (PowerShell):

```powershell
# Set permissions on key (one-time setup)
icacls "C:\path\to\oracle-resume-key.key" /inheritance:r
icacls "C:\path\to\oracle-resume-key.key" /grant:r "%USERNAME%:R"

# SSH into server (replace IP and username)
ssh -i "C:\path\to\oracle-resume-key.key" rocky@YOUR_SERVER_IP
# OR
ssh -i "C:\path\to\oracle-resume-key.key" almalinux@YOUR_SERVER_IP
```

### First Time Connection:
- It will ask: "Are you sure you want to continue connecting?"
- Type: `yes` and press Enter

---

## 📦 Step 5: Deploy Application

Once you're SSH'd into the server, run these commands:

### 5.1 Install Git
```bash
sudo dnf update -y
sudo dnf install git -y
```

### 5.2 Clone Your Repository
```bash
cd ~
git clone https://github.com/Benjamin-Rutt-Cyber/Resume-Enhancer.git
cd Resume-Enhancer
```

### 5.3 Verify Docker is Installed
```bash
docker --version
docker-compose --version
```

**If Docker is NOT installed:**
```bash
# Install Docker
sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes
exit
# SSH back in
```

### 5.4 Configure Environment Variables
```bash
cd ~/Resume-Enhancer/backend
cp .env.example .env
nano .env
```

**Edit the .env file with these settings:**
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:CHANGE_THIS_STRONG_PASSWORD@postgres:5432/resume_enhancement

# Security Configuration - CRITICAL!
SECRET_KEY=PASTE_YOUR_GENERATED_KEY_HERE
DEBUG=False

# CORS Origins
CORS_ORIGINS=["https://re-vsion.com","http://re-vsion.com"]

# Workspace
WORKSPACE_ROOT=workspace
```

**Generate a strong SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy the output and paste it as SECRET_KEY in .env
```

**Save the file:**
- Press `Ctrl + X`
- Press `Y`
- Press `Enter`

### 5.5 Build Docker Images
```bash
cd ~/Resume-Enhancer
docker-compose build
```
**This takes 5-10 minutes**

### 5.6 Start Services
```bash
docker-compose up -d
```

### 5.7 Check Services are Running
```bash
docker-compose ps
```
**Expected: All services show "Up"**

### 5.8 Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### 5.9 Verify Backend Health
```bash
curl http://localhost:8000/api/health
```
**Expected: {"status":"healthy"...}**

---

## 🌐 Step 6: Install and Configure Nginx

### 6.1 Install Nginx
```bash
sudo dnf install nginx -y
```

### 6.2 Configure Firewall on Server
```bash
# Rocky/AlmaLinux use firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 6.3 Create Nginx Configuration
```bash
sudo nano /etc/nginx/conf.d/re-vsion.conf
```

**Paste this configuration:**
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name re-vsion.com www.re-vsion.com;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000/api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API docs
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/api/health;
    }

    # Frontend - temporarily proxy to port 3000
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Save:** Ctrl+X, Y, Enter

### 6.4 Test and Start Nginx
```bash
# Test configuration
sudo nginx -t

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 🎨 Step 7: Start Frontend

### 7.1 Install Node.js
```bash
# Install Node.js 18.x
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install nodejs -y

# Verify
node --version
npm --version
```

### 7.2 Install PM2 (Process Manager)
```bash
sudo npm install -g pm2
```

### 7.3 Install Frontend Dependencies
```bash
cd ~/Resume-Enhancer/frontend
npm install
```

### 7.4 Start Frontend with PM2
```bash
pm2 start "npm run dev" --name resume-frontend

# Configure PM2 to start on boot
pm2 startup
# Copy and run the command it shows
pm2 save
```

---

## 🔒 Step 8: Install SSL Certificate

### 8.1 Install Certbot
```bash
sudo dnf install certbot python3-certbot-nginx -y
```

### 8.2 Get SSL Certificate
```bash
sudo certbot --nginx -d re-vsion.com -d www.re-vsion.com
```

**Follow the prompts:**
1. Enter your email address
2. Agree to terms of service (Y)
3. Redirect HTTP to HTTPS? → **Yes (2)**

**Certbot will:**
- Obtain SSL certificate
- Automatically configure Nginx
- Set up auto-renewal

### 8.3 Test Auto-Renewal
```bash
sudo certbot renew --dry-run
```

---

## 🌍 Step 9: Update DNS on Hostinger

### 9.1 Log into Hostinger
https://hpanel.hostinger.com/

### 9.2 Navigate to DNS Settings
1. Click on your domain: **re-vsion.com**
2. Go to **"DNS / Name Servers"**
3. Click **"DNS Records"** or **"Manage DNS"**

### 9.3 Update A Records

**Find and edit the A record:**

**Record 1:**
- **Type:** A
- **Name:** @ (or leave blank for root domain)
- **Value/Points to:** `YOUR_ORACLE_CLOUD_IP`
- **TTL:** 14400 (or default)

**Record 2 (www subdomain):**
- **Type:** A
- **Name:** www
- **Value/Points to:** `YOUR_ORACLE_CLOUD_IP`
- **TTL:** 14400

**Save changes**

### 9.4 Wait for DNS Propagation
- **Time:** 5 minutes to 48 hours (usually 15-30 minutes)
- **Check status:** https://dnschecker.org/

---

## ✅ Step 10: Verify Deployment

### Test Each Component:

1. **Health Check:**
   ```bash
   curl http://YOUR_SERVER_IP/health
   ```
   Expected: `{"status":"healthy"}`

2. **Test Domain (after DNS propagates):**
   ```bash
   curl http://re-vsion.com/health
   ```

3. **Test HTTPS (after SSL):**
   ```bash
   curl https://re-vsion.com/health
   ```

4. **Open in Browser:**
   - Visit: https://re-vsion.com
   - Should load the Resume Enhancement Tool
   - Green padlock icon (SSL working)

5. **Full Test:**
   - Upload a resume
   - Add job description
   - Create enhancement
   - Download enhanced resume

---

## 🐛 Troubleshooting

### Issue: Can't SSH into server
```bash
# Check instance is running in Oracle Cloud Console
# Verify you're using correct IP and username
# Check SSH key permissions

# Windows - fix key permissions:
icacls "path\to\key.key" /inheritance:r
icacls "path\to\key.key" /grant:r "%USERNAME%:R"
```

### Issue: Connection refused on port 8000
```bash
# Check backend is running
docker-compose ps

# Check logs
docker-compose logs backend

# Restart
docker-compose restart backend
```

### Issue: 502 Bad Gateway
```bash
# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Verify backend is accessible
curl http://localhost:8000/api/health

# Restart nginx
sudo systemctl restart nginx
```

### Issue: Frontend not loading
```bash
# Check PM2 status
pm2 status

# Check logs
pm2 logs resume-frontend

# Restart
pm2 restart resume-frontend
```

### Issue: SSL not working
```bash
# Check certificate
sudo certbot certificates

# Renew manually
sudo certbot renew

# Check nginx config
sudo nginx -t
```

### Issue: Database errors
```bash
# Check PostgreSQL
docker-compose logs postgres

# Verify connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine.url)"
```

---

## 📋 Maintenance Commands

### View Logs
```bash
# All Docker services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Frontend
pm2 logs resume-frontend

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Docker services
docker-compose restart

# Nginx
sudo systemctl restart nginx

# Frontend
pm2 restart resume-frontend
```

### Update Code
```bash
cd ~/Resume-Enhancer
git pull origin master
docker-compose build
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres resume_enhancement > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U postgres resume_enhancement < backup_20260112.sql
```

---

## 🎯 Success Criteria

✅ All checks passed:
- [ ] Oracle Cloud instance running
- [ ] SSH access working
- [ ] Docker containers running
- [ ] Database migrations applied
- [ ] Backend health check returns healthy
- [ ] Nginx configured and running
- [ ] Frontend accessible
- [ ] SSL certificate installed
- [ ] DNS pointing to server
- [ ] https://re-vsion.com loads
- [ ] Can upload resume
- [ ] Can download enhanced resume

---

## 📞 Quick Reference

**Your Configuration:**
- **Domain:** re-vsion.com
- **Hosting:** Oracle Cloud Always Free
- **OS:** Rocky Linux 9 or AlmaLinux 9
- **SSH User:** rocky or almalinux
- **GitHub:** https://github.com/Benjamin-Rutt-Cyber/Resume-Enhancer
- **Deployment Guide:** DEPLOY_TO_RE-VSION.md

**Important Files:**
- SSH Key: oracle-resume-key.key
- Backend .env: ~/Resume-Enhancer/backend/.env
- Nginx config: /etc/nginx/conf.d/re-vsion.conf

**Commands:**
```bash
# SSH
ssh -i oracle-resume-key.key rocky@YOUR_IP

# Docker
docker-compose ps
docker-compose logs -f
docker-compose restart

# Frontend
pm2 status
pm2 logs resume-frontend

# Nginx
sudo systemctl status nginx
sudo nginx -t
```

---

**Ready to deploy when Oracle Cloud capacity is available!**

**Try creating the instance at these times:**
- Early morning (6-9 AM)
- Late night (11 PM - 2 AM)
- Keep retrying every 10-15 minutes

**Good luck! 🚀**
