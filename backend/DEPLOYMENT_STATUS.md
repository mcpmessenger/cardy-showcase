# 🚀 Backend Deployment Status

## ✅ Previous EB Deployment (Legacy)
1. Created IAM user `tubbyai-eb-user` with EB permissions
2. Configured AWS credentials
3. Initialized EB application: `tubbyai-backend`
4. Created EB environment: `tubbyai-production`
5. Environment URL: `tubbyai-production.eba-pcqnhqe4.us-east-1.elasticbeanstalk.com`

> The Elastic Beanstalk deployment is now **deprecated**. We are migrating the backend to AWS Lambda via the Serverless Framework. Proceed to tear down the EB environment once the Lambda stack is verified.

---

## 🆕 Target Deployment: AWS Lambda + API Gateway

- Deployment guide: `backend/DEPLOY_TO_LAMBDA.md`
- Lambda handler: `app.main.handler` (via Mangum)
- Serverless config: `backend/serverless.yml`
- Environment variables: managed through Lambda/Serverless (`OPENAI_API_KEY`, `ELEVEN_LABS_API_KEY`, `ELEVEN_LABS_VOICE_ID`, `CORS_ORIGINS`)

### Next Steps
1. Run `serverless deploy` from `backend/` to create the Lambda/API Gateway stack
2. Update Amplify `VITE_API_BASE_URL` with the new API Gateway URL
3. Validate `/health`, `/api/chat`, `/api/stt/transcribe`, and `/api/tts/synthesize`
4. Terminate the EB environment (`eb terminate tubbyai-production`) and delete related AWS resources after confirming Lambda is stable
5. Rotate/delete the `tubbyai-eb-user` IAM credentials if no longer required

---

## 📓 Notes
- CloudWatch logs for Lambda can be tailed with `serverless logs -f api -t`
- Use `serverless remove` to destroy the Lambda stack if necessary
- Document any AWS resource deletions for audit purposes
