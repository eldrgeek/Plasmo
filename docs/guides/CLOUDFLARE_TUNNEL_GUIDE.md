# Cloudflare Tunnel Setup Guide

## 🌩️ Complete Guide to Exposing Your Plasmo MCP Server

This guide will help you expose your Plasmo MCP server to the internet using **Cloudflare Tunnel** - a free, secure, and reliable tunneling solution.

## 📋 Prerequisites

1. **Cloudflare Account**
   - Sign up at https://dash.cloudflare.com/sign-up
   - Free tier is sufficient
   - Verify your email address

2. **Running MCP Server**
   - Your Plasmo development environment should be working locally
   - MCP server should be running on port 8000

## 🚀 Quick Start

### Step 1: Initial Setup

```bash
# Run the setup script
python3 cloudflare_tunnel_manager.py setup
```

This will:
1. Install `cloudflared` if needed
2. Open browser for Cloudflare authentication
3. Create and configure your tunnel
4. Generate necessary credentials

### Step 2: Start the Secure MCP Server

```bash
python3 secure_mcp_manager.py start
```

### Step 3: Start the Tunnel

```bash
python3 cloudflare_tunnel_manager.py start
```

Or use VSCode:
1. Press `Cmd/Ctrl + Shift + P`
2. Type "Tasks: Run Task"
3. Select "Start All + Tunnel"

## 🔐 Security Features

1. **API Key Authentication**
   - Automatically generated secure API key
   - Required for all external requests
   - Stored in `environment.env`

2. **Rate Limiting**
   - Default: 100 requests per minute
   - Configurable in `environment.env`

3. **Origin Control**
   - Whitelist allowed origins
   - CORS protection
   - Configurable in `environment.env`

## 🛠️ Configuration

### Environment Variables (`environment.env`)

```env
# MCP Server Security
MCP_API_KEY=           # Auto-generated if not set
MCP_RATE_LIMIT=100    # Requests per minute
MCP_ALLOWED_ORIGINS=  # Comma-separated list

# Cloudflare Tunnel
TUNNEL_NAME=plasmo-mcp-server
CUSTOM_DOMAIN=        # Optional: your custom domain
```

### Custom Domain (Optional)

1. Add your domain to Cloudflare
2. Set `CUSTOM_DOMAIN` in `environment.env`
3. Update tunnel configuration
4. Add DNS record in Cloudflare dashboard

## 📝 Usage

### CLI Commands

```bash
# Tunnel Management
python3 cloudflare_tunnel_manager.py setup   # Initial setup
python3 cloudflare_tunnel_manager.py start   # Start tunnel
python3 cloudflare_tunnel_manager.py stop    # Stop tunnel
python3 cloudflare_tunnel_manager.py status  # Check status

# Secure MCP Server
python3 secure_mcp_manager.py setup    # Initial setup
python3 secure_mcp_manager.py start    # Start server
python3 secure_mcp_manager.py stop     # Stop server
python3 secure_mcp_manager.py status   # Check status
```

### VSCode Tasks

- `Start All + Tunnel`: Start everything
- `Stop All Services`: Stop everything
- `Check Tunnel Status`: View tunnel status
- `Check Services Status`: View all services status

## 🔍 Monitoring

### Logs
- Tunnel logs: `cloudflare_tunnel.log`
- MCP server logs: `secure_mcp.log`

### Metrics
- Available at: `localhost:9091/metrics`
- Includes tunnel performance metrics
- Connection statistics

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Ensure you're logged into Cloudflare
   - Check `~/.cloudflared/cert.pem` exists
   - Try `cloudflared login` manually

2. **Tunnel Won't Start**
   - Check if tunnel already exists
   - Verify credentials file exists
   - Check port availability

3. **Connection Issues**
   - Verify MCP server is running
   - Check firewall settings
   - Verify API key is configured

### Quick Fixes

1. **Reset Tunnel**
   ```bash
   cloudflared tunnel cleanup plasmo-mcp-server
   python3 cloudflare_tunnel_manager.py setup
   ```

2. **Regenerate API Key**
   - Delete `MCP_API_KEY` from `environment.env`
   - Restart secure MCP server

3. **Clear Configuration**
   ```bash
   rm ~/.cloudflared/config.yml
   python3 cloudflare_tunnel_manager.py setup
   ```

