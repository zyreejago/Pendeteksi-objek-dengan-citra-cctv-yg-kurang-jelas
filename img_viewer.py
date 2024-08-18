import PySimpleGUI as sg
import os.path
from PIL import Image, ImageOps 
from processing_list import *



# Kolom Area No 1: Area open folder and select image
file_list_column = [
 [
     sg.Text("Image Information:"),
 ],
 [
     sg.Text(size=(20, 1), key="ImgSize"),
 ],
 [
     sg.Text(size=(20, 1), key="ImgColorDepth"),
 ],
 [
     sg.Text("Open Image Folder :"),
 ],
 [
     sg.In(size=(20, 1), enable_events=True, key="ImgFolder"),
     sg.FolderBrowse(),
 ],
 [
     sg.Text("Choose an image from list :"),
 ],
 [
     sg.Listbox(
         values=[], enable_events=True, size=(18, 10), key="ImgList"
     )
 ],
 [
  sg.Text("List of Processing:"),
 ],

]
list_processing = [
 # [
 #  sg.HorizontalSeparator(),
 # ],

 [
    sg.Button("Processing", size=(20, 1), key="UAS_Filter2")
],
]
# Kolom Area No 2: Area viewer image input
image_viewer_column = [
 [sg.Text("Image Input :")],
 [sg.Text(size=(40, 1), key="FilepathImgInput")],
 [sg.Image(key="ImgInputViewer")],
]


# Kolom Area No 4: Area viewer image output
image_viewer_column2 = [
 [sg.Text("Image Processing Output:")],
 [sg.Text(size=(40, 1), key="ImgProcessingType")],
 [sg.Image(key="ImgOutputViewer")],
]
# Gabung Full layout
layout = [
 [
     sg.Column(file_list_column),
     sg.VSeperator(),
     sg.Column(list_processing),
     sg.VSeperator(),
     sg.Column(image_viewer_column),
     sg.VSeperator(),
     sg.Column(image_viewer_column2),
 ]
]
window = sg.Window("Mini Image Editor", layout)

#nama image file temporary setiap kali processing output
filename_out = "out.png" 

# Run the Event Loop
while True:
 event, values = window.read()
 if event == "Exit" or event == sg.WIN_CLOSED:
     break
 # Folder name was filled in, make a list of files in the folder
 if event == "ImgFolder":
     folder = values["ImgFolder"]
     
     try:
         # Get list of files in folder
         file_list = os.listdir(folder)
     except:
         file_list = []
         
     fnames = [
         f
         for f in file_list
         if os.path.isfile(os.path.join(folder, f))
         and f.lower().endswith((".png", ".gif"))
     ]
     
     window["ImgList"].update(fnames)
     
 elif event == "ImgList": # A file was chosen from the listbox
     try:
        filename = os.path.join(
            values["ImgFolder"], values["ImgList"][0]
        )
        
        window["FilepathImgInput"].update(filename)
        window["ImgInputViewer"].update(filename=filename)
        window["ImgProcessingType"].update(filename)
        window["ImgOutputViewer"].update(filename=filename)
        img_input = Image.open(filename)
        #img_input.show()
    
        #Size
        img_width, img_height = img_input.size
        window["ImgSize"].update("Image Size : "+str(img_width)+" x "+str(img_height))
        
        #Color depth
        mode_to_coldepth = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32, "YCbCr": 24, "LAB":
24, "HSV": 24, "I": 32, "F": 32}
        coldepth = mode_to_coldepth[img_input.mode]
        window["ImgColorDepth"].update("Color Depth : "+str(coldepth))
     except:
        pass
    
 elif event == "UAS_Filter2":
    try:
        brightVal = 90  # Nilai kecerahan tetap, bisa disesuaikan sesuai kebutuhan
        size = 3
        window["ImgProcessingType"].update("UAS Filter (Terang + Median + Prewitt)")
        img_output = combined_brightness_prewitt(img_input, coldepth, brightVal, size)
        img_output.save(filename_out)
        window["ImgOutputViewer"].update(filename=filename_out)
         # Deteksi objek
        threshold = 255  # Nilai ambang untuk deteksi objek
        object_detected = ObjectDetection(img_output, threshold)

        window["ImgProcessingType"].update("Object Detected" if object_detected else "No Object Detected")

    except Exception as e:
            print("Error:", e)
    except Exception as e:
        print("Error:", e)


window.close()
