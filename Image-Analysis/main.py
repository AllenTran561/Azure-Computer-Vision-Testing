import os
import io
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv, dotenv_values
from PIL import Image
import pandas as pd
import numpy as np

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
                # Append image name and byte data as a tuple to the list
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
        # Calculate average confidence
        if count > 0:
            averageConfidence = sum(conf) / count
        else:
            averageConfidence = 0

        # Append the result to the list
        results.append({
            'Filename': filename,
            'Object': target,
            'Count': count,
            'Confidence': averageConfidence
        })

    # Convert results list to a Pandas DataFrame
    df = pd.DataFrame(results)
    return df

if __name__ == "__main__":
    folderPath = "images/187-CV-C1"
    target = "person"
    client = setupClient()
    images = getImages(folderPath)
    df = processImages(client, images, target)
    print(df)