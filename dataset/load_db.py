import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm
from faker import Faker

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD


fake = Faker()

# Load full CSVs
users_df = pd.read_csv("target.csv")
edges_df = pd.read_csv("edges.csv")

# Step 1: Randomly sample 5000 edges
sampled_edges = edges_df.sample(n=5000, random_state=42)

# Step 2: Get all user IDs involved in those edges
valid_ids = set(sampled_edges['id_1']).union(set(sampled_edges['id_2']))

# Step 3: Filter users to only those in the edge set
users_df = users_df[users_df['id'].isin(valid_ids)]
id_to_name = dict(zip(users_df['id'], users_df['name']))

# Step 4: Map edge IDs to usernames
sampled_edges['from_user'] = sampled_edges['id_1'].map(id_to_name)
sampled_edges['to_user'] = sampled_edges['id_2'].map(id_to_name)

# Drop any edge rows with missing user mappings (shouldn't happen, but safe)
sampled_edges = sampled_edges.dropna(subset=['from_user', 'to_user'])

# Final user + edge lists
usernames = users_df['name'].tolist()
edges = list(zip(sampled_edges['from_user'], sampled_edges['to_user']))

print(f"✅ Preparing to create {len(usernames)} users and {len(edges)} relationships.")

# Neo4j driver setup
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def create_users(tx, users):
    for user in users:
        name = fake.name()
        email = f"{user}@gmail.com"
        password = user
        bio = fake.sentence()
        tx.run("""
        MERGE (:User {
            username: $username,
            name: $name,
            email: $email,
            password: $password,
            bio: $bio
        })
        """, username=user, name=name, email=email, password=password, bio=bio)

def create_follows(tx, edges):
    for u1, u2 in edges:
        if u1 != u2:
            tx.run("""
            MATCH (a:User {username: $from_user}), (b:User {username: $to_user})
            MERGE (a)-[:FOLLOWS]->(b)
            """, from_user=u1, to_user=u2)

def populate():
    with driver.session() as session:
        print(f"🔵 Creating {len(usernames)} users...")
        for i in tqdm(range(0, len(usernames), 500)):
            session.write_transaction(create_users, usernames[i:i+500])

        print(f"🔗 Creating {len(edges)} FOLLOWS relationships...")
        for i in tqdm(range(0, len(edges), 500)):
            session.write_transaction(create_follows, edges[i:i+500])

    print("✅ Done seeding Neo4j.")

if __name__ == "__main__":
    populate()
    driver.close()
