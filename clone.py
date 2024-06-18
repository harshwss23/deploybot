import os
from deepface import DeepFace
import numpy as np

import requests
from telegram import Update
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes,MessageHandler, filters, Updater,CallbackContext
import pandas as pd 
from fpdf import FPDF
import cv2 as cv
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from urllib.request import urlopen, HTTPError

data=pd.read_csv('new.csv')

# Load environment variables from the .env file
TOKEN='6702741814:AAGQPt5lYsk7lKeBH4GWA9QmVzs_SeeUrGM'
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: CallbackContext) -> None:
    # Create a custom keyboard with buttons
    keyboard = [
        ['Search By Name'], ['Search By Roll Number'],
        ['Search By Wing'],['Search By Image']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Send a message with the custom keyboard
    await update.message.reply_text('Choose an option:', reply_markup=reply_markup)


async def handle_name(update : Update, context : ContextTypes.DEFAULT_TYPE) -> None:
       
        input = update.message.text
        print(input)
        if(input == "Search By Name"):
            await update.message.reply_text("Enter any part of the name you know")
            return
        if(input == "Search By Roll Number"):
            await update.message.reply_text("Enter full Roll Number")
            return
        if(input == "Search By Wing"):
            await update.message.reply_text("Enter the Wing in Capital with no hyphens")
            return
        if(input == "Search By Image"):
            await update.message.reply_text("Upload the Image with face Zoomed in preferably with face facing Towards Camera(Feature not working now)")
            return
        input = input.upper()
        if(input == 'HI' or input == 'HELLO'):
            await update.message.reply_text("Hi, I am a bot, I do the following works")
            return
        rollnumberslist = []
        for i in range(0,1208):
            if input in data['Names'][i].upper():
               rollnumberslist.append((data['Roll Numbers'][i], i))
        rollnumberslist.sort()
        emptystr = ""
        if(len(rollnumberslist) > 0):
            for i in range(0, len(rollnumberslist)):
                emptystr = emptystr + data['Names'][rollnumberslist[i][1]] + " : " + str(data['Roll Numbers'][rollnumberslist[i][1]]) +  "\n"
            await update.message.reply_text(emptystr)
        if(len(rollnumberslist) == 0):
            await update.message.reply_text("No Matches Found")

 #pool

async def face_detection(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = await context.bot.get_file(file_id)
        file_path = file_info.file_path
        response = requests.get(file_path, stream=True)
        img_path="downloads/photototest.jpg"
        with open('downloads/photototest.jpg', 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    best_match=[]
    index_value=[]
    for i in range(len(data['Student Photo'])):
        try:
            img=urlopen(data['Student Photo'][i]).read()
            test_img_path="downloads/target{}.jpg".format(data['Roll Numbers'][i])
            open(test_img_path, 'wb').write(img)
            result=DeepFace.verify(img_path,test_img_path)
            output=result['verified']
            distance_value=result['distance']
            os.remove(test_img_path)
            print(i)
            if output==True:
                best_match.append(distance_value)
                index_value.append(i)
            else:
                continue
        except:
            continue
    os.remove(img_path)
        
    arr_best_match=np.array(best_match)
    sorted_arr=np.sort(arr_best_match)[:10]
    list_best_match=sorted_arr.tolist()
    for i in range(len(list_best_match)):
        x=best_match.index(list_best_match[i])
        data_index=index_value[x]
        await update.message.reply_text(data['Names'][data_index])
        print(data_index)
    print(data['Names'][data_index])


#To handle wing
async def handle_wing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    names = ""
    input = update.message.text
    input = input[:len(input)-1] + '-' + input[-1]
    pdf=FPDF()
    for i in range(len(data['Roll Numbers'])):
        if(input == data['Address'][i][:len(input)]):
            names = names + data['Names'][i] +"("+data['Address'][i].split(',')[0]+")"+ "\n"
            print(data['Names'][i])
            pdf.add_page()
            img=urlopen(data['Student Photo'][i]).read()
            img_path="downloads/target{}.jpg".format(data['Roll Numbers'][i])
            open(img_path, 'wb').write(img)
            pdf.image(img_path, x= 50, y=50, w=120)
            os.remove(img_path)
    pdf.output("Photos{}.pdf".format(update.message.chat_id))
    await context.bot.send_document(chat_id=update.message.chat_id,document="Photos{}.pdf".format(update.message.chat_id),caption=names)
    # await update.message.reply_text(names)


#To handle roll No.
async def handle_roll_no(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        roll_no=update.message.text
        print(roll_no)
        index_value=0
        if roll_no.isdigit() and len(roll_no)==6:
                for i in range(len(data['Roll Numbers'])):
                    if str(data['Roll Numbers'][i])==roll_no:
                        sliced = data['Address'][i].split(',')
                        chat_id=update.message.chat_id
                        if i==1045:
                            img_path="my_dp.jpg"
                            await context.bot.send_photo(chat_id=chat_id, photo=img_path, caption=f"""Student Name:-  {data['Names'][i]}\nStudent Roll:-  {data['Roll Numbers'][i]}\nStudent Room No.:-  {sliced[0]}\nStudent Hall :- {sliced[1]}""")
                        else:
                            img=urlopen(data['Student Photo'][i]).read()
                            img_path="target{}.jpg".format(data['Roll Numbers'][i])
                            open(img_path, 'wb').write(img)
                            await context.bot.send_photo(chat_id=chat_id, photo=img_path, caption=f"""Student Name:-  {data['Names'][i]}\nStudent Roll:-  {data['Roll Numbers'][i]}\nStudent Room No.:-  {sliced[0]}\nStudent Hall :- {sliced[1]}""")
                            os.remove(img_path)
                    
                        await context.bot.send_message(chat_id=chat_id, text="Hello :) ")
                        return
                    else:
                        continue
        

                        await update.message.reply_text("No such student found")
def main():
    if not TOKEN:
        print("Error: BOT_TOKEN is not set.")
        return
#E-1 E1-1 C-1
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("Start", start))
    application.add_handler(MessageHandler(filters.Regex(r'^\d{6}$'), handle_roll_no))
    application.add_handler(MessageHandler(filters.Regex(r'([A-Za-z][1-6])'), handle_wing))
    application.add_handler(MessageHandler(filters.Regex(r'^[A-Za-z]+(\s[A-Za-z]+)*$'), handle_name))
    application.add_handler(MessageHandler(filters.PHOTO, face_detection))



    # Start the Bot
    application.run_polling()


if __name__ == '__main__':
    main()
