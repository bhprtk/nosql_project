def get_user_input():
    print("=== User Registration ===")
    name = input("Name: ")
    username = input("Username: ")
    email = input("Email: ")
    password = input("Password: ")
    return name, username, email, password

def get_login_input():
    print("=== 🔐 User Login ===")
    username = input("Username: ")
    password = input("Password: ")
    return username, password