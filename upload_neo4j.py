import json
import os
from neo4j import GraphDatabase

# 1. Connect to Neo4j
driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "SSDP7676")
)

# 2. Load JSON Data
with open("arxiv_papers.json", "r", encoding="utf-8") as f:
    arxiv_data = json.load(f)

with open("pubmed_papers.json", "r", encoding="utf-8") as f:
    pubmed_data = json.load(f)

data = arxiv_data + pubmed_data

# 3. Load Parsed JSON Files
folder_path = "parsed_output"

for file in os.listdir(folder_path):
    if file.endswith(".json"):

        with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
            parsed = json.load(f)

            paper = {
                "title": parsed.get("metadata", {}).get("title"),
                "authors": parsed.get("metadata", {}).get("authors", []),
                "insight": parsed.get("insight", {})
            }

            data.append(paper)

# 4. Function to Insert Data into Neo4j
def create_graph(tx, paper):

    title = paper.get("title")

    # Create Paper Node
    tx.run(
        """
        MERGE (p:Paper {title:$title})
        """,
        title=title
    )

    # Add Authors
    authors = paper.get("authors", [])

    if isinstance(authors, str):
        authors = authors.split(",")

    for author in authors:
        tx.run(
            """
            MERGE (a:Author {name:$author})
            MERGE (p:Paper {title:$title})
            MERGE (a)-[:WROTE]->(p)
            """,
            author=author.strip(),
            title=title
        )

    # Add Insights
    insight = paper.get("insight", {})

    if insight:

        # Domains
        for domain in insight.get("domain", []):
            tx.run(
                """
                MERGE (d:Domain {name:$domain})
                MERGE (p:Paper {title:$title})
                MERGE (p)-[:BELONGS_TO]->(d)
                """,
                domain=domain,
                title=title
            )

        # Methods
        for method in insight.get("methods", []):
            tx.run(
                """
                MERGE (m:Method {name:$method})
                MERGE (p:Paper {title:$title})
                MERGE (p)-[:USES]->(m)
                """,
                method=method,
                title=title
            )

        # Metrics
        for metric in insight.get("metrics", []):
            tx.run(
                """
                MERGE (m:Metric {name:$metric})
                MERGE (p:Paper {title:$title})
                MERGE (p)-[:EVALUATED_BY]->(m)
                """,
                metric=metric,
                title=title
            )

# 5. Insert Data into Neo4j
with driver.session() as session:
    for paper in data:
        session.execute_write(create_graph, paper)

print("Knowledge Graph Created Successfully!")