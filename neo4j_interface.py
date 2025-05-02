from neo4j import GraphDatabase

class Neo4jInterface:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()
        print("✅ Connected to Neo4j AuraDB.")

    def close(self):
        self.driver.close()

    def create_user(self, name, username, email, password):
        query = """
        CREATE (:User {
            name: $name,
            username: $username,
            email: $email,
            password: $password
        })
        """
        with self.driver.session() as session:
            session.run(query, name=name, username=username, email=email, password=password)

    def user_exists(self, username, email):
        query = """
        MATCH (u:User)
        WHERE u.username = $username OR u.email = $email
        RETURN COUNT(u) AS count
        """
        with self.driver.session() as session:
            result = session.run(query, username=username, email=email)
            return result.single()["count"] > 0

    def validate_login(self, username, password):
        query = """
        MATCH (u:User {username: $username, password: $password})
        RETURN u.name AS name
        """
        with self.driver.session() as session:
            result = session.run(query, username=username, password=password)
            record = result.single()
            return record["name"] if record else None

    def get_user_profile(self, username):
        query = """
        MATCH (u:User {username: $username})
        RETURN u.name AS name, u.username AS username, u.email AS email, u.bio AS bio
        """
        with self.driver.session() as session:
            result = session.run(query, username=username)
            return result.single()

    def update_user_profile(self, username, name=None, bio=None):
        query = """
        MATCH (u:User {username: $username})
        SET u.name = COALESCE($name, u.name),
            u.bio = COALESCE($bio, u.bio)
        RETURN u.name AS name, u.bio AS bio
        """
        with self.driver.session() as session:
            result = session.run(query, username=username, name=name, bio=bio)
            return result.single()

    def follow_user(self, follower_username, followee_username):
        query_check = """
        MATCH (follower:User {username: $follower}), (followee:User {username: $followee})
        OPTIONAL MATCH (follower)-[r:FOLLOWS]->(followee)
        RETURN follower, followee, r IS NOT NULL AS already_follows
        """
        with self.driver.session() as session:
            result = session.run(query_check, follower=follower_username, followee=followee_username)
            record = result.single()

            if not record or record["follower"] is None or record["followee"] is None:
                return "❌ One or both users do not exist."
            if follower_username == followee_username:
                return "❌ You cannot follow yourself."
            if record["already_follows"]:
                return f"❌ You are already following '{followee_username}'."

            # Now create the FOLLOWS relationship
            create_query = """
            MATCH (follower:User {username: $follower}), (followee:User {username: $followee})
            CREATE (follower)-[:FOLLOWS]->(followee)
            """
            session.run(create_query, follower=follower_username, followee=followee_username)
            return f"✅ You are now following '{followee_username}'."

    def unfollow_user(self, follower_username, followee_username):
        query_check = """
        MATCH (follower:User {username: $follower}), (followee:User {username: $followee})
        OPTIONAL MATCH (follower)-[r:FOLLOWS]->(followee)
        RETURN follower, followee, r IS NOT NULL AS already_follows
        """
        with self.driver.session() as session:
            result = session.run(query_check, follower=follower_username, followee=followee_username)
            record = result.single()

            if not record or record["follower"] is None or record["followee"] is None:
                return "❌ One or both users do not exist."
            if follower_username == followee_username:
                return "❌ You cannot unfollow yourself."
            if not record["already_follows"]:
                return f"❌ You are not following '{followee_username}'."

            delete_query = """
            MATCH (follower:User {username: $follower})-[r:FOLLOWS]->(followee:User {username: $followee})
            DELETE r
            """
            session.run(delete_query, follower=follower_username, followee=followee_username)
            return f"✅ You have unfollowed '{followee_username}'."

    def get_following(self, username):
        query = """
        MATCH (:User {username: $username})-[:FOLLOWS]->(other:User)
        RETURN other.username AS username, other.name AS name
        ORDER BY other.username
        """
        with self.driver.session() as session:
            result = session.run(query, username=username)
            return result.data()

    def get_followers(self, username):
        query = """
        MATCH (other:User)-[:FOLLOWS]->(:User {username: $username})
        RETURN other.username AS username, other.name AS name
        ORDER BY other.username
        """
        with self.driver.session() as session:
            result = session.run(query, username=username)
            return result.data()

    def get_mutual_connections(self, username1, username2):
        query = """
        MATCH (u1:User {username: $user1})-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(u2:User {username: $user2})
        RETURN mutual.username AS username, mutual.name AS name
        ORDER BY mutual.username
        """
        with self.driver.session() as session:
            result = session.run(query, user1=username1, user2=username2)
            return result.data()

    def get_friend_recommendations(self, username):
        query = """
        MATCH (me:User {username: $username})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(suggested:User)
        WHERE NOT (me)-[:FOLLOWS]->(suggested) AND suggested.username <> $username
        RETURN suggested.username AS username, suggested.name AS name, COUNT(*) AS score
        ORDER BY score DESC, username
        LIMIT 10
        """
        with self.driver.session() as session:
            result = session.run(query, username=username)
            return result.data()

    def search_users(self, query):
        cypher = """
        MATCH (u:User)
        WHERE toLower(u.username) CONTAINS toLower($q)
           OR toLower(u.name) CONTAINS toLower($q)
        RETURN u.username AS username, u.name AS name
        ORDER BY u.username
        LIMIT 25
        """
        with self.driver.session() as session:
            result = session.run(cypher, q=query)
            return result.data()

    def get_popular_users(self, limit=10):
        query = """
        MATCH (u:User)<-[:FOLLOWS]-(:User)
        RETURN u.username AS username, u.name AS name, COUNT(*) AS followers
        ORDER BY followers DESC, username
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            return result.data()
