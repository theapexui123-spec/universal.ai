# Deployment Guide

This guide provides instructions for deploying the AI Course Platform to various hosting platforms.

## 🚀 Quick Deployment Options

### 1. Heroku Deployment

#### Prerequisites
- Heroku account
- Heroku CLI installed
- Git repository

#### Steps
```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Open app
heroku open
```

### 2. DigitalOcean App Platform

#### Steps
1. Connect your GitHub repository
2. Choose Python as the environment
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `gunicorn course_platform.wsgi:application`
5. Add environment variables
6. Deploy

### 3. AWS Elastic Beanstalk

#### Prerequisites
- AWS account
- AWS CLI installed

#### Steps
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init

# Create environment
eb create production

# Deploy
eb deploy

# Open application
eb open
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml ai-course-platform

# Scale services
docker service scale ai-course-platform_web=3
```

## ☁️ Cloud Platform Deployment

### Google Cloud Platform (GCP)

#### Using App Engine
1. Create `app.yaml` file:
```yaml
runtime: python311
entrypoint: gunicorn -b :$PORT course_platform.wsgi:application

env_variables:
  DJANGO_SETTINGS_MODULE: course_platform.settings
  DEBUG: "False"
```

2. Deploy:
```bash
gcloud app deploy
```

#### Using Cloud Run
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-course-platform

# Deploy to Cloud Run
gcloud run deploy ai-course-platform \
  --image gcr.io/PROJECT_ID/ai-course-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Microsoft Azure

#### Using Azure App Service
1. Create App Service in Azure Portal
2. Configure deployment from GitHub
3. Set environment variables
4. Deploy automatically on push

#### Using Azure Container Instances
```bash
# Build and push to Azure Container Registry
az acr build --registry yourregistry --image ai-course-platform .

# Deploy to Container Instances
az container create \
  --resource-group your-rg \
  --name ai-course-platform \
  --image yourregistry.azurecr.io/ai-course-platform:latest \
  --ports 8000
```

## 🔧 Production Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Email
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True

# Static Files
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# Security
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
```

### Database Configuration

#### PostgreSQL (Recommended)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

#### MySQL
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}
```

### Static Files Configuration

```python
# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 🔒 Security Configuration

### SSL/HTTPS Setup

#### Using Let's Encrypt
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Using Cloudflare
1. Add domain to Cloudflare
2. Update nameservers
3. Enable SSL/TLS encryption
4. Configure security headers

### Security Headers

Add to your web server configuration:

```nginx
# Nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

## 📊 Monitoring and Logging

### Application Monitoring

#### Using Sentry
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

#### Using New Relic
```python
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
```

### Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

## 🔄 Backup and Recovery

### Database Backup

#### PostgreSQL
```bash
# Create backup
pg_dump -h host -U user -d database > backup.sql

# Restore backup
psql -h host -U user -d database < backup.sql
```

#### Automated Backups
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$DATE.sql
gzip backup_$DATE.sql
aws s3 cp backup_$DATE.sql.gz s3://your-bucket/backups/
```

### File Backup

```bash
# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Upload to cloud storage
aws s3 cp media_backup_$(date +%Y%m%d).tar.gz s3://your-bucket/backups/
```

## 🚀 Performance Optimization

### Caching

#### Redis Configuration
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

#### Database Query Optimization
```python
# Use select_related for foreign keys
courses = Course.objects.select_related('instructor', 'category').all()

# Use prefetch_related for many-to-many
courses = Course.objects.prefetch_related('lessons', 'reviews').all()
```

### CDN Configuration

#### Using AWS CloudFront
1. Create CloudFront distribution
2. Set origin to your application
3. Configure cache behaviors
4. Update static files URLs

#### Using Cloudflare
1. Enable Cloudflare CDN
2. Configure cache rules
3. Enable minification
4. Set up page rules

## 🔧 Troubleshooting

### Common Issues

#### Database Connection
```bash
# Check database connectivity
python manage.py dbshell

# Test database connection
python manage.py check --database default
```

#### Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check static files configuration
python manage.py findstatic admin/css/base.css
```

#### Memory Issues
```bash
# Monitor memory usage
htop

# Check application logs
tail -f /app/logs/django.log
```

### Performance Monitoring

#### Using Django Debug Toolbar (Development)
```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

#### Using Django Silk (Production)
```python
INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
```

## 📞 Support

For deployment issues:
- Check application logs
- Review server error logs
- Test database connectivity
- Verify environment variables
- Contact support team

---

*This deployment guide covers the most common deployment scenarios. For specific platform requirements, refer to the platform's official documentation.*
