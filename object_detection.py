import cv2
import numpy as np
from tqdm import tqdm

# Load YOLOv3 model
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

# Load the COCO dataset class names
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Function to process video frames
def process_frame(frame):
    height, width = frame.shape[:2]
    
    # Prepare the image for YOLOv3
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)
    
    # Initialize lists for storing detection results
    class_ids = []
    confidences = []
    boxes = []
    
    # Iterate over each detection output
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            # Only keep detections above a confidence threshold (e.g., 0.5)
            if confidence > 0.5:
                # Get the bounding box coordinates
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    
    # Apply Non-Maximum Suppression to remove duplicate boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    
    # Draw rectangles around detected objects
    for i in indices:
        box = boxes[i]
        x, y, w, h = box
        label = str(classes[class_ids[i]])
        confidence = confidences[i]
        
        # Draw a rectangle and label
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return frame

# Process the video and save it
cap = cv2.VideoCapture("video.mp4")

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object
out = cv2.VideoWriter("output_video.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))


with tqdm(total=750, desc="Processing") as pbar:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Process the frame and detect objects
        frame = process_frame(frame)
        
        # Write the processed frame to the output video
        out.write(frame)
        pbar.update(1)

        cv2.imshow("YOLOv3 Object Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release video capture and writer
cap.release()
out.release()
cv2.destroyAllWindows()
