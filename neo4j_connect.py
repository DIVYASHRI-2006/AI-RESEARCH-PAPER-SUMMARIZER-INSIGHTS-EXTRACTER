from neo4j import GraphDatabase

# -------------------------------
# 1. Connect to Neo4j
# -------------------------------
driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "SSDP7676")   # change password if needed
)

# -------------------------------
# 2. Dummy Research Data
# -------------------------------
papers = [
    {
        "title": "Credit Card Fraud Detection in e-Commerce: An Outlier Detection Approach",
        "authors": ["Utkarsh Porwal", "Smruthi Mukund"],
        "methods": ["Outlier Detection", "K-Means Clustering", "Anomaly Detection"],
        "domain": "Artificial Intelligence"
    },
    {
        "title": "Can Vision Language Models Learn Intuitive Physics from Interaction?",
        "authors": ["Luca M. Schulze Buschoff", "Konstantinos Voudouris", "Can Demircan", "Eric Schulz"],
        "methods": ["Vision Language Models", "Reinforcement Learning", "Supervised Fine-Tuning"],
        "domain": "Artificial Intelligence"
    },
    {
        "title": "Machine Learning Techniques for Predicting Student Performance",
        "authors": ["Rushali Deshmukh", "Atharva Kulkarni", "Aditya Kumthekar", "Prasanna Kottur", "Soham Raut"],
        "methods": ["Neural Network", "Decision Tree", "Naive Bayes", "K-Nearest Neighbor", "Support Vector Machine"],
        "domain": "Artificial Intelligence"
    },
    {
        "title": "Predictive Modeling of Dropout in MOOCs Using Machine Learning Techniques",
        "authors": ["Kinjal K Patel", "Kiran Amin"],
        "methods": ["Decision Tree", "Random Forest", "Naive Bayes", "AdaBoost", "Extra Trees", "XGBoost", "Multilayer Perceptron"],
        "domain": "Artificial Intelligence"
    },
    {
        "title": "Wide & Deep Learning for Recommender Systems",
        "authors": ["Heng-Tze Cheng", "Levent Koc", "Jeremiah Harmsen", "Hrishi Aradhye", "Glen Anderson", "Greg Corrado"],
        "methods": ["Wide & Deep Learning", "Deep Neural Networks", "Linear Models"],
        "domain": "Artificial Intelligence"
    }
]

# -------------------------------
# 3. Create Graph Function
# -------------------------------
def create_graph(tx, paper):
    title = paper["title"]
    authors = paper["authors"]
    methods = paper["methods"]
    domain = paper["domain"]

    # Create Paper Node
    tx.run(
        """
        MERGE (p:Paper {title:$title})
        """,
        title=title
    )

    # Create Author Relationship
    for author in authors:
        tx.run(
            """
            MERGE (a:Author {name:$author})
            MERGE (p:Paper {title:$title})
            MERGE (a)-[:WROTE]->(p)
            """,
            author=author,
            title=title
        )

    # Create Method Relationship
    for method in methods:
        tx.run(
            """
            MERGE (m:Method {name:$method})
            MERGE (p:Paper {title:$title})
            MERGE (p)-[:USES]->(m)
            """,
            method=method,
            title=title
        )

    # Create Domain Relationship
    tx.run(
        """
        MERGE (d:Domain {name:$domain})
        MERGE (p:Paper {title:$title})
        MERGE (p)-[:BELONGS_TO]->(d)
        """,
        domain=domain,
        title=title
    )

# -------------------------------
# 4. Insert Data into Neo4j
# -------------------------------
with driver.session() as session:
    for paper in papers:
        session.execute_write(create_graph, paper)

print("Knowledge Graph Created!")

# -------------------------------
# 5. Query Graph
# -------------------------------
with driver.session() as session:
    result = session.run(
        """
        MATCH (p:Paper)-[:USES]->(m:Method)
        RETURN p.title AS paper, m.name AS method
        """
    )

    for record in result:
        print(record["paper"], "uses", record["method"])