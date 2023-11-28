module.exports = {
  apps : [{
    name: 'bacteraify-web',
    script: 'start-app.sh',
    interpreter: '/bin/bash',
    env: {
      NODE_ENV: 'production',
    }
  }],
};
