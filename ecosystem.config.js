module.exports = {
  apps : [{
    name: 'bacteraify-web',
    script: 'venv/bin/gunicorn',
    args: 'core.wsgi:application --bind 0.0.0.0:8000',
    interpreter: '/bin/bash',
    env: {
      NODE_ENV: 'development',
    },
    env_production: {
      NODE_ENV: 'production',
    }
    pre_start: 'bash build.sh',
    post_restart: 'bash build.sh'
  }],
};
