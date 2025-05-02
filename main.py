from neo4j_interface import Neo4jInterface
from user_service import UserService
from cli import get_user_input, get_login_input
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD


def main():
    try:
        db = Neo4jInterface(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        user_service = UserService(db)

        while True:
            print("\n👋 Welcome to the Social Network CLI")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose an option (1, 2, or 3): ").strip()

            if choice == "1":
                name, uname, email, pw = get_user_input()
                user_service.register_user(name, uname, email, pw)

            elif choice == "2":
                uname, pw = get_login_input()
                user_name = user_service.db.validate_login(uname, pw)
                if user_name:
                    print(f"\n✅ Welcome, {user_name}!")

                    # In-app loop after login
                    while True:
                        print("\nWhat would you like to do?")
                        print("1. View Profile")
                        print("2. Update Profile")
                        print("3. Logout")
                        print("4. Follow a User")
                        print("5. Unfollow a User")
                        print("6. View Connections")
                        print("7. View Mutual Connections")
                        print("8. Get Friend Recommendations")
                        print("9. Search Users")
                        print("10. Explore Popular Users")

                        user_choice = input("Choose an option: ").strip()
                        
                        if user_choice == "1":
                            user_service.view_profile(uname)
                        elif user_choice == "2":
                            user_service.update_profile(uname)
                        elif user_choice == "3":
                            print("👋 Logged out.")
                            break
                        elif user_choice == "4":
                            user_service.follow_user(uname)
                        elif user_choice == "5":
                            user_service.unfollow_user(uname)
                        elif user_choice == "6":
                            user_service.view_connections(uname)
                        elif user_choice == "7":
                            user_service.view_mutual_connections(uname)
                        elif user_choice == "8":
                            user_service.show_friend_recommendations(uname)
                        elif user_choice == "9":
                            user_service.search_users()
                        elif user_choice == "10":
                            user_service.explore_popular_users()
                        else:
                            print("❌ Invalid option.")

                else:
                    print("❌ Invalid username or password.")

            elif choice == "3":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please try again.")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        db.close()

if __name__ == "__main__":
    main()
