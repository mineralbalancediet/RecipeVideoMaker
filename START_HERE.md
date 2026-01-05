START HERE

(for Nutritionists & Non-Technical Users)

This folder helps you turn recipes from the
Mineral Balance Diet Android App
into short narrated videos.

You do not need programming knowledge.
You only need to follow the steps below, one by one.

WHAT THIS TOOL DOES

It turns:

• Recipe screens on your phone
• Simple text you write

into:

• One short video file with voice narration

The final video file is named output.mp4.

YOU ONLY NEED TO SET THIS UP ONCE

The setup steps below are done one time only.
After that, making videos is very easy and repeatable.

STEP 1 — INSTALL PYTHON (ONE TIME)

Python is a helper program that allows this tool to run.
You do not need to learn programming.

What to do:

• Open a web browser
• Go to python.org
• Download Python 3
• Run the installer

IMPORTANT:

During installation, make sure the option
“Add Python to PATH” is checked.

When installation finishes, Python is ready.

STEP 2 — INSTALL FFMPEG (ONE TIME)

ffmpeg is used to create the video.

What to do:

• Open a web browser
• Search for “ffmpeg Windows download”
• Download a Windows version

After downloading:

• Open the downloaded folder
• Find two files:
– ffmpeg.exe
– ffprobe.exe

• Copy BOTH files
• Paste them into this folder
(the same folder as RecipeVideoMaker)

That’s all.

STEP 3 — CONNECT YOUR ANDROID PHONE (ONE TIME)

You need to allow the computer to see your phone screen.

On your Android phone:

• Open Settings
• Go to About phone
• Tap Build number many times
• Developer mode will turn on

Then:

• Go back to Settings
• Open Developer options
• Turn ON USB debugging

Now:

• Connect your phone to the computer using a USB cable
• When asked on the phone, tap Allow

STEP 4 — FIND YOUR DEVICE ID (ONE TIME)

Your device ID is simply how the computer recognizes your phone.
You do not need to understand it — only copy it once.

How to find the device ID

• Make sure your phone is connected by USB
• Make sure USB debugging is ON

On your computer:

• Open the Windows command window
(Click Start, type cmd, press Enter)

In that window, type:

adb devices

Press Enter.

You will see a short list.
You should see one line containing:

• A group of letters and numbers
• Followed by the word device

Example (your text will be different):

26111JEGR11210 device

?? The letters and numbers are your device ID.

STEP 5 — PUT THE DEVICE ID INTO device.txt (ONE TIME)

In this folder there is a file named device.txt.

What to do:

• Open device.txt
• Copy the device ID you just saw
• Paste it into the file
• Make sure it is on one line only
• Save the file

You only need to do this once.

If you ever change phones, you can repeat this step.

AFTER SETUP: MAKING A VIDEO (EVERY TIME)

The steps below are what you repeat
each time you want to make a new video.

STEP A — OPEN THE RECIPE IN THE APP

• Open the Mineral Balance Diet app on your phone
• Open the recipe you want to make a video for
• Go to the first recipe screen

STEP B — TAKE SCREENSHOTS (ONE BY ONE)

In this folder there is a file named shot.bat.

This file takes one screenshot each time you use it.

How it works:

• It captures whatever is currently shown on your phone
• It saves the image into this folder
• Images are named automatically:
01.png, 02.png, 03.png, and so on

What to do:

• Phone shows the first recipe screen
• Use shot.bat with number 1
• This creates 01.png

Then:

• Swipe to the next recipe screen on your phone
• Use shot.bat with number 2
• This creates 02.png

Repeat until all recipe screens are captured.

Important rules:

• One screenshot = one page
• Always follow the recipe order
• Do not skip numbers

STEP C — WRITE THE VOICE TEXT

In this folder there is a file named script.txt.

This file contains the words spoken in the video.

Rules:

• One line = one image
• First line describes 01.png
• Second line describes 02.png
• Third line describes 03.png

Keep sentences short and clear.

STEP D — MAKE THE VIDEO

In this folder there is a file named RecipeVideoMaker.py.

To make the video, you run it from the Windows command window.

What to do:

• Open the Windows command window
(Click Start, type cmd, press Enter)

• Make sure the command window is working inside this project folder
(the folder that contains RecipeVideoMaker.py)

In the command window, type:

python RecipeVideoMaker.py

Press Enter.

When you run it:

• It reads the images (01.png, 02.png, …)
• It reads your text in script.txt
• It generates voice narration
• It combines everything into one video

When finished, you will see:

• output.mp4

This is your final video.

IMPORTANT NOTES

• Images must be named 01.png, 02.png, etc.
• Do not rename files
• Keep everything in one folder
