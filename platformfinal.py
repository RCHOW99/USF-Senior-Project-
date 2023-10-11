import mysql.connector
import tkinter as tk
import schedule
from PIL import ImageTk, Image
import io
import os
from datetime import datetime
from gpiozero import MotionSensor


def get_day():
    global day
    day = datetime.now()


# This function gets the blobs from database and stores them into the advertisements directory. This function also returns how many advertisements are in the db
def retrieve_image(host1, port1, database1, user1, password1, namecolumnindex, datacolumnindex, plnamecolumnindex, pldatacolumnindex,  query1, query2, query3, filedir):
    global advertisements
    global adcount
    global connection
    global cursor
    global filenames
    advertisements = []
    filenames = []
    connection = mysql.connector.connect(host=host1, port=port1, database=database1, user=user1, password=password1)
    cursor = connection.cursor()
    # This is used for scheduling mechanism, there are certain amount of ads that play per day, we are probably allowing 6 ads to play equally per minute at 10 second intervals
    # This part of the program gets the current day, and gets the image ads in the database with the current day
    # This scheduling mechanism is supposed to be on a monthly basis.
    get_day()
    where_day = ""
    if day.strftime('%A') == "Monday":
        where_day = day.strftime('%A')
    if day.strftime('%A') == "Tuesday":
        where_day = day.strftime('%A')
    if day.strftime('%A') == "Wednesday":
        where_day = day.strftime('%A')
    if day.strftime('%A') == "Thursday":
        where_day = day.strftime('%A')
    if day.strftime('%A') == "Friday":
        where_day = day.strftime('%A')
    # Extract the image file name and image that are in the current day
    full_query1 = query1 + '\'' + where_day + '\''
    cursor.execute(full_query1)
    data = cursor.fetchall()
    for row in data:
        imagedata = row[datacolumnindex]
        namedata = row[namecolumnindex]
        filenames.append(namedata)
        image = Image.open(io.BytesIO(imagedata))
        filepath = filedir + namedata
        rs_image = image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        rs_image.save(filepath)
        advertisements.append(ImageTk.PhotoImage(file=filepath))

    # Get the ad count to use for other code in the program
    full_query2 = query2 + '\'' + where_day + '\''
    cursor.execute(full_query2)
    data2 = cursor.fetchall()
    adcount = data2[0][0]


    if adcount < 6:
        cursor.execute(query3)
        data2 = cursor.fetchall()
        for row2 in data2[:6-adcount]:
                imagedata = row2[pldatacolumnindex]
                namedata = row2[plnamecolumnindex]
                image = Image.open(io.BytesIO(imagedata))
                filepath = filedir + namedata
                rs_image = image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
                rs_image.save(filepath)
                advertisements.append(ImageTk.PhotoImage(file=filepath))
        adcount=6


    if adcount ==0:
        cursor.execute(query3)
        data2 = cursor.fetchall()
        for row2 in data2:
                imagedata = row2[pldatacolumnindex]
                namedata = row2[plnamecolumnindex]
                filenames.append(namedata)
                image = Image.open(io.BytesIO(imagedata))
                filepath = filedir + namedata
                rs_image = image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
                rs_image.save(filepath)
                advertisements.append(ImageTk.PhotoImage(file=filepath))
        adcount=6


def create_window():
    global window
    global canvas
    global screen_width
    global screen_height
    # Set Screen Specifications, create root window
    window = tk.Tk()
    window.attributes('-fullscreen', True)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # Create a Canvas that has the images and is set in top of the root window
    canvas = tk.Canvas(window, width=screen_width, height=screen_height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)


def create_counters():
    global count, counters, counter1, counter2, counter3, counter4, counter5, counter6
    # These counter variable will increment to show view count via pir sensor.
    counter1 = 1
    counter2 = 0
    counter3 = 0
    counter4 = 0
    counter5 = 0
    counter6 = 0
    counters = [counter1, counter2, counter3, counter4, counter5, counter6]
    # pir = MotionSensor(4)
    # This variable is used as the beginning variable to keep incrementing the list
    count = -1
    # This program will cycle through 6 advertisement images for the whole day, hence 6 counter variables


# Function that changes the images
def cycle():
    global count
    if count == adcount - 1:
        canvas.create_image(0, 0, image=advertisements[0], anchor='nw')
        count = 0
        counters[0] += 1
    else:
        canvas.create_image(0, 0, image=advertisements[count + 1], anchor='nw')
        count += 1
        if count == 1:
            counters[1] += 1
        if count == 2:
            counters[2] += 1
        if count == 3:
            counters[3] += 1
        if count == 4:
            counters[4] += 1
        if count == 5:
            counters[5] += 1
    # Loop portion of the function
    # The number is the time, ie 10,000 is 10 seconds
    window.after(2000, cycle)
    schedule.run_pending()

# Function that changes the images with PIR
# def cyclepir():
#     global count
#     if count == adcount - 1:
#         canvas.create_image(0, 0, image=advertisements[0], anchor='nw')
#         count = 0
#         pir.wait_for_motion(timeout=5)
#         if pir.motion_detected:
#           counters[0] += 1
#     else:
#        canvas.create_image(0, 0, image=advertisements[count + 1], anchor='nw')
#        pir.wait_for_motion(timeout=5)
#        if ((count == 1) and (pir.motion_detected)):
#         counters[1] += 1
#        if ((count == 2) and (pir.motion_detected)):
#         counters[2] += 1
#        if ((count == 3) and (pir.motion_detected)):
#         counters[3] += 1
#        if ((count == 4) and (pir.motion_detected)):
#         counters[4] += 1
#        if ((count == 5) and (pir.motion_detected)):
#         counters[6] += 1

#     # Loop portion of the function
#     # The number is the time, ie 10,000 is 10 seconds
#     window.after(2000, cycle)
#     schedule.run_pending()


def remove_images(dir):
    # Code referenced from https://www.techiedelight.com/delete-all-files-directory-python/
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

def update_view_count():
    for i in range(len(filenames)):
        insertquery = "Update p2.Advertisements INNER JOIN p2.Images on p2.Advertisements.imageID = p2.Images.imageID set p2.Advertisements.displayCounter =" + str(counters[i]) + " where p2.Images.imageName =" + '\'' + filenames[i] + '\''
        iq = insertquery
        cursor.execute(iq)
        connection.commit()


image_query = "select * from Images inner join Advertisements on Images.imageID = Advertisements.imageID where adApproved = 1 and adPaused !=1 and days = "
count_query = "select count(*) from Images inner join Advertisements on Images.imageID = Advertisements.imageID where adApproved = 1 and adPaused !=1 and days = "
placeholder_query = "Select * from PlaceholderImages"



# # This is the folder where the advertisements are stored
filedir = "C:/Users/Raad/Desktop/PLATFORM IMAGES/"
Queries = [image_query, count_query, placeholder_query]



create_window()
# # # host1, port1, database1, user1, password1, namecolumnindex, datacolumnindex, plnamecolumnindex, pldatacolumnindex,  query1, query2, query3, filedir
retrieve_image("54.91.84.242", "3306", "p2", "remote", "db2023#",1,2, 1, 0, Queries[0], Queries[1],Queries[2], filedir)
create_counters()
schedule.every(2).seconds.do(update_view_count)
cycle()
tk.mainloop()






