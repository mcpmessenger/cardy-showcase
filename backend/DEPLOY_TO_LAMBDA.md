## Deploy Backend to AWS Lambda (Serverless Framework)

This guide replaces the Elastic Beanstalk deployment. It packages the FastAPI app with [Mangum](https://github.com/jordaneremieff/mangum) so the API runs behind API Gateway (HTTP API) and scales on demand.

---

### 1. Prerequisites

1. Install the Serverless Framework CLI (requires Node.js):
   ```bash
   npm install -g serverless
   ```
2. Install the Python dependencies locally:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Ensure your AWS credentials are configured (`aws configure`) with permissions for Lambda, API Gateway, CloudFormation, S3, CloudWatch Logs, and IAM role creation.
4. Set the required environment variables in your shell (or in a `.env` file picked up by Serverless):
   ```bash
   export OPENAI_API_KEY=...
   export ELEVEN_LABS_API_KEY=...
   export ELEVEN_LABS_VOICE_ID=...
   export CORS_ORIGINS=https://your-frontend.example.com
    export PRODUCT_CATALOG_URL=https://tubbyai-products-catalog.s3.amazonaws.com/unified-products-master.json
    export PRODUCT_MEDIA_BASE_URL=https://tubbyai-products-catalog.s3.amazonaws.com/
   ```

> **Note:** Lambda cold starts can increase latency for MCP commands. If you rely heavily on MCP tools that need local binaries, ensure they are available in the Lambda package or disable those paths.

---

### 2. Deploy

```bash
cd backend
serverless deploy
```

The command will:

- Create an S3 deployment bucket (if one does not exist)
- Package the FastAPI app (excluding `venv/`, build artifacts, etc.)
- Provision Lambda, API Gateway HTTP API, IAM roles, and CloudWatch log groups
- Output the HTTPS endpoint (copy it for the frontend `VITE_API_BASE_URL`)

To deploy updates after code changes:

```bash
serverless deploy
```

To remove the stack completely:

```bash
serverless remove
```

---

### 3. Configure Frontend

Update the Amplify backend URL:

1. Go to **Amplify Console → App settings → Environment variables**
2. Set `VITE_API_BASE_URL` to the output HTTP API URL from `serverless deploy`
3. Trigger a redeploy (push to `main` or redeploy from the console)

---

### 4. Post-Deployment Checks

1. **Health check:** `GET https://<api-id>.execute-api.us-east-1.amazonaws.com/health`
2. **Voice flow:** Ensure `/api/stt/transcribe` works with your audio workflows
3. **Chat:** Call `/api/chat` and confirm OpenAI + tool calls succeed
4. **Logs:** Use `serverless logs -f api -t` to tail Lambda logs if troubleshooting
5. **Cost monitoring:** The Lambda + API Gateway combo is pay-per-use and should be lower cost than an always-on EC2 environment for sporadic traffic

---

### 5. Decommission Elastic Beanstalk

After confirming the Lambda deployment:

1. Run `eb terminate tubbyai-production` (or delete from the AWS Console) to remove the EB environment
2. Delete the EB application `tubbyai-backend` if no longer needed
3. Remove associated resources created by EB:
   - Load balancer and target group
   - EC2 instance profile/roles (if exclusive to EB)
   - S3 bucket `elasticbeanstalk-<region>-<account>` if not storing anything else
   - CloudWatch log groups for EB
4. Rotate/delete IAM user `tubbyai-eb-user` and its access keys if no longer required

Document the deletions in your ops notes or runbooks to keep an audit trail.

---

### 6. Local Testing

For local development you can still run:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Lambda-specific handler (`app.main.handler`) uses Mangum and does not affect local execution.

---

### 7. Useful Commands

```bash
# Tail Lambda logs
serverless logs -f api -t

# Invoke the function with payload
serverless invoke -f api -d '{"path":"/health","httpMethod":"GET"}'

# Remove all deployed resources (be careful!)
serverless remove
```

---

You are now running the backend on AWS Lambda. Update your runbooks and monitoring to reflect the new architecture.


