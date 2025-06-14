# LocalTunnel Setup Guide

## 🚇 Free Tunneling for Your Plasmo MCP Server

LocalTunnel provides a simple, free way to expose your MCP server to the internet without requiring any account signup or credit card.

## 📋 Prerequisites

1. **Node.js** - Required for LocalTunnel
   - Check: `node --version`
   - Install from: https://nodejs.org/

2. **Running MCP Server**
   - Your Plasmo development environment should be working locally
   - MCP server should be running on port 8000

## 🚀 Quick Start

### Option 1: VSCode Tasks (Recommended)

1. Press `Cmd/Ctrl + Shift + P`
2. Type "Tasks: Run Task"
3. Select "Start All + LocalTunnel"

This will:
- Start the secure MCP server
- Start LocalTunnel and expose it publicly
- Display the public URL in the terminal

### Option 2: Command Line

```bash
# Start secure MCP server
python3 secure_mcp_manager.py start

# Start LocalTunnel
python3 localtunnel_manager.py start

# Check status and get URL
python3 localtunnel_manager.py status
```

## 📝 Available Commands

### CLI Commands

```bash
# Start LocalTunnel (auto-installs if needed)
python3 localtunnel_manager.py start

# Stop LocalTunnel
python3 localtunnel_manager.py stop

# Check status and get public URL
python3 localtunnel_manager.py status
```

### VSCode Tasks

- **Start LocalTunnel**: Start tunnel only
- **Stop LocalTunnel**: Stop tunnel
- **Check LocalTunnel Status**: View status and URL
- **Start All + LocalTunnel**: Start everything together

## 🌐 How It Works

1. **LocalTunnel Installation**: Script auto-installs `localtunnel` via npm if needed
2. **Tunnel Creation**: Creates a secure tunnel from your local port 8000 to a public URL
3. **Random URL**: You get a URL like `https://funny-cat-123.loca.lt`
4. **No Limits**: Free, unlimited usage (unlike ngrok's 2-hour limit)

## 🔍 Monitoring

### Check Status
```bash
python3 localtunnel_manager.py status
```

### View Logs
- LocalTunnel logs: `localtunnel.log`
- MCP server logs: `secure_mcp.log`

### Get Public URL
The public URL is saved in `.localtunnel.url` and displayed when you check status.

## 🔐 Security

LocalTunnel exposes your server publicly, so we use the secure MCP server with:
- **API Key Authentication**: Required for all requests
- **Rate Limiting**: 100 requests per minute by default
- **CORS Protection**: Configurable allowed origins

## 🚨 Troubleshooting

### Common Issues

1. **"lt command not found"**
   - Solution: Script will auto-install LocalTunnel
   - Manual: `npm install -g localtunnel`

2. **Node.js not installed**
   - Install from: https://nodejs.org/
   - Verify: `node --version`

3. **Tunnel won't start**
   - Check if port 8000 is available
   - Ensure MCP server is running first
   - Check `localtunnel.log` for errors

4. **Can't access the URL**
   - Verify MCP server is running: `python3 secure_mcp_manager.py status`
   - Check if API key is configured
   - Try accessing: `https://your-url.loca.lt/health`

### Quick Fixes

1. **Restart Everything**
   ```bash
   python3 localtunnel_manager.py stop
   python3 secure_mcp_manager.py restart
   python3 localtunnel_manager.py start
   ```

2. **Get Fresh URL**
   ```bash
   python3 localtunnel_manager.py stop
   python3 localtunnel_manager.py start
   ```

3. **Check Logs**
   ```bash
   tail -f localtunnel.log
   tail -f secure_mcp.log
   ```

## 📊 Usage Examples

### Test Your Tunnel

```bash
# Get your tunnel URL
URL=$(cat .localtunnel.url)

# Test health endpoint
curl $URL/health

# Test with API key
API_KEY=$(grep MCP_API_KEY environment.env | cut -d'=' -f2)
curl -H "Authorization: Bearer $API_KEY" $URL/mcp/tools
```

### Share Your MCP Server

Once running, share your tunnel URL with others:
- **Health Check**: `https://your-url.loca.lt/health`
- **MCP Endpoint**: `https://your-url.loca.lt/mcp`
- **API Key**: Found in `environment.env`

## 🆚 LocalTunnel vs Alternatives

| Feature | LocalTunnel | ngrok (free) | Cloudflare |
|---------|-------------|--------------|------------|
| **Signup Required** | ❌ No | ✅ Yes | ✅ Yes |
| **Time Limits** | ❌ None | ⚠️ 2 hours | ❌ None |
| **Custom Domains** | ❌ No | ❌ No (paid) | ✅ Yes |
| **Rate Limits** | ❌ None | ⚠️ 40/min | ❌ None |
| **Reliability** | ⚠️ Good | ✅ Excellent | ✅ Excellent |
| **Setup Complexity** | ✅ Simple | ✅ Simple | ⚠️ Complex |

## 🎯 Best Practices

1. **Development Only**: LocalTunnel is great for development and testing
2. **Monitor Usage**: Keep an eye on who's accessing your tunnel
3. **Secure Your API**: Always use the API key for external access
4. **Regular Restarts**: Restart tunnel if you notice issues
5. **Log Monitoring**: Check logs regularly for any issues

## 📚 Additional Resources

- [LocalTunnel Documentation](https://localtunnel.github.io/www/)
- [Node.js Installation Guide](https://nodejs.org/en/download/)
- [MCP Server Security Guide](./CLOUDFLARE_TUNNEL_GUIDE.md#security-features) 