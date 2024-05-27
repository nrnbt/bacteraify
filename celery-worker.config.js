module.exports = {
  apps : [{
    name: 'celery-worker',
    script: 'celery-worker.sh',
    max_restarts: 5,
    interpreter: '/bin/bash',
    env: {
      NODE_ENV: 'production',
    }
  }],
};
