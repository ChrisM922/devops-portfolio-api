# Deployment with Render

This directory contains deployment configurations for the application on Render.

## Setup

1. Create a new Web Service on Render:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - Name: todo-app
     - Environment: Python
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app.main:app`

2. Create a PostgreSQL database:
   - Click "New +" and select "PostgreSQL"
   - Name: todo-db
   - Database: todo
   - User: todo_user
   - Plan: Free

3. Configure environment variables in Render:
   - `FLASK_ENV`: production
   - `DATABASE_URL`: (will be provided by Render)

4. Get the deploy hook:
   - Go to your web service settings
   - Find the "Deploy Hook" section
   - Copy the deploy hook URL

5. Add the deploy hook to GitHub Secrets:
   - Go to your GitHub repository
   - Go to Settings > Secrets and variables > Actions
   - Add a new secret named `RENDER_DEPLOY_HOOK` with your deploy hook URL

## Deployment

The application will automatically deploy when:

1. You push changes to the main branch
2. The GitHub Actions workflow runs successfully
3. The deploy hook is triggered

## Monitoring

Monitor your application through the Render dashboard:

- View logs
- Check performance metrics
- Monitor database status
- View deployment history

## Security Notes

- Keep your deploy hook URL secure
- Monitor your application's performance
- Review deployment logs for any issues
