from flask import Flask, flash, redirect, render_template, request, url_for, send_file
from werkzeug.utils import secure_filename
import os
from nn import colorize_image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}                                         # Allowed image extensions for upload

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'                                         # Access key
app.config['UPLOAD_FOLDER'] = 'static/original'                                     # The upload folder for original images
app.config['NORMALIZED_FOLDER'] = 'static/normalized'                               # The download folder for processed normalized images

def allowed_file(filename):  # Checks if the file has an allowed extension
    # Splits the filename at the last period to separate the extension and checks if it's in the allowed list
    # .lower() ensures the check is case-insensitive
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS  

# Python Intensive Course - Eric Matthes helped me greatly with these "pythonic" functions

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == "POST":                                                    # File uploads are handled via POST requests
        file = request.files['file']                                                # Retrives the file
        if file.filename == '':                                                     # Accounts if there was no file selected
            flash('No selected file')           
            return redirect(request.url)
        if file and allowed_file(file.filename):                                    # If a valid file is selected and its extension is allowed:
            filename = secure_filename(file.filename)   
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)        # Constructs the path where the image will be saved
            file.save(image_path)                                                   # Saves the image
            normalized_filename = colorize_image(image_path, app.config['NORMALIZED_FOLDER'])       
            return redirect(url_for('finished', filename=normalized_filename))      # Redirects to display the processed image
        else:
            flash('Invalid file type')                      
            return redirect(request.url)
    else:
        return render_template('index.html')


@app.route('/finished', methods=['GET', 'POST'])
def finished():
    if request.method == "POST":
        return redirect("/")
    else:   
        filename = request.args.get('filename')                                     # Gets the processed image filename
        return render_template('finished.html', filename=filename)                  # Passes the image to the HTML template


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['NORMALIZED_FOLDER'], filename)             # Constructs the file path for the processed image
    return send_file(file_path, as_attachment=True)                                 # Sends the file for download using Flask's send_file


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)                                  # Forwarded to port 5003 (adjusted due to authorization issues)

