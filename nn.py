import cv2          # Open Computer Vision Library for Python
import numpy as np  # NumPy for array work
import os
import uuid         # For generating random filenames

def colorize_image(image_path, output_dir):

    # Load the neural network model
    # The neural network model is pretrained by @https://github.com/richzhang, this is just my implementation of his NN model to BW-LBA-BGR colorization
    # My motivation for this project was to colorize old black-and-white photos of my ancestors, with guidance from @github.com/opencv.

    
    # Paths to the model files
    prototext_path = './models/colorization_deploy_v2.prototxt'             # Network configuration  
    model_path = './models/colorization_release_v2.caffemodel'              # Pretrained weights
    kernel_path = './models/pts_in_hull.npy'                                # Cluster centers for ab color space
    

    # Initialize the neural network as a deep neural network (DNN)
    net = cv2.dnn.readNetFromCaffe(prototext_path, model_path)
    points = np.load(kernel_path)
    points = points.transpose().reshape(2, 313, 1, 1)                       # Reshape to match the expected input
    net.getLayer(net.getLayerId("class8_ab")).blobs = [points.astype(np.float32)] # Load cluster centers
    net.getLayer(net.getLayerId("conv8_313_rh")).blobs = [np.full([1, 313], 2.606, dtype="float32")] # Scaling factors


     # Read the input grayscale image received from Flask
    input_image = cv2.imread(image_path)
    normalized = input_image.astype("float32") / 255.0                      # Normalize the image to x ∈ [0, 1] range

    # Convert the image to LAB color space
    # LAB is another way to represent colors that is easier for neural networks to work with, L - Lightness and A/B (color) channels
    lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)                        # Converting BGR to LAB color space
    resized = cv2.resize(lab, (224, 224))                                    # The model was trained on a 224x224 dimensioned training set, that is why the image needs to be resized
    L = cv2.split(resized)[0]                                                # Extracting the L - lightness channel 
    L -= 50                                                                  # Mean value subtraction - This value can be played with for different types of results


    # Run the neural network to predict the color channels
    net.setInput(cv2.dnn.blobFromImage(L))                                   # Set the L channel as input to the network
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))                      # Get the predicted A and B channels
    
    # Resize the predicted AB channels back to the original image size
    ab = cv2.resize(ab, (input_image.shape[1], input_image.shape[0]))    
   
    # Combine the original L channel with the predicted AB channels
    L = cv2.split(lab)[0]                                                    # Re-extract the L channel from the original image
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)            #Conjoining the L channel with the A/B channels
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)                   # Convert from LAB to BGR color space
    colorized = (255.0 * colorized).astype("uint8")                          # Getting back the 0-255 values from 0-1 because of past division. Convert to uint8 type


    # Generate the output filename 
    random_filename = str(uuid.uuid4()) + '.jpg'                             #Generate a random filename
    output_filename = 'colorized_' + random_filename                         #Having 'colorized_' prefixed to it
    
    # Create the path for saving the file
    output_path = os.path.join(output_dir, output_filename)                  # Constructing the output_path
    cv2.imwrite(output_path, colorized)                                      # And now it takes the colorized np array and outputs it as an actual image
                                                                             # Via the cv2 library's .imwrite() function
    
    return output_filename                                                   # Return the filename for further use