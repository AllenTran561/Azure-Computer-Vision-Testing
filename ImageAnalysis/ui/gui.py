import tkinter as tk
from tkinter import filedialog
from pandastable import Table
from imageProcessing import setupClient, getImages, processImages

def selectFolder():
    folderPath = filedialog.askdirectory()
    if folderPath:
        folderPathVar.set(folderPath)

def runAnalysis():
    root = tk.Tk()
    # Folder path and target is inputted through the gui
    folderPath = folderPathVar.get()
    target = targetVar.get()

    client = setupClient()
    images = getImages(folderPath)
    df = processImages(client, images, target)
    
    df = df.sort_values(by='Filename')

    # Export df to CSV
    df.to_csv('output.csv', index=False)
    
    # Export df to JSON
    df.to_json('output.json', orient='records')
    print("Analysis completed. Output files saved as 'output.csv' and 'output.json'.")
    
    frame = tk.Frame(root)
    frame.grid(row=3, column=0, columnspan=3)

    # Creates a table in gui
    pt = Table(frame, dataframe=df)
    pt.show()

    root.mainloop()

def runGui():    
    root = tk.Tk()  # Create Tkinter root window
    root.title("Image Analysis Tool")

    global folderPathVar, targetVar

    folderPathVar = tk.StringVar()
    targetVar = tk.StringVar()

    # Folder label
    labelFolder = tk.Label(root, text="Select Image Folder:")
    labelFolder.grid(row=0, column=0, padx=10, pady=5)

    # Folder input
    entryFolder = tk.Entry(root, textvariable=folderPathVar, width=50)
    entryFolder.grid(row=0, column=1, padx=10, pady=5)

    # Folder browse button (opens up windows explorer)
    buttonBrowse = tk.Button(root, text="Browse", command=selectFolder)
    buttonBrowse.grid(row=0, column=2, padx=10, pady=5)

    # Target label
    labelTarget = tk.Label(root, text="Target Object:")
    labelTarget.grid(row=1, column=0, padx=10, pady=5)
    
    # Target input
    entryTarget = tk.Entry(root, textvariable=targetVar, width=50)
    entryTarget.grid(row=1, column=1, padx=10, pady=5)

    # Runs program when pressed
    buttonRun = tk.Button(root, text="Run Analysis", command=runAnalysis)
    buttonRun.grid(row=2, column=1, padx=10, pady=5)

    root.mainloop()