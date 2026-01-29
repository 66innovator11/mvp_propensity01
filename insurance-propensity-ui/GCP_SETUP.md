# GCP Cloud Storage Setup Guide (Without Firebase)

## Prerequisites
- You already have a GCP bucket named `cust_data_bucket`
- You have access to Google Cloud Console

## Step 1: Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **IAM & Admin** > **Service Accounts**
4. Click **Create Service Account**
5. Fill in the details:
   - Service account name: `insurance-app-uploader`
   - Click **Create and Continue**
6. Grant roles:
   - Add role: **Storage Object Admin** (allows read/write to buckets)
   - Click **Continue** and **Done**

## Step 2: Create and Download Service Account Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** > **Create new key**
4. Choose **JSON** format
5. Click **Create** - the JSON file will download automatically

**Important:** Keep this JSON file safe! It contains credentials to your GCP account.

## Step 3: Set Up Environment Variable

1. Copy the downloaded JSON file to your project folder:
   ```
   cp ~/Downloads/your-service-account-key.json ./insurance-propensity-ui/
   ```

2. Set the environment variable in your system:
   - **Windows (PowerShell):**
     ```powershell
     $env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\your-service-account-key.json"
     ```
   
   - **Mac/Linux:**
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"
     ```

3. Alternatively, create a `.env` file in the project root:
   ```
   GCP_PROJECT_ID=your-project-id
   GCP_BUCKET_NAME=cust_data_bucket
   PORT=3001
   ```

## Step 4: Install Dependencies

Dependencies are already installed. If not, run:
```bash
npm install express cors multer @google-cloud/storage dotenv
```

## Step 5: Start the Backend Server

In a new terminal, run:
```bash
node server.js
```

You should see:
```
Server is running on http://localhost:3001
GCP Project ID: your-project-id
GCP Bucket: cust_data_bucket
```

## Step 6: Start the React App

In another terminal, run:
```bash
npm start
```

## How It Works

1. **Frontend (React):** Collects files from user via UI
2. **Backend (Node.js):** Receives files and uploads to GCP Cloud Storage
3. **GCP Bucket:** Files stored in `gs://cust_data_bucket/uploads/`

## File Upload Flow

```
User uploads file (UI)
        ↓
Sends to http://localhost:3001/api/upload
        ↓
Backend server receives file
        ↓
Backend authenticates with GCP using service account
        ↓
File uploaded to gs://cust_data_bucket/uploads/
        ↓
Success confirmation sent back to UI
```

## View Uploaded Files

- **In Google Cloud Console:**
  1. Go to Cloud Storage > Buckets
  2. Click `cust_data_bucket`
  3. Files will be in `uploads/` folder

- **Via API:**
  ```bash
  curl http://localhost:3001/api/files
  ```

## Troubleshooting

### "Permission denied" error
- Ensure service account has **Storage Object Admin** role
- Verify `GOOGLE_APPLICATION_CREDENTIALS` is set correctly

### "Bucket not found" error
- Verify bucket name in `.env` matches your actual bucket: `cust_data_bucket`
- Ensure bucket exists in Google Cloud Console

### Backend server not running
- Make sure to run `node server.js` before uploading files
- Check that port 3001 is not in use

### "Cannot find module '@google-cloud/storage'"
- Run `npm install @google-cloud/storage`

## Security Note

- **Never commit** the service account JSON file to git
- Add the JSON file to `.gitignore`
- Restrict service account permissions to specific bucket if possible

