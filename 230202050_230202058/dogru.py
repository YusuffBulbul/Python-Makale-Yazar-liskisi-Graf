import pandas as pd
import json

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'left')

file_path = "C:\\Users\\yusuf\\OneDrive\\Masaüstü\\230202050_230202058\\PROLAB 3 - GÜNCEL DATASET.xlsx"

try:
    data = pd.read_excel(file_path)

    if data.isnull().values.any():
        data = data.fillna("Boş")

    graph = {}
    node_ids = {}
    current_id = 1

    for _, row in data.iterrows():
        author = row['author_name']
        coauthors = eval(row['coauthors'])
        paper_title = row['paper_title']

        if author not in graph:
            graph[author] = {"id": current_id, "papers": [], "edges": {}}
            node_ids[author] = current_id
            current_id += 1

        if paper_title not in graph[author]["papers"]:
            graph[author]["papers"].append(paper_title)

        for coauthor in coauthors:
            if coauthor not in graph:
                graph[coauthor] = {"id": current_id, "papers": [], "edges": {}}
                node_ids[coauthor] = current_id
                current_id += 1

            if paper_title not in graph[coauthor]["papers"]:
                graph[coauthor]["papers"].append(paper_title)

            if coauthor != author:
                if coauthor not in graph[author]["edges"]:
                    graph[author]["edges"][coauthor] = {"weight": 0, "papers": []}
                if paper_title not in graph[author]["edges"][coauthor]["papers"]:
                    graph[author]["edges"][coauthor]["weight"] += 1
                    graph[author]["edges"][coauthor]["papers"].append(paper_title)

                if author not in graph[coauthor]["edges"]:
                    graph[coauthor]["edges"][author] = {"weight": 0, "papers": []}
                if paper_title not in graph[coauthor]["edges"][author]["papers"]:
                    graph[coauthor]["edges"][author]["weight"] += 1
                    graph[coauthor]["edges"][author]["papers"].append(paper_title)

            for other_coauthor in coauthors:
                if coauthor != other_coauthor:
                    if other_coauthor not in graph[coauthor]["edges"]:
                        graph[coauthor]["edges"][other_coauthor] = {"weight": 0, "papers": []}
                    if paper_title not in graph[coauthor]["edges"][other_coauthor]["papers"]:
                        graph[coauthor]["edges"][other_coauthor]["weight"] += 1
                        graph[coauthor]["edges"][other_coauthor]["papers"].append(paper_title)

    output_file = "graph_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=4)

    print(f"Graf yapısı '{output_file}' dosyasına kaydedildi.")

except Exception as e:
    print(f"Veri çekilirken bir hata oluştu: {e}")
