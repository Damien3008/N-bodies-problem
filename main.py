from src.visualization.dashboard import NBodyDashboard

def main():
    # Create the dashboard
    dashboard = NBodyDashboard()
    
    # Run the dashboard in production mode
    dashboard.run_server(
        host='0.0.0.0',  # Allow external connections
        port=8050,       # Specify port
        debug=False,     # Disable debug mode
        dev_tools_hot_reload=False  # Disable hot reloading
    )

if __name__ == "__main__":
    main() 