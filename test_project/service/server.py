from iterative import prep_app as populate_app_with_routers
from iterative import web_app as app

populate_app_with_routers()

# Main entry point
if __name__ == "__main__":
    import uvicorn

    # Determine host and port based on environment
    host = "127.0.0.1" 
    port = 8002

    # Run the server
    uvicorn.run(app, host=host, port=port)