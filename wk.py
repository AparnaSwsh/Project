import cv2
import numpy as np
import networkx as nx
import pyttsx3
import tkinter as tk


def insert_nodes(image_path, node_coordinates, node_names=None, start_node=None, end_node=None):
    # Load image
    img = cv2.imread(image_path)

    # Define node colors
    node_color = (0, 0, 255)  # Default color for nodes
    start_color = (0, 255, 0)  # Green color for start node
    end_color = (255, 0, 0)  # Blue color for end node

    # Define node radius
    default_radius = 3
    start_end_radius = 7

    # Draw nodes on image
    for i, (x, y) in enumerate(node_coordinates):
        # Determine node color and radius
        if node_names and node_names[i] == start_node:
            color = start_color
            radius = start_end_radius
        elif node_names and node_names[i] == end_node:
            color = end_color
            radius = start_end_radius
        else:
            color = node_color
            radius = default_radius

        # Draw circle for node
        cv2.circle(img, (x, y), radius=radius, color=color, thickness=-1)  # filled circle

    return img


def find_shortest_path(node_info, start_node_name, end_node_name):
    # Create a graph
    G = nx.Graph()
    for name, (x, y) in node_info.items():
        G.add_node(name, pos=(x, y))  # Add node with position

    # Add edges based on proximity among nodes in node_info
    for name1, coord1 in node_info.items():
        for name2, coord2 in node_info.items():
            if name1 != name2:  # Avoid adding self-loops
                dist = np.linalg.norm(np.array(coord1) - np.array(coord2))
                if dist < 102:  # Adjust the threshold as needed
                    G.add_edge(name1, name2)

    shortest_path_nodes = nx.shortest_path(G, source=start_node_name, target=end_node_name)

    # Convert node names to indices (if needed)
    shortest_path_indices = [node_names.index(node) for node in shortest_path_nodes]

    return shortest_path_indices


def generate_directions(shortest_path_indices, node_coordinates, node_names):
    directions = []
    prev_direction = None
    for i in range(len(shortest_path_indices) - 1):
        start_node_name = node_names[shortest_path_indices[i]]
        end_node_name = node_names[shortest_path_indices[i + 1]]
        start_coord = node_coordinates[shortest_path_indices[i]]
        end_coord = node_coordinates[shortest_path_indices[i + 1]]
        direction = get_direction(start_coord, end_coord)

        # Add the first move direction
        if not directions:
            directions.append(f"Go {direction} from {start_node_name} to {end_node_name}")

        # Check for change in direction greater than 30 degrees
        if i + 2 < len(shortest_path_indices):
            next_coord = node_coordinates[shortest_path_indices[i + 2]]
            next_direction = get_direction(end_coord, next_coord)
            angle_diff = abs(angle_difference(direction, next_direction))
            if angle_diff > 30:
                directions.append(f"Turn {next_direction} at {end_node_name}")

        prev_direction = direction

    # Add the last move direction
    last_start_node_name = node_names[shortest_path_indices[-2]]
    last_end_node_name = node_names[shortest_path_indices[-1]]
    last_start_coord = node_coordinates[shortest_path_indices[-2]]
    last_end_coord = node_coordinates[shortest_path_indices[-1]]
    last_direction = get_direction(last_start_coord, last_end_coord)
    directions.append(f"Go {last_direction} from {last_start_node_name} to {last_end_node_name}")

    return directions


def angle_difference(dir1, dir2):
    angle1 = {"upwards": 90, "leftwards": 180, "forward": 270, "rightwards": 0}
    angle2 = {"upwards": 90, "leftwards": 180, "forward": 270, "rightwards": 0}
    return abs(angle1[dir1] - angle2[dir2])


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
                    (154, 206),
                    (194, 208),
                    (359, 204),
                    (389, 168),
                    (420, 207),
                    (585, 206),
                    (624, 208),
                    (764, 248),
                    (762, 309),
                    (732, 353),
                    (628, 354),
                    (596, 354),
                    (552, 334),
                    (506, 334),
                    (311, 331),
                    (247, 333),
                    (206, 352),
                    (165, 352),
                    (62, 352),
                    (92, 272),  # X1
                    (176, 273),  # X2
                    (275, 269),  # X3
                    (361, 269),  # X4
                    (393, 208),  # X5
                    (426, 279),  # X6
                    (520, 265),  # X7
                    (606, 277),
                    (696, 282)]  # Example node coordinates
node_names = ['Library','Smart Class', 'Boys common room', 'Gents Toilet', 'Lift1', 'First aid room',
              'Lab House keeping','Kitchen', 'Restaurant', 'Classroom', 'Stairs near restaurant', 'Tutorial room',
              'Staff room', 'Stationary store', 'Class 205', 'Mini hall', 'Professors room', 'Pantry', 'Tutorial room1',
              'Stairs near Library', 'Near smart class', 'Near to smart class', 'Near Professors room', 'Near to the turning towards lift', 'Near lift', 'Near to lift', 'Near stationary ', 'Near kitchen','Near restaruant']
# Initialize node_info with only the nodes starting with "X"
node_info = {name: coordinates for name, coordinates in zip(node_names, node_coordinates) if name.startswith('N')}

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
img = insert_nodes(image_path, node_coordinates, node_names, start_node=start_node_name, end_node=end_node_name)
image_with_path = draw_path(img, shortest_path_indices, node_coordinates)
cv2.imshow('Image with Nodes and Shortest Path', image_with_path)
cv2.waitKey(0)
cv2.destroyAllWindows()

root.mainloop()
