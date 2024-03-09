
def global_data(request):
    # Define the navigation items
    nav_items = [
        {'name': 'Home', 'url_name': 'home', 'icon': 'home'},
        {'name': 'Login', 'url_name': 'login', 'icon': 'login'},
        {'name': 'Sign Up', 'url_name': 'signup', 'icon': 'passkey'},
        {'name': 'Tasks', 'url_name': 'tasks', 'icon': 'task'},
        {'name': 'Projects', 'url_name': 'projects', 'icon': 'view_list'},
        {'name': 'Organizations', 'url_name': 'organizations', 'icon': 'corporate_fare'},
        {'name': 'Notifications', 'url_name': 'notifications', 'icon': 'notifications'},        
    ]


    # Check user authentication and adjust nav_items accordingly
    if request.user.is_authenticated:
        # Filter out 'Login' and 'Sign Up' for authenticated users
        nav_items = [item for item in nav_items if item['name'] not in ['Login', 'Sign Up']]
    else:
        # Filter out items not relevant for unauthenticated users
        nav_items = [item for item in nav_items if item['name'] in ['Home', 'Login', 'Sign Up']]

    return {'nav_items': nav_items}
