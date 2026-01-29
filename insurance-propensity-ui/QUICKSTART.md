# Quick Start Guide

## ✓ Your Setup is Ready!

Everything is configured correctly. Your backend server is running and connected to GCP Cloud Storage.

## How to Run the Application

### Step 1: Start the Backend Server

Open a terminal in the project folder and run:
```bash
npm run server
```

You should see:
```
✓ GCP Storage initialized successfully
Server is running on http://localhost:3001
GCP Project ID: propensity-to-buy-b7bde
GCP Bucket: cust_data_bucket
```

### Step 2: Start the React Application (in a new terminal)

```bash
npm start
```

This will automatically open http://localhost:3000 in your browser.

### Step 3: Upload Files

1. Select files from your computer (up to 4 files)
2. Click "Upload Files"
3. Files will be uploaded to your GCP bucket: `cust_data_bucket`
4. Continue with reviewing data and adding predictors

## What Happens When You Upload

1. **Frontend** collects files from you
2. **Frontend** sends files to backend at http://localhost:3001/api/upload
3. **Backend** receives files and uploads them to GCP
4. **Files** are stored in: `gs://cust_data_bucket/uploads/timestamp_filename`
5. **Success** message shown in your browser

## File Locations

- **In Google Cloud Console:**
  - Go to Cloud Storage > Buckets > `cust_data_bucket` > `uploads` folder

- **Via API:**
  ```bash
  curl http://localhost:3001/api/files
  ```

## Troubleshooting

If you encounter issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Backend won't start | Make sure service account JSON exists in project folder |
| Upload fails | Check both servers are running (port 3000 and 3001) |
| Files not in GCP | Verify bucket name is `cust_data_bucket` in .env |
| Port already in use | Change PORT in .env or kill existing process |

Enjoy! 🎉
