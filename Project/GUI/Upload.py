import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import MyappMultiImage as app

ctk.set_appearance_mode('light')
# ctk.set_default_color_theme("dark-blue")

Image_paths = []
image_paths_to_receive_from_server = []
image_multi_list = []


def identify_clicked_button(button_text):
    global image_paths_to_receive_from_server
    global operation
    operation = button_text

    update_progress()
    image_paths_to_receive_from_server = app.main(Image_paths, operation)
    print(image_paths_to_receive_from_server)

sent_num = 0
receive_num = 0
def update_progress():
    global sent_num
    global receive_num
    message = app.progress()
    if message == "Instance Started and Registered to the ALB target group with port 8080":
        progress_bar.set(0.1)
    elif message == "Start Splitting":
        progress_bar.set(0.2)
    elif message == "Splitting the image is done":
        progress_bar.set(0.3)
    elif message == "Image is sent to instance and its image processing Started":
        progress_bar.set(0.4)
    elif message == "All images are sent successfully":
        progress_bar.set(0.5)
    elif message == "Received Image from the instance":
        progress_bar.set(0.6)
    elif message == "All Images are received":
        progress_bar.set(0.7)
    elif message == "Sorting Received Image like it was sent from User":
        progress_bar.set(0.8)
    elif message == "Deregister the instance from the target group and Stoping them":
        progress_bar.set(0.9)
    elif message == "Sending back to user":
        progress_bar.set(1)
        print("Monitoring messages Ends")
    elif message is None:
        progress_bar.set(0)

    if message != "Sending back to user":
        # Schedule the next update
        root.after(10, update_progress)

def open():
    global Image_paths
    global image_in
    # global Image_paths
    # IMAGE LOCATION
    filenames = filedialog.askopenfilename(multiple= True,
                                               initialdir="/Downloads",
                                               title="Select Image",
                                               filetypes=(("jpg files", "*.jpg"), ("png files", "*.png"), ("jpeg files", "*.jpeg")))

    if len(filenames) == 1:
        display_uploaded_single_image(filenames[0])
        upload_btn.configure(fg_color='black')
    elif len(filenames) > 1:
        display_multi_upload(filenames)
        upload_btn.configure(fg_color='black')
    if filenames:
        for filepath in filenames:
            Image_paths.append(filepath.replace("/", "//"))



def display_uploaded_single_image(filename):
    global image_in
    # OPEN IMAGE AND CONVERT TO TK
    image_in = ctk.CTkImage(Image.open(filename), size=(500, 400))
    upload_label2.configure(image=image_in, text='')
    upload_label2.image = image_in  # Keep a reference to prevent image from being garbage collected
    inner_frame.place_forget()
    upload_label2.pack(expand=True)


def display_multi_upload(filenames):
    global image_multi_list
    global j  # Declare j as global
    j = 0

    for image_in in filenames :
        image_in_list = ctk.CTkImage(Image.open(image_in), size=(500, 400))
        image_multi_list.append(image_in_list)
        upload_label2.configure(image=image_multi_list[j], text='')
        upload_label2.image = image_in  # Keep a reference to prevent image from being garbage collected
        inner_frame.place_forget()
        upload_label2.pack(expand=True)


#FORWARD FUNC
def Forward():
    global j
    j = j + 1
    try:
        upload_label2.configure(image=image_multi_list[j])
    except:
        j = -1
        Forward()  # calling the forward function


# BACKWARD FUNC
def Backward():
    global j  # creating a global variable j
    j = j - 1
    try:
        upload_label2.configure(image=image_multi_list[j])
    except:
        j = 0
        Backward()  # calling the forward function


def display_downloaded():
    global image_multi_list
    global j
    j = 0
    image_multi_list.clear()
    for receive_server in image_paths_to_receive_from_server:
        #array
        array_multi_list = app.get_from_s3(app.bucket_name, receive_server)
        # Convert ndarray to a PIL Image
        pil_image = Image.fromarray(array_multi_list)
        # Convert the PIL Image to a CTkImage
        ctk_image_multi_list = ctk.CTkImage(pil_image, size=(500, 400))
        image_multi_list.append(ctk_image_multi_list)
        upload_label2.configure(image=image_multi_list[j], text='')
        upload_label2.image = image_multi_list[j]  # Keep a reference to prevent image from being garbage collected
        inner_frame.place_forget()
        upload_label2.pack(expand=True)

def download_then_forget():
    display_download_btn.place_forget()
    app.download(image_paths_to_receive_from_server)


root = tk.Tk()
root.title("CLOUD IMAGE")
root.geometry("1000x600")

# #ICON
# my_font = ctk.CTkFont(family='PT Sans Narrow', size=16, weight="bold")
# cloud_image_label = ctk.CTkLabel(root, text='Image Pro', font=my_font, text_color='black')
# cloud_image_label.place(x=80, y=20)

#TODO: IF I WANT TO MAKE WINDOW BIGGER DONT FORGET TO CHANGE .RESIZE HENA
#BACKGROUND
image = Image.open('greybg.jpeg').resize((1000, 600))
background_image = ImageTk.PhotoImage(image)
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# UPLOAD FRAME
upload_frame = ctk.CTkFrame(root, border_width=3, border_color="green",
                     fg_color="white",width=500, height=400)
