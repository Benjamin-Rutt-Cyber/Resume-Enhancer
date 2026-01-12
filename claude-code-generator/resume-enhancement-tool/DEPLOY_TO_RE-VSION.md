# Deploying to re-vsion.com on Oracle Cloud

**Status:** Ready to deploy
**Domain:** re-vsion.com
**Server:** Oracle Cloud Always Free (Docker installed, DNS configured)

---

## Prerequisites Checklist

- ✅ Oracle Cloud server with Docker installed
- ✅ re-vsion.com DNS pointing to server IP
- ⬜ SSH access to server
- ⬜ Git installed on server (or will use file transfer)

---

## Step 1: Transfer Code to Server

### Option A: Using Git (Recommended)

**On your local machine:**
```bash
cd D:\Linux\claude-code-generator\resume-enhancement-tool

# Initialize git if not already done
git init
git add .
git commit -m "Prepare for deployment to re-vsion.com"

# Push to GitHub (create repo first at github.com)
git remote add origin https://github.com/YOUR_USERNAME/resume-enhancement-tool.git
git push -u origin master
```

**On your Oracle Cloud server (via SSH):**
```bash
# Install git if needed
sudo apt update
sudo apt install git -y

# Clone the repository
cd /home/ubuntu  # or your preferred location
git clone https://github.com/YOUR_USERNAME/resume-enhancement-tool.git
cd resume-enhancement-tool
```

### Option B: Using SCP (Direct Transfer)

**On your local machine (PowerShell/CMD):**
```powershell
# Replace YOUR_SERVER_IP with your actual IP
# Replace ubuntu with your actual username
scp -r D:\Linux\claude-code-generator\resume-enhancement-tool ubuntu@YOUR_SERVER_IP:/home/ubuntu/
```

---

## Step 2: Configure Production Environment

**On your server:**
```bash
cd /home/ubuntu/resume-enhancement-tool/backend

# Create production .env file
cp .env.example .env
nano .env  # or use vi/vim
```

**Update .env with production settings:**
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:CHANGE_THIS_PASSWORD@postgres:5432/resume_enhancement

# Security Configuration (CRITICAL!)
SECRET_KEY=YOUR_SUPER_SECRET_KEY_AT_LEAST_32_CHARS_LONG_CHANGE_THIS
DEBUG=False

# CORS Origins - your domain
CORS_ORIGINS=["https://re-vsion.com","http://re-vsion.com"]

# Workspace
WORKSPACE_ROOT=workspace

# Optional: Anthropic API (if you want style previews)
# ANTHROPIC_API_KEY=your-api-key-here
```

**Generate a secure SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Step 3: Create Production Docker Compose Override

**On your server:**
```bash
cd /home/ubuntu/resume-enhancement-tool

# Create production override file
nano docker-compose.override.yml
```

**Add this content:**
```yaml
version: '3.8'

services:
  backend:
    restart: unless-stopped
    environment:
      - DEBUG=False
    ports:
      - "127.0.0.1:8000:8000"  # Only accessible from localhost (nginx will proxy)

  postgres:
    restart: unless-stopped
    environment:
      - POSTGRES_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD
    volumes:
      - postgres-data:/var/lib/postgresql/data

  worker:
    restart: unless-stopped

volumes:
  postgres-data:
    driver: local
```

---

## Step 4: Build and Start Docker Containers

**On your server:**
```bash
cd /home/ubuntu/resume-enhancement-tool

# Build the images
docker-compose build

# Start the services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

**Expected output:**
```
resume-enhancement-tool_postgres   Up      5432/tcp
resume-enhancement-tool_backend    Up      127.0.0.1:8000->8000/tcp
resume-enhancement-tool_worker     Up
```

---

## Step 5: Run Database Migrations

**On your server:**
```bash
cd /home/ubuntu/resume-enhancement-tool

# Run migrations
docker-compose exec backend alembic upgrade head

# Verify
docker-compose exec backend alembic current
```

**Expected:** Should show latest migration (b1bb9c5ce84e)

---

## Step 6: Install and Configure Nginx

**On your server:**
```bash
# Install nginx if not already installed
sudo apt update
sudo apt install nginx -y

# Create nginx configuration for re-vsion.com
sudo nano /etc/nginx/sites-available/re-vsion.com
```

**Add this configuration:**
```nginx
# Redirect HTTP to HTTPS (will be enabled after SSL setup)
server {
    listen 80;
    listen [::]:80;
    server_name re-vsion.com www.re-vsion.com;

    # Temporary: Allow HTTP for initial testing
    # After SSL is set up, this will redirect to HTTPS

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API endpoints
    location /api {
        proxy_pass http://localhost:8000/api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' 'https://re-vsion.com' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Origin, X-Requested-With, Content-Type, Accept, Authorization' always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
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
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

**Enable the site:**
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/re-vsion.com /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Enable nginx on boot
sudo systemctl enable nginx
```

---

## Step 7: Start Frontend on Server

Since the frontend is not in Docker Compose, we need to serve it:

### Option A: Run Frontend with PM2 (Recommended for Development Mode)

