import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from PIL import Image, ImageDraw, ImageFont
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField, SubmitField, validators
from flask_mail import Mail, Message
import random
import string


app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Ensure a directory for saving signature images exists
if not os.path.exists('static/signatures'):
    os.makedirs('static/signatures')

def capitalize_name(name):
    """Capitalize the first letters of the first and last names."""
    return ' '.join([word.capitalize() for word in name.split()])

def get_font_paths():
    """Get all font file paths from the static/fonts directory."""
    font_directory = 'static/fonts'
    fonts = []
    for font_file in os.listdir(font_directory):
        if font_file.endswith('.ttf'):  # Only include TTF fonts
            fonts.append(os.path.join(font_directory, font_file))
    return fonts



class ContactForm(FlaskForm):
    name = StringField('Name', [validators.InputRequired()])
    surname = StringField('Surname', [validators.InputRequired()])
    email = EmailField('Email', [validators.InputRequired(), validators.Email()])
    phone = StringField('Phone', [validators.InputRequired()])
    message = TextAreaField('Message', [validators.InputRequired()])
    captcha = StringField('Captcha', [validators.InputRequired()])
    submit = SubmitField('Submit')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    # Generate a simple captcha
    captcha_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    if request.method == 'POST':
        if form.validate_on_submit() and form.captcha.data == captcha_code:
            msg = Message('New Contact Form Submission', recipients=['sachinreal2003@gmail.com'])
            msg.body = f"""
            Name: {form.name.data}
            Surname: {form.surname.data}
            Email: {form.email.data}
            Phone: {form.phone.data}
            Message: {form.message.data}
            """
            mail.send(msg)
            flash('Your message has been sent!', 'success')
            return redirect(url_for('contact'))
        else:
            flash('Invalid captcha or form data. Please try again.', 'danger')

    return render_template('pages/contact.html', form=form, captcha_code=captcha_code)



# making contact form here
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sachinreal2003@gmail.com'
app.config['MAIL_PASSWORD'] = 'YOUR_GMAIL_APP_PASSWORD'  # Use an app password for security
app.config['MAIL_DEFAULT_SENDER'] = 'sachinreal2003@gmail.com'
mail = Mail(app)




def generate_signature_image(text, font_path, index):
    """Generate both a display and high-resolution version of the signature image."""
    
    # **1. Create Full HD (1920x1080) Image for Download**
    full_hd_img = Image.new('RGBA', (3840, 2160), (255, 255, 255, 0))  # 4K resolution
    d_full_hd = ImageDraw.Draw(full_hd_img)

    # Load the font and set the font size for the high-res version
    full_hd_font = ImageFont.truetype(font_path, 250)

    # Determine the text bounding box to center it for high resolution
    bbox_hd = d_full_hd.textbbox((0, 0), text, font=full_hd_font)
    text_width_hd, text_height_hd = bbox_hd[2] - bbox_hd[0], bbox_hd[3] - bbox_hd[1]
    position_hd = ((full_hd_img.width - text_width_hd) // 2, (full_hd_img.height - text_height_hd) // 2)

    # Add the text to the high-resolution image
    d_full_hd.text(position_hd, text, fill='black', font=full_hd_font)

    # Save the high-resolution image (for download)
    hd_image_path = f'static/signatures/signature_hd_{index}.png'
    full_hd_img.save(hd_image_path, format="PNG")  # Save high-res image for download

    # **2. Create a Smaller Image for Display (e.g., 400x100)**
    display_img = Image.new('RGBA', (400, 100), (255, 255, 255, 0))  # Smaller image for display
    d_display = ImageDraw.Draw(display_img)

    # Load the font and set the font size for the display version
    display_font = ImageFont.truetype(font_path, 40)

    # Determine the text bounding box to center it for display version
    bbox_display = d_display.textbbox((0, 0), text, font=display_font)
    text_width_display, text_height_display = bbox_display[2] - bbox_display[0], bbox_display[3] - bbox_display[1]
    position_display = ((display_img.width - text_width_display) // 2, (display_img.height - text_height_display) // 2)

    # Add the text to the display image
    d_display.text(position_display, text, fill='black', font=display_font)

    # Save the smaller display image
    display_image_path = f'static/signatures/signature_display_{index}.png'
    display_img.save(display_image_path, format="PNG")  # Save smaller image for display

    # Return both the display path and high-res path
    return display_image_path, hd_image_path



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    name = request.form.get('name')
    if name:
        stylish_name = capitalize_name(name)
        signature_paths = []
        fonts = get_font_paths()
        
        if not fonts:
            return "No fonts found in the static/fonts directory.", 500
        
        # Generate 10 signature images with different fonts
        for i in range(10):
            font_path = random.choice(fonts)
            signature_path = generate_signature_image(stylish_name, font_path, i)
            signature_paths.append(signature_path)
        return render_template('result.html', signatures=signature_paths)
    return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download(filename):
    """Send the signature file for download."""
    return send_file(filename, as_attachment=True)

@app.route('/another')
def another():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
