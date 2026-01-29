module.exports = {
  apps: [
    {
      name: 'streamlit-api_demo',
      script: '/lipidmaps/lipidmaps_py/venv/bin/python',
      args: '-m streamlit run scripts/streamlit_demo.py --server.address 127.0.0.1 --server.port 8501 --server.baseUrlPath /api_demo --server.headless true --server.enableCORS false --server.enableXsrfProtection false',
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
