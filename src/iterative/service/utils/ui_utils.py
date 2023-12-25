import os

# usage is like
# # Assuming the script is run from the 'turbo' directory
# create_ui_directories('.')

def create_ui_directories(base_path):
    service_path = os.path.join(base_path, "colorfull", "service")

    # Check if the path exists
    if not os.path.exists(service_path):
        print(f"Path not found: {service_path}")
        return

    # Iterate through directories in the service path
    for service in os.listdir(service_path):
        service_dir = os.path.join(service_path, service)
        
        # Check if it's a directory and has a '.iterave' folder
        if os.path.isdir(service_dir) and '.iterave' in os.listdir(service_dir):
            ui_path = os.path.join(service_dir, 'ui')
            
            # Create the 'ui' directory if it doesn't exist
            if not os.path.exists(ui_path):
                os.makedirs(ui_path)
                print(f"Created UI directory: {ui_path}")
            else:
                print(f"UI directory already exists: {ui_path}")


