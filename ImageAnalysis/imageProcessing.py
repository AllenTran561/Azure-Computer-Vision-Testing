import os
import io
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from PIL import Image
import pandas as pd

# Connects to Azure API
def setupClient():
    try:
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        ENDPOINT = os.getenv("ENDPOINT")
    except KeyError:
        print("Error in retrieving credentials")
        exit()
    print("Starting client")

    return ImageAnalysisClient(endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY))
    
# gets all images in the folder
def getImages(folderPath):
    images = []
    try:
        for filename in os.listdir(folderPath):
            filepath = os.path.join(folderPath, filename)
            if os.path.isfile(filepath) and filename.lower().endswith('.jpg'):
                img = Image.open(filepath)
                # Convert image to bytes (client.analyze uses bytes)
                with io.BytesIO() as output:
                    img.save(output, format="JPEG")  # Save as JPEG
                    image_data = output.getvalue()
                images.append((filename, image_data))
    except FileNotFoundError:
        print("Error: Folder not found")
        exit()
    print(len(images), "images found in", folderPath)
    return images

def processImages(client, images, target):
    results = []
    for filename, image_data in images:
        print("Processing image:", filename)
        result = client.analyze(image_data=image_data, visual_features=[VisualFeatures.OBJECTS])
        # Number of targets in the image
        count = 0
        # Arr of confidence per target in the image
        conf = []
        if 'values' in result.objects:
            detected_objects = result.objects['values']
            for detected_object in detected_objects:
                tags = detected_object['tags']
                for tag in tags:
                    name = tag['name']
                    confidence = tag['confidence']
                    if name == target:  # Check if the detected object matches the target
                        count += 1
                        conf.append(confidence)
        # Average confidence
        if count > 0:
            averageConfidence = sum(conf) / count
        else:
            averageConfidence = 0

        results.append({
            'Filename': filename,
            'Object': target,
            'Count': count,
            'Confidence': averageConfidence
        })
        print("Finished processing image:", filename)

    # Convert results to DataFrame
    df = pd.DataFrame(results)
    return df