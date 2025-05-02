from neo4j_interface import Neo4jInterface

class UserService:
    def __init__(self, db: Neo4jInterface):
        self.db = db

    def register_user(self, name, username, email, password):
        if self.db.user_exists(username, email):
            print("❌ Username or email already exists. Try logging in or use different credentials.")
        else:
            self.db.create_user(name, username, email, password)
            print(f"✅ User '{username}' registered successfully!")

    def login_user(self, username, password):
        name = self.db.validate_login(username, password)
        if name:
            print(f"✅ Welcome back, {name}!")
        else:
            print("❌ Invalid username or password.")

    def view_profile(self, username):
        profile = self.db.get_user_profile(username)
        if profile:
            print("\n👤 Your Profile:")
            print(f"Name     : {profile['name']}")
            print(f"Username : {profile['username']}")
            print(f"Email    : {profile['email']}")
            print(f"Bio      : {profile['bio'] or 'N/A'}")
        else:
            print("❌ Profile not found.")

    def update_profile(self, username):
        print("\n🔧 Update Profile (press Enter to skip any field)")
        new_name = input("New name: ").strip()
        new_bio = input("New bio: ").strip()
        name = new_name if new_name else None
        bio = new_bio if new_bio else None
        updated = self.db.update_user_profile(username, name=name, bio=bio)
        print(f"✅ Updated Profile: Name = {updated['name']}, Bio = {updated['bio']}")

    def follow_user(self, current_username):
        print("\n👥 Follow a User")
        target = input("Enter the username of the person you want to follow: ").strip()
        if not target:
            print("❌ Username cannot be empty.")
            return
        result = self.db.follow_user(current_username, target)
        print(result)

    def unfollow_user(self, current_username):
        print("\n👥 Unfollow a User")
        target = input("Enter the username of the person you want to unfollow: ").strip()
        if not target:
            print("❌ Username cannot be empty.")
            return
        result = self.db.unfollow_user(current_username, target)
        print(result)

    def view_connections(self, username):
        following = self.db.get_following(username)
        followers = self.db.get_followers(username)

        print("\n👥 You are following:")
        if following:
            for user in following:
                print(f" - {user['username']} ({user['name']})")
        else:
            print(" (no one)")

        print("\n👥 People following you:")
        if followers:
            for user in followers:
                print(f" - {user['username']} ({user['name']})")
        else:
            print(" (no one)")

    def view_mutual_connections(self, username):
        print("\n🔍 View Mutual Connections")
        other_user = input("Enter the username to compare with: ").strip()
        if not other_user:
            print("❌ Username cannot be empty.")
            return
        if other_user == username:
            print("❌ You can't compare with yourself.")
            return

        mutuals = self.db.get_mutual_connections(username, other_user)
        if mutuals:
            print(f"\n🤝 Mutual connections between you and '{other_user}':")
            for user in mutuals:
                print(f" - {user['username']} ({user['name']})")
        else:
            print(f"😕 No mutual connections with '{other_user}'.")

    def show_friend_recommendations(self, username):
        print("\n🤖 Friend Recommendations (based on mutual follows):")
        recommendations = self.db.get_friend_recommendations(username)
        if recommendations:
            for user in recommendations:
                print(f" - {user['username']} ({user['name']}) — followed by {user['score']} of your connections")
        else:
            print("😕 No recommendations found right now.")

    def search_users(self):
        print("\n🔍 Search for Users")
        query = input("Enter a name or username to search: ").strip()
        if not query:
            print("❌ Search query cannot be empty.")
            return

        matches = self.db.search_users(query)
        if matches:
            print(f"\n🔎 Found {len(matches)} user(s):")
            for user in matches:
                print(f" - {user['username']} ({user['name']})")
        else:
            print("😕 No users found.")

    def explore_popular_users(self):
        print("\n🌟 Most-Followed Users:")
        popular = self.db.get_popular_users()
        if popular:
            for user in popular:
                print(f" - {user['username']} ({user['name']}) — {user['followers']} followers")
        else:
            print("No popular users found.")
