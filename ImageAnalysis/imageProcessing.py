import os
import io
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from PIL import Image

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
            if os.path.isfile(filepath) and filename.lower().endswith(".jpg"):
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

def processImages(client, images, target, expectedCount, expectedConfidence):
    results = []
    for filename, imageData in images:
        result = client.analyze(image_data=imageData, visual_features=[VisualFeatures.OBJECTS])
        
        # Process result and calculate average confidence
        count = 0
        total_confidence = 0
        if "values" in result.objects:
            detected_objects = result.objects["values"]
            for detected_object in detected_objects:
                tags = detected_object["tags"]
                for tag in tags:
                    name = tag["name"]
                    confidence = tag["confidence"]
                    if name == target:
                        count += 1
                        total_confidence += confidence
        # Average confidence should use expected count as a divisor
        averageConfidence = total_confidence / max(expectedCount, 1)

        # Add result to list
        results.append({
            "Filename": filename,
            "Object": target,
            "Count": count,
            "Expected Count": expectedCount,
            "Confidence": averageConfidence,
            "Expected Confidence": expectedConfidence
        })
    print(results)
    return results