upload_frame.place(x=400, y=60)
#TODO: I CHANGED W WA H HENA TO 10 MEN 400
upload_label2 = ctk.CTkLabel(upload_frame, text='', width=100, height=100)


#INNER FRAME IN UPLOAD
inner_frame= ctk.CTkFrame(upload_frame, fg_color="white", border_color="green", width=480, height=380, border_width=3)
inner_frame.place(x=10, y=10)


#UPLOAD LABEL
upload_label = ctk.CTkLabel(inner_frame, text="Upload Photo", font=("American Typewriter", 16), text_color='black')
upload_label.place(x=200, y=180)

upload_label_img_icon= ctk.CTkImage(Image.open('icon_upload.jpeg'), size= (70, 70))
upload_image_label= ctk.CTkLabel(inner_frame, image=upload_label_img_icon, text='')
upload_image_label.place(x=200,y=110)

#UPLOAD BUTTON
upload_btn = ctk.CTkButton(root, width=120, corner_radius=60, fg_color='#142C14', text_color= 'white', hover_color= '#8DA750', text="Upload", command=open)
upload_btn.place(x=400, y=500)
#TODO : DOWNLOAD BTN

#BACK BTN
back_button_photo = ctk.CTkImage(Image.open('Back_Button.png'),size=(30,30))
back_button_btn = ctk.CTkButton(root, text='', fg_color='#f2f2f2', image=back_button_photo, width=5, border_width=0, command= Forward)
back_button_btn.place(x=350, y=270)

#NEXT BTN
next_button_photo = ctk.CTkImage(Image.open('forward_button.png'),size=(34,34))
next_button_btn = ctk.CTkButton(root, image= next_button_photo, text='', fg_color='#ebeae9', width=5, border_width=0, command= Backward)
next_button_btn.place(x=905, y=270)

#IMAGE SHOW BOX
# image_show_box_photo= ctk.CTkImage(Image.open('forward_button.png'),size=(38,38))
# image_show_box_label= ctk.CTkLabel(upload_frame, image= image_show_box_photo,border=0)
# image_show_box_label.place(x=20,y=20)

#LABEL FOR BTNS
btns_label = ctk.CTkLabel(root, text="Select the type of processing for your image:", fg_color= 'transparent',text_color='black', font=("PT Sans Narrow", 17))
btns_label.place(x=50, y=120)

# THREE BUTTONS for Image Processing functions
edge_detection = ctk.CTkButton(root, width=240, corner_radius=20, fg_color='green', text_color='white', hover_color='#8DA750', text=" Edge Detection", command=lambda: identify_clicked_button("edge_detection"))
edge_detection.place(x=80, y=180)
color_inversion = ctk.CTkButton(root, width=240, corner_radius=20, fg_color='green', text_color='white', hover_color='#8DA750', text=" Color Invsersion", command=lambda: identify_clicked_button("color_manipulation"))
color_inversion.place(x=80, y=220)
blur = ctk.CTkButton(root, width=240, corner_radius=20, fg_color='green', text_color='white', hover_color='#8DA750', text=" Image Blurring", command=lambda: identify_clicked_button("blurring"))
blur.place(x=80, y=260)

grayscale = ctk.CTkButton(root, width=240, corner_radius=20, fg_color='green', text_color='white', hover_color='#8DA750', text=" Image grayscale", command=lambda: identify_clicked_button("grayscale"))
grayscale.place(x=80, y=300)
thresholding = ctk.CTkButton(root, width=240, corner_radius=20, fg_color='green', text_color='white', hover_color='#8DA750', text=" Image thresholding", command=lambda: identify_clicked_button("thresholding"))
thresholding.place(x=80, y=340)
dilation = ctk.CTkButton(root, width=240, corner_radius=20, fg_color='green', text_color='white', hover_color='#8DA750', text=" Image dilation", command=lambda: identify_clicked_button("dilation"))
dilation.place(x=80, y=380)
erosion = ctk.CTkButton(root, width=240, corner_radius=20, fg_color='green', text_color='white', hover_color='#8DA750', text=" Image erosion", command=lambda: identify_clicked_button("erosion"))
erosion.place(x=80, y=420)

#DOWNLOAD BTN
download_btn = ctk.CTkButton(root, width=240, corner_radius=20, fg_color='black', text_color='white', hover_color='#8DA750', text=" Download Your Image", command= lambda: download_then_forget())
download_btn.place(x=80, y=475)

#DISPLAY DOWNLOAD BTN
display_download_btn = ctk.CTkButton(root, width=240,corner_radius=20 ,fg_color='black',text_color= 'white',hover_color='#8DA750', text=" Display Your Processed Image", command=lambda: display_downloaded())
display_download_btn.place(x=80, y=510)

#PROGRESS BAR
progress_bar= ctk.CTkProgressBar(root, orientation="horizontal", width=350, height=30,fg_color='light grey',progress_color='#8DA750', determinate_speed=.5)
progress_bar.place(x=540, y=500)
progress_bar.set(0)

#TODO: IMPLMENT EL FUNCTION THAT MOVE THE PROGRESS BAR
'''
EXAMPLE
def clicker():
	my_progressbar.step()
	my_label.configure(text=(int(my_progressbar.get()*100)))

'''

root.mainloop()