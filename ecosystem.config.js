module.exports = {
  apps: [
    {
      name: 'api_demo',
      script: '/lipidmaps/lipidmaps_py/venv/bin/python',
      args: '-m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --server.enableCORS false',
      cwd: '/lipidmaps/lipidmaps_py',
      autorestart: true,
      restart_delay: 5000,
      watch: false,
      max_memory_restart: '300M',
      env: {
        PATH: '/lipidmaps/lipidmaps_py/venv/bin:$PATH'
      }
    }
  ]
};