## 📚 Additional Resources

- [Cloudflare Tunnels Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Security Best Practices](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/configuration/configuration-file/ingress)
- [Custom Domain Setup](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/routing-to-tunnel/)

## 🔍 Troubleshooting

### Common Issues

#### 1. Tunnel Not Starting

```bash
# Check if cloudflared is installed
which cloudflared

# Check authentication
cloudflared tunnel list

# Check configuration
cat ~/.cloudflared/config.yml
```

#### 2. Services Not Running

```bash
# Check service status
./tunnel_status.sh

# Start services manually
./start_all.sh

# Check specific ports
curl http://localhost:8000/health
curl http://localhost:3001
```

#### 3. Access Denied / 404 Errors

```bash
# Check tunnel configuration
cloudflared tunnel info plasmo-mcp-server

# Verify ingress rules
cloudflared tunnel route dns plasmo-mcp-server mcp.yourdomain.com

# Test local access first
curl http://localhost:8000/health
```

#### 4. Authentication Issues

```bash
# Check API key
cat .mcp_api_key

# Test without auth (if security disabled)
curl https://your-tunnel-url.com/health

# Generate new API key
python3 mcp_server_secure.py --generate-key
```

### Logs and Debugging

```bash
# View tunnel logs
cloudflared tunnel run plasmo-mcp-server --log-level debug

# View MCP server logs
tail -f ~/mcp_server.log

# Check process status
ps aux | grep cloudflared
ps aux | grep python3
```

## 📊 Monitoring

### Cloudflare Dashboard

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Go to **Zero Trust** → **Networks** → **Tunnels**
3. Click on your `plasmo-mcp-server` tunnel
4. View metrics, logs, and configuration

### Local Monitoring

```bash
# Real-time status
watch ./tunnel_status.sh

# Monitor logs
tail -f ~/mcp_server.log

# Check tunnel metrics
cloudflared tunnel info plasmo-mcp-server
```

## 🔒 Advanced Security

### Cloudflare Access (Optional)

For additional security, enable Cloudflare Access:

1. **Zero Trust Dashboard** → **Access** → **Applications**
2. **Add an Application** → **Self-hosted**
3. Configure domain: `mcp.yourdomain.com`
4. Set authentication rules (email, Google OAuth, etc.)

### IP Restrictions

Add IP allowlists in Cloudflare:

1. **Dashboard** → **Security** → **WAF**
2. **Create Rule** → **Custom Rule**
3. Add IP restrictions for your tunnel

### Rate Limiting

Configure advanced rate limiting:

```yaml
# Add to config.yml
ingress:
  - hostname: mcp.yourdomain.com
    service: http://localhost:8000
    originRequest:
      httpHostHeader: localhost:8000
      # Add rate limiting headers
      headers:
        X-Rate-Limit: "100"
```

## 🎯 Integration Examples

### GitHub Actions

```yaml
# .github/workflows/deploy-tunnel.yml
name: Deploy MCP Server
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup tunnel
        run: |
          ./setup_cloudflare_tunnel.sh
          ./start_tunnel.sh
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN ./setup_cloudflare_tunnel.sh
CMD ["./start_tunnel.sh"]
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: mcp-server
        image: your-image
        command: ["./start_tunnel.sh"]
        env:
        - name: MCP_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: api-key
```

## 📚 Additional Resources

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Zero Trust Dashboard](https://one.dash.cloudflare.com/)
- [Cloudflare Community](https://community.cloudflare.com/)

## ❓ FAQ

**Q: Is Cloudflare Tunnel really free?**
A: Yes! Basic tunneling is completely free with unlimited bandwidth.

**Q: Can I use multiple domains?**
A: Yes, you can route multiple subdomains to different services.

**Q: What happens if my local server goes down?**
A: Cloudflare will return a 502 error until your local server restarts.

**Q: Can I restrict access to specific IPs?**
A: Yes, use Cloudflare's firewall rules or Access policies.

**Q: How do I update the tunnel configuration?**
A: Edit `~/.cloudflared/config.yml` and restart the tunnel.

---

**💡 Pro Tip**: Start with the auto-generated URLs for testing, then move to custom domains for production use. The tunnel will keep running even if your local network IP changes! 