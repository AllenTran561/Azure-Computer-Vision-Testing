import tkinter as tk
from tkinter import filedialog
from imageProcessing import getImages, processImages, setupClient
from pandastable import Table
import pandas as pd

# GUI class
class ImageAnalysisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Analysis Tool")
        self.folderPathVar = tk.StringVar()
        # Inputted images
        self.images = None
        # expected output for each image
        self.imageParams = []
        self.target = None
        self.selectFolder()

    # Select folder with images
    def selectFolder(self):
        labelFolder = tk.Label(self.root, text="Select Image Folder:")
        labelFolder.grid(row=0, column=0, padx=10, pady=5)

        folder = tk.Entry(self.root, textvariable=self.folderPathVar, width=50)
        folder.grid(row=0, column=1, padx=10, pady=5)

        buttonBrowse = tk.Button(self.root, text="Browse", command=self.getImages)
        buttonBrowse.grid(row=0, column=2, padx=10, pady=5)

        buttonSubmit = tk.Button(self.root, text="Submit", command=self.imageExpectedOutput)
        buttonSubmit.grid(row=1, column=1, padx=10, pady=5)

    # Gets images in the folder
    def getImages(self):
        folderPath = filedialog.askdirectory()
        if folderPath:
            self.folderPathVar.set(folderPath)
            self.images = getImages(folderPath)
    
    # Accepts user inputs for expected result for each image
    def imageExpectedOutput(self):
        if self.images:
            paramsWindow = tk.Toplevel()
            paramsWindow.title("Image Parameters")

            frame = tk.Frame(paramsWindow)
            frame.pack(padx=10, pady=5)

            labelFilename = tk.Label(frame, text="Filename")
            labelFilename.grid(row=0, column=0, padx=5, pady=2)

            labelExpectedCount = tk.Label(frame, text="Expected Count")
            labelExpectedCount.grid(row=0, column=1, padx=5, pady=2)

            labelExpectedConfidence = tk.Label(frame, text="Expected Confidence")
            labelExpectedConfidence.grid(row=0, column=2, padx=5, pady=2)

            expectedConfidence = tk.Entry(frame, width=10)
            expectedConfidence.grid(row=0, column=3, padx=5, pady=2)

            for filename, _ in self.images:
                frame = tk.Frame(paramsWindow)
                frame.pack(padx=10, pady=5)

                labelFilename = tk.Label(frame, text=filename)
                labelFilename.grid(row=0, column=0, padx=5, pady=2)

                expectedCount = tk.Entry(frame, width=10)
                expectedCount.grid(row=0, column=1, padx=5, pady=2)

                self.imageParams.append((filename, expectedCount, expectedConfidence))

            labelTarget = tk.Label(frame, text="Target:")
            labelTarget.grid(row=len(self.images), column=0, padx=5, pady=2)

            # Sets Target Variable
            self.target = tk.Entry(frame, width=10)
            self.target.grid(row=len(self.images), column=1, padx=5, pady=2)

            buttonSubmit = tk.Button(paramsWindow, text="Submit", command=self.runAnalysis)
            buttonSubmit.pack(padx=10, pady=5)

    # Runs Image Analysis for each image
    def runAnalysis(self):
        client = setupClient()
        target = self.target.get()
        results = []

        for filename, expectedCount, expectedConfidence in self.imageParams:
            # Convert String input to int
            expectedCount = int(expectedCount.get())
            expectedConfidence = float(expectedConfidence.get())
            imageData = [imgData for imgName, imgData in self.images if imgName == filename][0]
            result = processImages(client, [(filename, imageData)], target, expectedCount, expectedConfidence)
            results.append(result)  
            
        self.displayResults(results)

    # Displays results
    def displayResults(self, results):
        resultsWindow = tk.Toplevel()
        resultsWindow.title("Analysis Results")
        # print("results: ", results)
        # print("result type: ", type(results))
        frameResults = tk.Frame(resultsWindow)
        frameResults.pack(side=tk.LEFT, padx=10, pady=5)

        frameSummary = tk.Frame(resultsWindow)
        frameSummary.pack(side=tk.RIGHT, padx=10, pady=5)

        # Turns list of lists to dictionary which df uses
        resultsDict = [item for sublist in results for item in sublist]
        df = pd.DataFrame(resultsDict)
        print("df: ", df)

        # Post results
        # Add Detection column
        df["Detection"] = df.apply(lambda row: "Accurate" 
                                if row["Count"] == row["Expected Count"]
                                    else ("No Detection"
                                if row["Count"] == 0
                                    else "Inaccurate"
                                          ), axis=1)

        # If
        df["Accuracy"] = df.apply(lambda row: "No Accuracy"
                                if row["Confidence"] == 0 
                                    else ("High Confidence" 
                                if row["Confidence"] > row["Expected Confidence"]                                   
                                    else "Low Confidence"), axis=1)

        # Add Pass column
        df["Pass"] = df.apply(lambda row: True 
                            if row["Detection"] == "Accurate" 
                                and 
                            row["Accuracy"] == "High Confidence" 
                                else False, axis=1)

        summary = {
            "Detection Average": df["Detection"].eq("Accurate").mean(),
            "Accuracy Average": df["Accuracy"].eq("High Confidence").mean(),
            "Pass Rate ": f"{df["Pass"].sum()} / {len(df)}",
            "Pass Percentage": df["Pass"].eq(True).mean()
        }

        summaryDf = pd.DataFrame([summary])
        print(summaryDf)
        pt = Table(frameResults, dataframe=df, width=1000, height=1000, column_minwidth=150)
        summaryPt = Table(frameSummary, dataframe=summaryDf)
        pt.show()
        summaryPt.show()

    def run(self):
        self.root.mainloop()