**On your server:**
```bash
# Install Node.js if not already installed
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install PM2 globally
sudo npm install -g pm2

# Install frontend dependencies
cd /home/ubuntu/resume-enhancement-tool/frontend
npm install

# Start frontend with PM2
pm2 start "npm run dev" --name resume-frontend

# Configure PM2 to start on boot
pm2 startup
pm2 save
```

### Option B: Build and Serve Frontend with Nginx (Better for Production)

**On your server:**
```bash
cd /home/ubuntu/resume-enhancement-tool/frontend

# Install dependencies
npm install

# Build for production
npm run build

# The build will create a 'dist' folder
```

**Update nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/re-vsion.com
```

**Replace the frontend location block with:**
```nginx
    # Serve built frontend files
    location / {
        root /home/ubuntu/resume-enhancement-tool/frontend/dist;
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
```

**Restart nginx:**
```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 8: Set Up SSL with Let's Encrypt

**On your server:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate for re-vsion.com
sudo certbot --nginx -d re-vsion.com -d www.re-vsion.com

# Follow the prompts:
# - Enter your email address
# - Agree to terms of service
# - Choose whether to redirect HTTP to HTTPS (recommend YES)
```

**Certbot will automatically:**
- Obtain SSL certificates
- Update nginx configuration
- Set up automatic renewal

**Test auto-renewal:**
```bash
sudo certbot renew --dry-run
```

---

## Step 9: Configure Firewall

**On your server (if Oracle Cloud):**
```bash
# Allow HTTP and HTTPS through firewall
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT

# Save rules
sudo netfilter-persistent save

# Or on Oracle Linux:
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

**Also configure Oracle Cloud security list:**
1. Go to Oracle Cloud Console
2. Navigate to your instance → Subnet → Security Lists
3. Add ingress rules:
   - Port 80 (HTTP) from 0.0.0.0/0
   - Port 443 (HTTPS) from 0.0.0.0/0

---

## Step 10: Verify Deployment

**Test each component:**

1. **Health Check:**
   ```bash
   curl http://localhost:8000/api/health
   ```
   Expected: `{"status":"healthy",...}`

2. **API Access:**
   ```bash
   curl http://localhost:8000/api/resumes
   ```
   Expected: `{"resumes":[],...}`

3. **Frontend (local):**
   ```bash
   curl http://localhost:3000
   ```
   Expected: HTML content

4. **Nginx Proxy:**
   ```bash
   curl http://re-vsion.com/health
   ```
   Expected: Health check response

5. **SSL (after certbot):**
   ```bash
   curl https://re-vsion.com/health
   ```
   Expected: Health check response with SSL

6. **Full Test in Browser:**
   - Visit: https://re-vsion.com
   - Expected: Resume Enhancement Tool loads
   - Test: Upload a resume
   - Test: Create enhancement
   - Test: Download enhanced resume

---

## Troubleshooting

### Issue: "Connection refused" on port 8000
```bash
# Check backend is running
docker-compose ps

# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Issue: "502 Bad Gateway" from nginx
```bash
# Check nginx error log
sudo tail -f /var/log/nginx/error.log

# Verify backend is accessible
curl http://localhost:8000/api/health

# Check nginx configuration
sudo nginx -t
```

### Issue: Frontend not loading
```bash
# If using PM2:
pm2 logs resume-frontend

# If using built files:
ls -la /home/ubuntu/resume-enhancement-tool/frontend/dist

# Check nginx is serving files
sudo nginx -t
sudo systemctl status nginx
```

### Issue: SSL certificate not working
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Check nginx SSL configuration
sudo nano /etc/nginx/sites-available/re-vsion.com
```

### Issue: Database connection errors
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL
```

---

## Maintenance Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres

# Frontend (if using PM2)
pm2 logs resume-frontend
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend

# Nginx
sudo systemctl restart nginx
```

### Update Application
```bash
cd /home/ubuntu/resume-enhancement-tool

# Pull latest code
git pull origin master

# Rebuild and restart
docker-compose build
docker-compose up -d

# Run any new migrations
docker-compose exec backend alembic upgrade head
```

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres resume_enhancement > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U postgres resume_enhancement < backup_20260112.sql
```

---

## Security Checklist

- [ ] Changed SECRET_KEY in .env
- [ ] Changed PostgreSQL password
- [ ] DEBUG=False in production
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Nginx security headers added
- [ ] CORS origins restricted to re-vsion.com
- [ ] Database backups configured

---

## Success Criteria

✅ https://re-vsion.com loads successfully
✅ Can upload resume
✅ Can add job description
✅ Can create enhancement
✅ Can download enhanced resume (MD, DOCX, PDF)
✅ SSL certificate shows as valid (green padlock)
✅ Health check returns healthy
✅ No errors in browser console
✅ No errors in docker-compose logs

---

## Next Steps After Deployment

1. Set up automated backups (daily database dumps)
2. Configure monitoring (uptime monitoring, error alerts)
3. Set up log rotation
4. Configure CDN (optional, for faster loading)
5. Set up staging environment (optional)

---

**Need Help?**
- Check logs: `docker-compose logs -f`
- Verify health: `curl http://localhost:8000/api/health`
- Test nginx: `sudo nginx -t`
- View SSL status: `sudo certbot certificates`
