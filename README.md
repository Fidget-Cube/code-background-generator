# code-background-generator
Create a scrolling background of binary-encoded secret messages!

Prep:
 - `sudo apt install ffmpeg`
 - `pip3 install -r requirements.txt`
 - Create a list of (ideally short) messages and put them in messages.txt, each on a separate line.

Steps:
 - `python3 generator.py`
 - `ffmpeg -i ./img/%003dtest.bmp output.gif`

output.gif will be your generated background image
