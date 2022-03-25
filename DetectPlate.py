from skimage.io import imread
from skimage.filters import threshold_otsu
import matplotlib.pyplot as plt
from skimage.transform import resize  
from flask import Flask,jsonify,request

# car image -> grayscale image -> binary image
#import imutils

def resize_if_necessary(image_to_resize):
        """
        function is used to resize the image before further
        processing if the image is too big. The resize is done
        in such a way that the aspect ratio is still maintained
        Parameters:
        ------------
        image_to_resize: 2D-Array of the image to be resized
        3D array image (RGB channel) can also be resized
        Return:
        --------
        resized image or the original image if resize is not
        neccessary
        """
        height, width = image_to_resize.shape
        ratio = float(width) / height
        # if the image is too big, resize
        if width > 600:
            width = 600
            height = round(width / ratio)
            return resize(image_to_resize, (height, width))

        return image_to_resize

def validate_plate(candidates,license_plate_exact):
        """
        validates the candidate plate objects by using the idea
        of vertical projection to calculate the sum of pixels across
        each column and then find the average.
        This method still needs improvement
        Parameters:
        ------------
        candidate: 3D Array containing 2D arrays of objects that looks
        like license plate
        Returns:
        --------
        a 2D array of the likely license plate region
        """
        
        for each_candidate in candidates:
            height, width = each_candidate.shape
            each_candidate = inverted_threshold(each_candidate)           
            highest_average = 0
            total_white_pixels = 0
            for column in range(width):
                total_white_pixels += sum(each_candidate[:, column])
            
            average = float(total_white_pixels) / width
            if average >= highest_average:
                license_plate_exact = each_candidate
                highest_average = average

        return license_plate_exact



def inverted_threshold(grayscale_image):
        """
        used to invert the threshold of the candidate regions of the plate
        localization process. The inversion was neccessary
        because the license plate area is white dominated which means
        they have a greater gray scale value than the character region
        Parameters:
        -----------
        grayscale_image: 2D array of the gray scale image of the
        candidate region
        Returns:
        --------
        a 2D binary image
        """
        threshold_value = threshold_otsu(grayscale_image)
        return grayscale_image > threshold_value



car_image = imread("car.jpg", as_gray=True)

#car_image = imutils.rotate(car_image, 270)
# car_image = imread("car.png", as_gray=True)
# it should be a 2 dimensional array
print(car_image.shape)
car_image=resize_if_necessary(car_image)

# the next line is not compulsory however, a grey scale pixel
# in skimage ranges between 0 & 1. multiplying it with 255
# will make it range between 0 & 255 (something we can relate better with

gray_car_image = car_image * 255
fig, (ax1, ax2) = plt.subplots(1, 2) 
ax1.imshow(gray_car_image, cmap="gray") 
threshold_value = threshold_otsu(gray_car_image)
binary_car_image = gray_car_image > threshold_value
print(binary_car_image) 
ax2.imshow(binary_car_image, cmap="gray") 
plt.show()   

# CCA (finding connected regions) of binary image


from skimage import measure
from skimage.measure import regionprops
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# this gets all the connected regions and groups them together
label_image = measure.label(binary_car_image)
#print(label_image)

#print(label_image.shape[0]) #width of car img

# getting the maximum width, height and minimum width and height that a license plate can be
plate_dimensions = (0.03*label_image.shape[0], 0.08*label_image.shape[0], 0.15*label_image.shape[1], 0.3*label_image.shape[1])
plate_dimensions2 = (0.08*label_image.shape[0], 0.2*label_image.shape[0], 0.15*label_image.shape[1], 0.4*label_image.shape[1])
min_height, max_height, min_width, max_width = plate_dimensions
plate_objects_cordinates = []
plate_like_objects = []
acc_licence = []

fig, (ax1) = plt.subplots(1)    
ax1.imshow(gray_car_image, cmap="gray")
flag =0
# regionprops creates a list of properties of all the labelled regions
for region in regionprops(label_image):
    # print(region)
    if region.area < 50:        
        #if the region is so small then it's likely not a license plate
        continue
        # the bounding box coordinates
    min_row, min_col, max_row, max_col = region.bbox    

    region_height = max_row - min_row
    region_width = max_col - min_col     

    # ensuring that the region identified satisfies the condition of a typical license plate
    if region_height >= min_height and region_height <= max_height and region_width >= min_width and region_width <= max_width and region_width > region_height:
        flag = 1
        plate_like_objects.append(binary_car_image[min_row:max_row,
                                  min_col:max_col])
        plate_objects_cordinates.append((min_row, min_col,
                                         max_row, max_col))
        rectBorder = patches.Rectangle((min_col, min_row), max_col - min_col, max_row - min_row, edgecolor="red",
                                       linewidth=2, fill=False)
        #ax1.add_patch(rectBorder)  ----
        # let's draw a red rectangle over those regions
if(flag == 1):
    # print(plate_like_objects[0])
    plt.show()
    print(" ")




if(flag==0):
    min_height, max_height, min_width, max_width = plate_dimensions2
    plate_objects_cordinates = []
    plate_like_objects = []

    fig, (ax1) = plt.subplots(1)
    ax1.imshow(gray_car_image, cmap="gray")

    # regionprops creates a list of properties of all the labelled regions
    for region in regionprops(label_image):
        if region.area < 50:
            #if the region is so small then it's likely not a license plate
            continue
            # the bounding box coordinates
        min_row, min_col, max_row, max_col = region.bbox
        
        region_height = max_row - min_row
        region_width = max_col - min_col         

        # ensuring that the region identified satisfies the condition of a typical license plate
        if region_height >= min_height and region_height <= max_height and region_width >= min_width and region_width <= max_width and region_width > region_height:
            # print("hello")
            plate_like_objects.append(binary_car_image[min_row:max_row,
                                      min_col:max_col])
            plate_objects_cordinates.append((min_row, min_col,
                                             max_row, max_col))
            rectBorder = patches.Rectangle((min_col, min_row), max_col - min_col, max_row - min_row, edgecolor="red",
                                           linewidth=2, fill=False)
            ax1.add_patch(rectBorder)
            # let's draw a red rectangle over those regions
    # print(plate_like_objects[0])
    plt.show()
number_of_candidates=len(plate_like_objects)
print(number_of_candidates)
if number_of_candidates == 0:
    print("Licence plate could not be located")
if number_of_candidates == 1:
    acc_licence = inverted_threshold(plate_like_objects[0])
    fig, ax1 = plt.subplots(1)
    ax1.imshow(acc_licence, cmap="gray")    
else:
    acc_licence = validate_plate(plate_like_objects,acc_licence)
 

