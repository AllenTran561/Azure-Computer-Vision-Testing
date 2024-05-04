import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv, dotenv_values

def run():
    try:
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        ENDPOINT = os.getenv("ENDPOINT")
    except KeyError:
        print("Error in retrieving credentials")
        exit()
    print("Starting client")

    client = ImageAnalysisClient(endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY))

    try:
        # Load image from folder
        with open("images/187-CV-C1/H1C1.jpg", "rb") as f:
            image_data = f.read()
    except FileNotFoundError:
        print("Error: Image file not found")
        exit()
        
    # Call Azure Cognitive Services to analyze the image
    result = client.analyze(image_data=image_data, visual_features=[VisualFeatures.OBJECTS])
    
    # Process the result as needed
    # For example, print detected objects
    print(result.objects)
    for detected_object in result.objects['values']:
        bounding_box = detected_object['boundingBox']
        tags = detected_object['tags']
        print("Bounding Box:", bounding_box)
        for tag in tags:
            name = tag['name']
            confidence = tag['confidence']
            print(f"Object: {name} | Confidence: {confidence}")

if __name__ == "__main__":
    run()