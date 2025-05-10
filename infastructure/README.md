# Deployment with Render CLI

This directory contains deployment configurations for managing the application on Render.

## Prerequisites

1. Install Render CLI:

   ```bash
   curl -o render https://render.com/download/cli/linux/latest
   chmod +x render
   sudo mv render /usr/local/bin/
   ```

2. Login to Render:

   ```bash
   render login
   ```

## Deployment

1. Make sure you're logged in to Render:

   ```bash
   render whoami
   ```

2. Deploy using the script:

   ```bash
   ./deploy.sh
   ```

   Or manually:

   ```bash
   render deploy
   ```

## Infrastructure Components

- PostgreSQL Database
  - Free tier
  - Oregon region
  - Automatic backups

- Web Service
  - Free tier
  - Oregon region
  - Connected to PostgreSQL database
  - Environment variables configured automatically

## Environment Variables

Make sure to set these environment variables in your Render dashboard:

- `DATABASE_URL`: Your PostgreSQL connection string
- `FLASK_ENV`: Set to "production"

## Maintenance

To update your application:

1. Push changes to your repository
2. Run the deployment script or use `render deploy`

To view logs:

```bash
render logs
```

## Security Notes

- Keep your Render account credentials secure
- Review deployment logs for any issues
- Monitor your application's performance in the Render dashboard
