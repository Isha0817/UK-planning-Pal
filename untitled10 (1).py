# -*- coding: utf-8 -*-
"""Untitled10.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hPONzUjE-17hemU7ciOFhVVPRc6aGeok
"""

import subprocess

subprocess.run(["git", "clone", "https://github.com/facebookresearch/segment-anything.git"])

!wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

import requests

url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
output_file = "sam_vit_h_4b8939.pth"

response = requests.get(url, stream=True)
if response.status_code == 200:
    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
    print(f"File downloaded successfully: {output_file}")
else:
    print(f"Failed to download file. Status code: {response.status_code}")

!pip install segment-anything

from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
mask_generator = SamAutomaticMaskGenerator(sam)


image = Image.open("/content/exiisting elevations.PNG").convert("RGB")
image_np = np.array(image)


masks = mask_generator.generate(image_np)


def show_masks(image, masks):
    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    for mask in masks:
        plt.imshow(mask["segmentation"], alpha=0.5)
    plt.axis("off")
    plt.show()

show_masks(image_np, masks)

import cv2
import numpy as np
from google.colab.patches import cv2_imshow

# Load the floor plan image
image_path = '/content/exiisting elevations.PNG'  # Replace with your image path
image = cv2.imread(image_path)

# Resize image for better handling (optional)
image = cv2.resize(image, (800, 800))

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply adaptive thresholding
thresh = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
)

# Apply morphological operations to clean up noise
kernel = np.ones((5, 5), np.uint8)
cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

# Find contours
contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter and sort contours by area and position
filtered_contours = [c for c in contours if cv2.contourArea(c) > 5000]
sorted_contours = sorted(filtered_contours, key=lambda c: cv2.boundingRect(c)[1])  # Sort top-to-bottom

# Create a copy for visualization
output_image = image.copy()

# Iterate through sorted contours and save each segment
for i, contour in enumerate(sorted_contours):
    # Get bounding box for the contour
    x, y, w, h = cv2.boundingRect(contour)

    # Draw bounding box for visualization
    cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Extract and save each segmented view
    segment = image[y:y+h, x:x+w]  # Extract from original image
    cv2.imwrite(f'segment_{i+1}.jpg', segment)

# Display the result with bounding boxes for verification
cv2_imshow(output_image)

# Save the output image
cv2.imwrite('segmented_views_bounding_boxes.jpg', output_image)

!pip install paddlepaddle paddleocr

import cv2
import numpy as np
from paddleocr import PaddleOCR
from google.colab.patches import cv2_imshow

def detect_text_paddleocr(image):
    """Detect text in an image using PaddleOCR."""
    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Initialize with English and angle classifier

    # Perform OCR on the image
    result = ocr.ocr(image, cls=True)

    # Extract detected text and bounding boxes
    detected_text = []
    for line in result[0]:
        text = line[1][0]  # Get the text from the tuple
        bbox = line[0]  # Bounding box of the text
        detected_text.append({
            "Text": text,
            "BoundingBox": bbox
        })

    return detected_text

def segment_views_and_detect_text(image_path):
    """Segment views based on contours and detect text using PaddleOCR."""
    # Load the image
    image = cv2.imread(image_path)

    # Resize image for better handling (optional)
    image = cv2.resize(image, (800, 800))

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Apply morphological operations to clean up noise
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and sort contours by area and position
    filtered_contours = [c for c in contours if cv2.contourArea(c) > 5000]
    sorted_contours = sorted(filtered_contours, key=lambda c: cv2.boundingRect(c)[1])  # Sort top-to-bottom

    # Prepare to store segments
    segments = []
    detected_text = detect_text_paddleocr(image)  # Step 2: Detect text using PaddleOCR

    # Iterate through sorted contours and save each segment
    for i, contour in enumerate(sorted_contours):
        # Get bounding box for the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Extract the segment from the original image
        segment = image[y:y + h, x:x + w]

        # Now, let's check if there is text within this bounding box
        for text_item in detected_text:
            text = text_item["Text"]
            bbox = text_item["BoundingBox"]

            # Check if the text is within the bounding box of the segment
            if x <= bbox[0][0] <= x + w and y <= bbox[0][1] <= y + h:
                # If the text is within the segment, save it with the text label as the filename
                segment_filename = f"{text.replace(' ', '_')}.jpg"
                cv2.imwrite(segment_filename, segment)
                segments.append(segment_filename)

    return segments

# Input image path
image_path = "/content/exiisting elevations.PNG"  # Replace with your image file

# Step 1: Segment views and detect text using PaddleOCR
segmented_files = segment_views_and_detect_text(image_path)

# Step 2: Display results
print("Segmented views saved as:")
for filename in segmented_files:
    print(filename)

import cv2
import numpy as np
from paddleocr import PaddleOCR
from google.colab.patches import cv2_imshow

def detect_text_paddleocr(image):
    """Detect text in an image using PaddleOCR."""
    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    # Perform OCR on the image
    result = ocr.ocr(image, cls=True)


    detected_text = []
    for line in result[0]:
        text = line[1][0]
        bbox = line[0]
        detected_text.append({
            "Text": text,
            "BoundingBox": bbox
        })

    return detected_text

def segment_views_and_detect_text(image_path):
    """Segment views based on contours and detect text using PaddleOCR."""
    # Load the image
    image = cv2.imread(image_path)

    # Resize image for better handling (optional)
    image = cv2.resize(image, (800, 800))

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Apply morphological operations to clean up noise
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and sort contours by area and position
    filtered_contours = [c for c in contours if cv2.contourArea(c) > 5000]
    sorted_contours = sorted(filtered_contours, key=lambda c: cv2.boundingRect(c)[1])  # Sort top-to-bottom

    # Prepare to store segments
    segments = []
    detected_text = detect_text_paddleocr(image)  # Step 2: Detect text using PaddleOCR

    # Iterate through sorted contours and save each segment
    for i, contour in enumerate(sorted_contours):
        # Get bounding box for the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Extract the segment from the original image
        segment = image[y:y + h, x:x + w]

        # Now, let's check if there is text within this bounding box
        for text_item in detected_text:
            text = text_item["Text"].lower()
            bbox = text_item["BoundingBox"]

            # Check if the text contains 'elevation' or 'floor' and if it is within the segment
            if ('elevation' in text or 'floor' in text) and (x <= bbox[0][0] <= x + w and y <= bbox[0][1] <= y + h):

                segment_filename = f"{text.replace(' ', '_')}.jpg"
                cv2.imwrite(segment_filename, segment)
                segments.append(segment_filename)

    return segments

# Input image path
image_path = "/content/exiisting elevations.PNG"

# Step 1: Segment views and detect text using PaddleOCR
segmented_files = segment_views_and_detect_text(image_path)

# Step 2: Display results
print("Segmented views saved as:")
for filename in segmented_files:
    print(filename)







