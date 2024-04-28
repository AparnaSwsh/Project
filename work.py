import cv2
import numpy as np
import networkx as nx
import pyttsx3
import threading
import tkinter as tk


def insert_nodes(image_path, node_coordinates, node_names=None):
    # Load image
    img = cv2.imread(image_path)

    # Define node color (here, using red)
    node_color = (0, 0, 255)

    # Draw nodes on image
    for i, (x, y) in enumerate(node_coordinates):
        # Draw circle for node
        cv2.circle(img, (x, y), radius=5, color=node_color, thickness=-1)  # filled circle

        # Add node name as text
        if node_names:
            cv2.putText(img, node_names[i], (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, node_color, 1)

    return img


def find_shortest_path(node_info, start_node_name, end_node_name):

    print(node_info)
    # Create a graph
    G = nx.Graph()
    for i, (x, y) in enumerate(node_info):
        G.add_node(i, pos=(x, y))  # Add node with position

    # Add edges based on proximity among nodes in node_info
    for i in range(len(node_info)):
        for j in range(i + 1, len(node_info)):
            dist = np.linalg.norm(np.array(node_info[i]) - np.array(node_info[j]))
            if dist < 100:  # Adjust the threshold as needed
                G.add_edge(i, j)

    # Find indices of start and end nodes
    start_node_index = [i for i, (x, y) in enumerate(node_info) if node_names[i] == start_node_name][0]
    end_node_index = [i for i, (x, y) in enumerate(node_info) if node_names[i] == end_node_name][0]

    # Find shortest path using Dijkstra's algorithm
    shortest_path_indices = nx.shortest_path(G, source=start_node_index, target=end_node_index)

    return shortest_path_indices


def generate_directions(shortest_path_indices, node_coordinates, node_names):
    directions = []
    for i in range(len(shortest_path_indices) - 1):
        start_node_name = node_names[shortest_path_indices[i]]
        end_node_name = node_names[shortest_path_indices[i + 1]]
        start_coord = node_coordinates[shortest_path_indices[i]]
        end_coord = node_coordinates[shortest_path_indices[i + 1]]
        direction = get_direction(start_coord, end_coord)
        directions.append(f"Go {direction} from {start_node_name} to {end_node_name}")
    return directions


def speak_direction(direction):
    engine = pyttsx3.init()
    engine.say(direction)
    engine.runAndWait()


def get_direction(start_coord, end_coord):
    dx = end_coord[0] - start_coord[0]
    dy = end_coord[1] - start_coord[1]
    angle = np.arctan2(dy, dx) * 180 / np.pi
    if angle < 0:
        angle += 360
    if 45 <= angle < 135:
        return "upwards"
    elif 135 <= angle < 225:
        return "leftwards"
    elif 225 <= angle < 315:
        return "forward"
    else:
        return "rightwards"


def draw_path(img, shortest_path_indices, node_coordinates):
    # Draw shortest path as dotted line
    for i in range(len(shortest_path_indices) - 1):
        start_coord = node_coordinates[shortest_path_indices[i]]
        end_coord = node_coordinates[shortest_path_indices[i + 1]]
        cv2.line(img, start_coord, end_coord, (0, 0, 255), thickness=1, lineType=cv2.LINE_AA)
    return img


def display_image_with_path(img, window_name):
    img_with_path = img.copy()
    cv2.imshow(window_name, img_with_path)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def on_button_click(directions):
    for direction in directions:
        speak_direction(direction)


# Example usage
image_path = r'C:\Users\HOME\Desktop\project\myitems\floorimg.jpg'  # Path to input image
node_coordinates = [(38, 302),
                    (38, 255),
                    (154, 206),
                    (194, 208),
                    (359, 204),
                    (389, 168),
                    (420, 207),
                    (585, 206),
                    (764, 248),
                    (762, 309),
                    (732, 353),
                    (628, 354),
                    (596, 354),
                    (552, 334),
                    (506, 334),
                    (506, 334),
                    (311, 331),
                    (247, 333),
                    (206, 352),
                    (165, 352),
                    (62, 352),
                    (92, 272),
                    (176, 273),
                    (275, 269),
                    (396, 268),
                    (393, 208),
                    (536, 271),
                    (608, 269),
                    (716, 276)]  # Example node coordinates
node_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U',
              'V', 'X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8']  # Example node names (optional)

# Initialize node_info with only the nodes starting with "X"
node_info = {name: coordinates for name, coordinates in zip(node_names, node_coordinates) if name.startswith('X')}

# Input from user for start and end nodes
start_node_name = input('Enter the name of the start node: ')
end_node_name = input('Enter the name of the end node: ')

# Find the coordinates for the start node
start_node_coordinates = None
for i, name in enumerate(node_names):
    if name == start_node_name:
        start_node_coordinates = node_coordinates[i]
        break

# Find the coordinates for the end node
end_node_coordinates = None
for i, name in enumerate(node_names):
    if name == end_node_name:
        end_node_coordinates = node_coordinates[i]
        break

# Add the coordinates of start and end nodes to the existing node_info dictionary
node_info[start_node_name] = start_node_coordinates
node_info[end_node_name] = end_node_coordinates

# Output the updated node information
print("Updated Node Information:")
for name, coordinates in node_info.items():
    print(f"{name}: {coordinates}")

# Find shortest path
shortest_path_indices = find_shortest_path(node_info, start_node_name, end_node_name)

# Generate directions
directions = generate_directions(shortest_path_indices, node_coordinates, node_names)

# Print directions
for direction in directions:
    print(direction)


# Create a button for voice output
root = tk.Tk()
button = tk.Button(root, text="Start Voice Output", command=lambda: on_button_click(directions))
button.pack()

# Display image with nodes and shortest path
img = insert_nodes(image_path, node_coordinates, node_names)
image_with_path = draw_path(img, shortest_path_indices, node_coordinates)
cv2.imshow('Image with Nodes and Shortest Path', image_with_path)
cv2.waitKey(0)
cv2.destroyAllWindows()

root.mainloop()
