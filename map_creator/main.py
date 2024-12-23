import tkinter as tk
import json

class GraphEditor:
    def __init__(self, root, save_path="."):
        self.root = root
        self.root.title("Graph Editor")

        self.save_path = save_path

        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()

        self.nodes = []
        self.edges = []
        self.current_node = None
        self.current_type = "Router"
        self.current_color = "blue"
        self.buffer_size = 0

        self.canvas.bind("<Button-1>", self.add_node)
        self.canvas.bind("<Button-3>", self.start_edge)
        self.canvas.bind("<ButtonRelease-3>", self.end_edge)
        
        self.root.bind("<KeyPress-s>", lambda e: self.set_current_type("Server", "red"))
        self.root.bind("<KeyPress-r>", lambda e: self.set_current_type("Router", "blue"))
        self.root.bind("<KeyPress-h>", lambda e: self.set_current_type("Host", "green"))

        controls_frame = tk.Frame(root)
        controls_frame.pack()

        self.file_name_entry = tk.Entry(controls_frame, width=15)
        self.file_name_entry.insert(0, "graph.json")
        self.file_name_entry.pack(side=tk.LEFT)

        self.buffer_size_entry = tk.Entry(controls_frame, width=10)
        self.buffer_size_entry.insert(0, "0")
        self.buffer_size_entry.pack(side=tk.LEFT)

        self.save_button = tk.Button(controls_frame, text="Save Graph", command=self.save_graph)
        self.save_button.pack(side=tk.LEFT)

    def set_current_type(self, node_type, color):
        self.current_type = node_type
        self.current_color = color

    def add_node(self, event):
        x, y = event.x, event.y
        node_id = len(self.nodes)

        if self.current_type == "Router":
            try:
                self.buffer_size = int(self.buffer_size_entry.get())
            except ValueError:
                self.buffer_size = 0

            self.nodes.append({
                "type": self.current_type,
                "bufferSize": self.buffer_size,
                "coordinates": {"x": x, "y": y}
            })
        else:

            self.nodes.append({
                "type": self.current_type,
                "coordinates": {"x": x, "y": y}
            })

        self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=self.current_color, outline="black")
        self.canvas.create_text(x, y, text=str(node_id), fill="white")

    def start_edge(self, event):
        x, y = event.x, event.y
        self.current_node = self.get_node_at(x, y)

    def end_edge(self, event):
        if self.current_node is None:
            return

        x, y = event.x, event.y
        target_node = self.get_node_at(x, y)
        if target_node is not None and target_node != self.current_node:
            self.edges.append({"weight": 10000, "from": self.current_node, "to": target_node})
            x1, y1 = self.nodes[self.current_node]["coordinates"].values()
            x2, y2 = self.nodes[target_node]["coordinates"].values()
            self.canvas.create_line(x1, y1, x2, y2, fill="black")

        self.current_node = None

    def get_node_at(self, x, y):
        for i, node in enumerate(self.nodes):
            nx, ny = node["coordinates"].values()
            if (nx - 10 <= x <= nx + 10) and (ny - 10 <= y <= ny + 10):
                return i
        return None

    def save_graph(self):
        graph_data = {"nodes": self.nodes, "edges": self.edges}
        path = self.save_path + "/" + self.file_name_entry.get()
        with open(path, "w") as f:
            json.dump(graph_data, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    editor = GraphEditor(root, save_path=".")
    root.mainloop()
