# Troubleshooting Guide for npm run dev

## Issue: npm run dev failing or hanging

### Solution: Run servers in separate terminals

The issue with `npm run dev` might be that concurrently has trouble with certain terminal setups. Instead, run the servers separately:

### Method 1: Recommended (Two Separate Terminals)

**Terminal 1 - Start Backend Server:**
```bash
cd insurance-propensity-ui
npm run server
```

You should see:
```
✓ GCP Storage initialized successfully
Server is running on http://localhost:3001
GCP Project ID: propensity-to-buy-b7bde
GCP Bucket: cust_data_bucket
```

**Terminal 2 - Start React App:**
```bash
cd insurance-propensity-ui
npm start
```

This will open http://localhost:3000 in your browser.

### Method 2: If you want to use npm run dev

Run this in your terminal:
```bash
npm run dev:full
```

This uses concurrently to run both servers at once.

## Troubleshooting Server Issues

### Issue: "✗ Failed to initialize GCP Storage"

**Solution:** Make sure the service account JSON file exists:
```bash
# Check if the file exists
ls propensity-to-buy-b7bde-d603e877bf61.json
```

If it doesn't exist:
1. Download it from Google Cloud Console
2. Place it in the `insurance-propensity-ui` folder

### Issue: "Port 3001 already in use"

If port 3001 is already in use:
```bash
# Find process using port 3001 (Windows)
netstat -ano | findstr :3001

# Kill the process
taskkill /PID <PID> /F

# Or change the port in .env
PORT=3002
```

### Issue: "CORS error" when uploading

Make sure both servers are running:
- Backend: http://localhost:3001
- Frontend: http://localhost:3000

### Issue: Files not uploading to GCP

1. Check that service account has "Storage Object Admin" role in GCP
2. Verify bucket name is `cust_data_bucket` in .env
3. Check browser console (F12) for error messages
4. Check server logs for upload errors

## Recommended Workflow

1. **Terminal 1:** Start backend
   ```bash
   npm run server
   ```

2. **Terminal 2:** Start React app
   ```bash
   npm start
   ```

3. Open http://localhost:3000 in browser

4. Upload files - they should appear in your GCP bucket

## Testing

### Check if backend is running:
```bash
curl http://localhost:3001/api/health
```

Should return: `{"status":"Server is running"}`

### List uploaded files:
```bash
curl http://localhost:3001/api/files
```

Should return: `{"success":true,"files":[...]}`
