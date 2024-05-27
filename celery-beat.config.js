module.exports = {
  apps : [{
    name: 'celery-beat',
    script: 'celery-beat.sh',
    max_restarts: 5,
    interpreter: '/bin/bash',
    env: {
      NODE_ENV: 'production',
    }
  }],
};
