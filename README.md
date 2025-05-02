# 📘 Social Network CLI App (Neo4j + Python)

Command-line social networking application built with Python and Neo4j.  


## 📂 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/bhprtk/nosql_project.git
cd nosql_project
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

---

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

### 4. Add Your Neo4j Credentials

1. Create `config.py` and add your Neo4j AuraDB credentials:

```python
NEO4J_URI = "neo4j+s://<your-instance>.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "<your-password>"
```

> 💡 You can find your AuraDB credentials under "Connect > Connection URI" in the Neo4j Aura dashboard.

---

### 5. Load the Dataset (Optional)

To seed the database with users and follower relationships:

```bash
cd dataset
python load_db.py
```

- Loads 5,000 `FOLLOWS` relationships
- Includes realistic fake names, bios, and emails for all involved users

---

### 6. Run the CLI App

```bash
python main.py
```

---

## 📊 Dataset Overview

- **Source:** [GitHub Social Network (Kaggle)](https://www.kaggle.com/datasets/kausthubkannan/github-social-network)
- `target.csv`: contains users (ID, username)
- `edges.csv`: follower connections (`id_1` follows `id_2`)
- Used in `dataset/load_db.py` to upload to Neo4j


### 🔧 Dataset Manipulation for Neo4j
To prepare the dataset for uploading into Neo4j:
- A random sample of 5,000 edges was selected from edges.csv.
- All unique user IDs involved in those 5,000 edges were extracted.
- The target.csv file was then filtered to include only the users corresponding to those IDs.

For each user node, the following properties were assigned:
- username: taken from the name column
- name: a randomly generated full name using faker
- email: formatted as username@gmail.com
- password: identical to the username
- bio: erandomly generated sentence using faker

A total of 5,000 FOLLOWS relationships were created between the users using Cypher queries.

---

## 🔒 Security Notes

- `config.py` is **ignored by Git** via `.gitignore`
- You need to create your own `config.py` using their Neo4j credentials
- Never push secrets or credentials to GitHub

---

