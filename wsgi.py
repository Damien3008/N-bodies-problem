from src.visualization.dashboard import NBodyDashboard

# Create the dashboard application
dashboard = NBodyDashboard()
# Get the underlying Flask server
application = dashboard.app.server

if __name__ == "__main__":
    dashboard.run_server(
        host='0.0.0.0',
        port=8050,
        debug=False
    ) 