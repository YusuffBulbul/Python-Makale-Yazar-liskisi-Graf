from flask import Flask, jsonify, render_template, request
import json

app = Flask(__name__)

def json_yukle(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        graph_data = json.load(f)
    return graph_data

input_file = "graph_data.json"  
graph_data = json_yukle(input_file)

class Queue:
    def __init__(self):
        self.items = []
        self.log = []

    def enqueue(self, item):
        self.items.append(item)
        self.log.append({"action": "enqueue", "item": item})

    def dequeue(self):
        if not self.is_empty():
            removed_item = self.items.pop(0)
            self.log.append({"action": "dequeue", "item": removed_item})
            return removed_item
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def get_items(self):
        return self.items

    def get_log(self):
        return self.log

def dugum_id_bul(graph, target_id):
    for node, data in graph.items():
        if str(data["id"]) == str(target_id):
            return node
    return None

def kuyrukta_isbirlikci_sirala2(graph, author_node):
    queue = Queue()
    coauthors = graph[author_node]["edges"]

    for coauthor, edge_data in coauthors.items():
        weight = len(graph[coauthor]["papers"])
        queue.enqueue((coauthor, weight))

    log = queue.get_log()

    sorted_items = []
    while not queue.is_empty():
        max_item = max(queue.get_items(), key=lambda x: x[1])
        queue.get_items().remove(max_item)
        queue.log.append({"action": "dequeue", "item": max_item})
        sorted_items.append(max_item)
        queue.log.append({"action": "enqueue_sorted", "item": max_item})

    queue.log.append({"action": "sorted", "item": sorted_items})
    return sorted_items, queue.get_log()

def toplam_isbirlikci_hesapla5(graph, author_node):
    collaborators = len(graph[author_node]["edges"])
    return collaborators

def en_cok_isbirlik_yapan6(graph):
    max_collabs = 0
    most_collaborative = None
    for author, data in graph.items():
        collab_count = len(data["edges"])
        if collab_count > max_collabs:
            max_collabs = collab_count
            most_collaborative = {"author": author, "collaborations": collab_count}
    return most_collaborative

def dfs_uzun_yol7(graph, start_node):
    def dfs(node, visited, path):
        visited.add(node)
        path.append(node)
        longest = list(path)
        for neighbor in graph[node]["edges"]:
            if neighbor not in visited:
                current_path = dfs(neighbor, visited, path)
                if len(current_path) > len(longest):
                    longest = current_path
        path.pop()
        visited.remove(node)
        return longest

    visited = set()
    longest_path = dfs(start_node, visited, [])
    return longest_path

def json_yukle(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        graph_data = json.load(f)
    return graph_data

input_file = "graph_data.json"
graph_data = json_yukle(input_file)

def bfs_en_kisa_yol(graph, start, end):
    visited = set()
    queue = [[start]]
    path_steps = []
    result_queue = []

    if start == end:
        result_queue.append(start)
        return [start], [{"step": 1, "path": [start]}], result_queue

    step_count = 0
    while queue:
        path = queue.pop(0)
        node = path[-1]

        if node not in visited:
            neighbors = graph[node]["edges"]

            for neighbor in neighbors:
                new_path = path + [neighbor]
                queue.append(new_path)
                step_count += 1
                path_steps.append({"step": step_count, "path": " → ".join(new_path)})

                if neighbor == end:
                    result_queue = [graph[n]["id"] for n in new_path]
                    return new_path, path_steps, result_queue

            visited.add(node)

    return None, path_steps, result_queue

@app.route("/shortest-path", methods=["POST"])
def en_kisa_yol():
    data = request.get_json()
    start_id = data.get("start")
    end_id = data.get("end")

    if not start_id or not end_id:
        return jsonify({"error": "Başlangıç ve bitiş yazar ID'leri gereklidir."}), 400

    start_node = next((node for node, d in graph_data.items() if str(d["id"]) == str(start_id)), None)
    end_node = next((node for node, d in graph_data.items() if str(d["id"]) == str(end_id)), None)

    if not start_node or not end_node:
        return jsonify({"error": "Geçersiz yazar ID'leri."}), 400

    result, path_steps, result_queue = bfs_en_kisa_yol(graph_data, start_node, end_node)

    if not result:
        return jsonify({
            "message": "Yazarlar arasında bağlantı yok.",
            "path": [],
            "edges": []
        }), 404

    edges_on_path = []
    for i in range(len(result) - 1):
        source_node = graph_data[result[i]]["id"]
        target_node = graph_data[result[i + 1]]["id"]
        edges_on_path.append({"source": source_node, "target": target_node})

    global last_queue
    last_queue = result_queue

    return jsonify({
        "path": [graph_data[node]["id"] for node in result],
        "steps": path_steps,
        "edges": edges_on_path,
        "queue": result_queue
    })

@app.route("/list-authors", methods=["POST"])
def yazar_listesi3():
    try:
        data = request.get_json()
        author_id = data.get("author_id")
        queue = data.get("queue")

        if not queue or not isinstance(queue, list):
            return jsonify({"error": "Geçerli bir kuyruk bulunamadı."}), 400

        if not author_id:
            return jsonify({"error": "Silinecek yazar ID'si gereklidir."}), 400

        original_queue = []
        for item in queue:
            node_name = dugum_id_bul(graph_data, item["id"])
            if node_name:
                original_queue.append({"id": item["id"], "label": node_name})
            else:
                original_queue.append({"id": item["id"], "label": "Bilinmeyen Yazar"})

        author_to_delete = next((item for item in queue if str(item["id"]) == str(author_id)), None)
        if not author_to_delete:
            return jsonify({"error": "Belirtilen ID'ye sahip yazar bulunamadı."}), 404

        node_name = dugum_id_bul(graph_data, author_id)
        if not node_name:
            node_name = "Bilinmeyen Yazar"

        updated_queue = [item for item in queue if str(item["id"]) != str(author_id)]

        updated_queue_display = []
        for item in updated_queue:
            node_name = dugum_id_bul(graph_data, item["id"])
            if node_name:
                updated_queue_display.append({"id": item["id"], "label": node_name})
            else:
                updated_queue_display.append({"id": item["id"], "label": "Bilinmeyen Yazar"})

        return jsonify({
            "original_queue": original_queue,
            "updated_queue": updated_queue_display,
            "deleted_author": {"id": author_id, "label": node_name}
        })
    except Exception as e:
        return jsonify({"error": "Sunucu tarafında bir hata oluştu."}), 500

@app.route("/queue", methods=["POST"])
def yazarlarin_kuyrugu():
    data = request.get_json()
    author_id = data.get("author")

    if not author_id:
        return jsonify({"error": "Yazar ID'si gereklidir."}), 400

    author_node = dugum_id_bul(graph_data, author_id)
    if not author_node:
        return jsonify({"error": "Geçersiz yazar ID'si."}), 400

    sorted_queue, log = kuyrukta_isbirlikci_sirala2(graph_data, author_node)
    return jsonify({"queue": sorted_queue, "log": log})

def dijkstra_algoritmasi(graph, start_node):
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0
    previous_nodes = {node: None for node in graph}
    visited = set()
    steps = []

    while len(visited) < len(graph):
        current_node = min((node for node in graph if node not in visited), key=lambda x: distances[x])

        if distances[current_node] == float('inf'):
            break

        for neighbor, edge_info in graph[current_node]["edges"].items():
            weight = edge_info["weight"]
            new_distance = distances[current_node] + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node
                steps.append({
                    "from": current_node,
                    "to": neighbor,
                    "distance": new_distance
                })

        visited.add(current_node)

    distances = {node: (dist if dist != float('inf') else "Ulaşılamaz") for node, dist in distances.items()}
    return distances, steps

@app.route("/shortest-paths-all", methods=["POST"])
def tum_en_kisa_yollar():
    data = request.get_json()
    author_id = data.get("author")

    if not author_id:
        return jsonify({"error": "Yazar ID'si gereklidir."}), 400

    author_node = dugum_id_bul(graph_data, author_id)
    if not author_node:
        return jsonify({"error": "Geçersiz yazar ID'si."}), 400

    distances, steps = dijkstra_algoritmasi(graph_data, author_node)

    return jsonify({
        "author_name": author_node,
        "distances": distances,
        "steps": steps
    })

@app.route("/collaborators", methods=["POST"])
def toplam_isbirlikci():
    data = request.get_json()
    author_id = data.get("author")

    if not author_id:
        return jsonify({"error": "Yazar ID'si gereklidir."}), 400

    author_node = dugum_id_bul(graph_data, author_id)
    if not author_node:
        return jsonify({"error": "Geçersiz yazar ID'si."}), 400

    total = toplam_isbirlikci_hesapla5(graph_data, author_node)
    return jsonify({"author": author_node, "total_collaborators": total})

@app.route("/most-collaborative", methods=["GET"])
def en_fazla_yazar_isbirligi():
    result = en_cok_isbirlik_yapan6(graph_data)
    return jsonify(result)

@app.route("/longest-path", methods=["POST"])
def en_uzun_yol():
    data = request.get_json()
    start_id = data.get("start")

    if not start_id:
        return jsonify({"error": "Başlangıç yazar ID'si gereklidir."}), 400

    start_node = dugum_id_bul(graph_data, start_id)
    if not start_node:
        return jsonify({"error": "Geçersiz yazar ID'si."}), 400

    longest_path_result = dfs_uzun_yol7(graph_data, start_node)
    return jsonify({"longest_path": longest_path_result, "length": len(longest_path_result)})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/graph")
def graph():
    return jsonify(graph_data)

if __name__ == "__main__":
    app.run(debug=True)
