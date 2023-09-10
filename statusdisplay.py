#!/usr/bin/env python3
from flask import Flask, jsonify, request, render_template
from PIL import Image, ImageDraw, ImageFont
from displayhatmini import DisplayHATMini
import threading
import os

app = Flask(__name__)

width = 320
height = 240

# Initialize DisplayHATMini for LED control
buffer = Image.new("RGB", (width, height))
dispmini = DisplayHATMini(buffer)
draw = ImageDraw.Draw(buffer)
font = ImageFont.load_default()

display_event = threading.Event()

@app.route('/display', methods=['GET'])
def display_image_endpoint():

    valid_image_names = [f for f in os.listdir('images') if f.endswith(('.jpg', '.png'))]
    new_image_name = request.args.get('imageName', default=None, type=str)
    # Check if the new_image_name is valid
    if new_image_name not in valid_image_names:
        return jsonify({'error': 'Invalid image name. Please use a valid one.'}), 400

    display_text = request.args.get('text', default=None, type=str)
    # TODO: If empty text and limit to nr of characters
    font_size    = request.args.get('fontSize', default=None, type=int)
    # TODO: Limit size
    led_color = request.args.get('ledColor', default=None, type=str)

    # Send a event message to threads
    display_event.set()

    # Font settings
    # https://www.fontspace.com/falling-sky-font-f22358
    font = ImageFont.truetype("fonts/FallingSkyExtrabold-redB.otf", size=font_size)

    # Start the display in a separate thread
    threading.Thread(target=display_image_and_control_led, args=(display_event, f"images/{new_image_name}", display_text, font, led_color)).start()

    return jsonify({'message': f"Image {new_image_name}.jpg will be displayed."}), 200

def display_image_and_control_led(display_event, image_file_path, display_text, font, led_color):

    # Control the LED (set it to red here, but you can change as needed)
 
    r, g, b = map(float, led_color.split(','))

    dispmini.set_led(r, g, b)
    

    im = Image.open(image_file_path)
    im2 = im.resize((width, height))
    buffer.paste(im2)

    draw.multiline_text((160, 120), text=display_text, font=font, fill="MintCream", anchor="mm", align="center")

    # Continuously display the image until a new image is selected
    while True:
        dispmini.display()

        # Check if a new request is called and the threading event get set
        if display_event.is_set():        
            break

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
