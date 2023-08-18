# Built in packages
import math
import sys
from pathlib import Path

# Matplotlib will need to be installed if it isn't already. This is the only package allowed for this base part of the 
# assignment.
from matplotlib import pyplot
from matplotlib.patches import Rectangle

# import our basic, light-weight png reader library
import imageIO.png

# this function reads an RGB color png file and returns width, height, as well as pixel arrays for r,g,b
def readRGBImageToSeparatePixelArrays(input_filename):

    image_reader = imageIO.png.Reader(filename=input_filename)
    # png reader gives us width and height, as well as RGB data in image_rows (a list of rows of RGB triplets)
    (image_width, image_height, rgb_image_rows, rgb_image_info) = image_reader.read()

    print("read image width={}, height={}".format(image_width, image_height))

    # our pixel arrays are lists of lists, where each inner list stores one row of greyscale pixels
    pixel_array_r = []
    pixel_array_g = []
    pixel_array_b = []

    for row in rgb_image_rows:
        pixel_row_r = []
        pixel_row_g = []
        pixel_row_b = []
        r = 0
        g = 0
        b = 0
        for elem in range(len(row)):
            # RGB triplets are stored consecutively in image_rows
            if elem % 3 == 0:
                r = row[elem]
            elif elem % 3 == 1:
                g = row[elem]
            else:
                b = row[elem]
                pixel_row_r.append(r)
                pixel_row_g.append(g)
                pixel_row_b.append(b)

        pixel_array_r.append(pixel_row_r)
        pixel_array_g.append(pixel_row_g)
        pixel_array_b.append(pixel_row_b)

    return (image_width, image_height, pixel_array_r, pixel_array_g, pixel_array_b)


# a useful shortcut method to create a list of lists based array representation for an image, initialized with a value
def createInitializedGreyscalePixelArray(image_width, image_height, initValue = 0):

    new_array = [[initValue for x in range(image_width)] for y in range(image_height)]
    return new_array


# You can add your own functions here:
def computeRGBtoGreyscale(px_array_r, px_array_g, px_array_b, image_width, image_height):
    greyscale_pixel_array = createInitializedGreyscalePixelArray(image_width, image_height)
    maxVal = 0
    for i in range(image_height):
        for j in range(image_width):
            greyscale_pixel_array[i][j] = round(0.299 * px_array_r[i][j] + 0.587 * px_array_g[i][j] + 0.114 * px_array_b[i][j])
            if maxVal < greyscale_pixel_array[i][j]:
                maxVal = greyscale_pixel_array[i][j]
    for i in range(image_height):
        for j in range(image_width):
            greyscale_pixel_array[i][j] = greyscale_pixel_array[i][j] / maxVal * 255

            #normalized value = (value - min_pixel) / (max_pixel - min_pixel)           
    return greyscale_pixel_array

def applyStdDevFilter(px_array, image_width, image_height):
    result = createInitializedGreyscalePixelArray(image_width, image_height, 0.0)
    
    for i in range(image_height):
        for j in range(image_width):
            if i > 1 and i < image_height-2 and j > 1 and j < image_width-2:
                x = i-2
                y = j-2
                k = i-2    
                p = j-2
                sum = 0
                for a in range(5):
                    for b in range(5):
                        sum = sum + px_array[x][y]
                        y += 1
                    
                    x += 1
                    y = j-2
                mean = sum / 25
                
                get = 0
                for _ in range(5):
                    for __ in range(5):
                        
                        get += math.pow(px_array[k][p] - mean, 2)
                        p += 1
                    
                    k += 1
                    p = j-2
                result[i][j] = math.sqrt(get/25)
    return result

def applyGaussianFilter(px_array, image_width, image_height):
    result = createInitializedGreyscalePixelArray(image_width, image_height)
    
    for i in range(image_height):
        px_array[i].insert(0, px_array[i][0])
        px_array[i].append(px_array[i][len(px_array[i])-1])
    px_array.insert(0, px_array[0])
    px_array.append(px_array[len(px_array)-1])
    
    for i in range(image_height+2):
        for j in range(image_width+2):
            if i != 0 and i != image_height+1 and j != 0 and j != image_width+1:
                get = px_array[i-1][j-1]*(1.0)+px_array[i-1][j]*(2.0)+px_array[i-1][j+1]*(1.0)+px_array[i][j-1]*(2.0)+px_array[i][j]*(4.0)+px_array[i][j+1]*(2.0)+px_array[i+1][j-1]*(1.0)+px_array[i+1][j]*(2.0)+px_array[i+1][j+1]*(1.0)
                result[i-1][j-1] = get/16
    return result

def computeThreshold(px_array, threshold_value, image_width, image_height):
    for i in range(image_height):
        for j in range(image_width):
            if px_array[i][j] >= threshold_value:
                px_array[i][j] = 255
            elif px_array[i][j] <= threshold_value:
                px_array[i][j] = 0
    return px_array

def applyErosion(px_array, image_width, image_height):
    result = createInitializedGreyscalePixelArray(image_width+2, image_height+2)
    for i in range(image_height):
        px_array[i].insert(0,0)
        px_array[i].append(0)
        
    px_array.insert(0,[0]*(image_width+2))
    px_array.append([0]*(image_width+2))
    for i in range(image_height+2):
        for j in range(image_width+2):
            
            if i > 0 and i < image_height+1 and j > 0 and j < image_width+1:
                
                if px_array[i][j] > 0:
                    val = px_array[i][j]
                    x = i-1
                    y = j-1
                    count = 0
                    for a in range(3):
                        for b in range(3):
                            if px_array[x][y] == val:
                                count += 1
                            y += 1
                        x += 1
                        y = j-1
                    if count < 9:
                        result[i][j] = 0
                    else:
                        result[i][j] = 1
    result.pop(0)
    result.pop(-1)
    for i in range(image_height):
        result[i].pop(0)
        result[i].pop(-1)
    
    return result

def applyDilation(px_array, image_width, image_height):
    result = createInitializedGreyscalePixelArray(image_width+2, image_height+2)
    for i in range(image_height):
        px_array[i].insert(0,0)
        px_array[i].append(0)
        
    px_array.insert(0,[0]*(image_width+2))
    px_array.append([0]*(image_width+2))
    for i in range(image_height+2):
        for j in range(image_width+2):
            
            if i > 0 and i < image_height+1 and j > 0 and j < image_width+1:
                
                if px_array[i][j] > 0:
                    
                    x = i-1
                    y = j-1
                    for a in range(3):
                        for b in range(3):
                            result[x][y] = 1
                            y += 1
                        x += 1
                        y = j-1
    result.pop(0)
    result.pop(-1)
    for i in range(image_height):
        result[i].pop(0)
        result[i].pop(-1)
    
    return result
class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)
q = Queue()
x=[-1,0,1,0]
y=[0,1,0,-1]

def bfs_traversal(pixel_array, visited, i, j, image_width, image_height, ccimg, count):
    min_x, min_y, max_x, max_y = image_width,image_height,0,0
    number=0
    
    # add (i,j) into queue adn matk it as visited
    q.enqueue((i,j))
    if min_x > i:
        min_x = i
    if min_y > j:
        min_y = j
    if max_x < i:
        max_x = i
    if max_y < j:
        max_y = j
    visited[i][j]=True

    # do the following till queue becomes empty
    while(not q.isEmpty()):
        # take a position (a,b) from queue
        a,b=q.dequeue()
        # mark the nvalue at (a,b) in ccimg with component count
        ccimg[a][b]=count
        number+=1

        # if any unvisited 1 or 255 values is present in 4 sides of current posution, add it into queue
        for z in range(4):
            newI=a+x[z]
            newJ=b+y[z]
            if newI>=0 and newI<image_height and newJ>=0 and newJ<image_width and not visited[newI][newJ] and pixel_array[newI][newJ]!=0:
                visited[newI][newJ]=True
                q.enqueue((newI,newJ))
                if min_x > newI:
                    min_x = newI
                if min_y > newJ:
                    min_y = newJ
                if max_x < newI:
                    max_x = newI
                if max_y < newJ:
                    max_y = newJ
    
    region_width = max_x - min_x
    region_height = max_y - min_y

# at last retun number of values in the current component
    return [number,region_width+1,region_height+1,min_x+1,min_y+1,max_x+1,max_y+1]

def connectedComponent(px_array, image_width, image_height):
    visited=[]
    ccimg=[]

    # make all the visited values as False and ccimg values as 0
    for i in range(image_height):
        temp1=[]
        temp2=[]
        for j in range(image_width):
            temp1.append(False)
            temp2.append(0)
        visited.append(temp1)
        ccimg.append(temp2)
        
    ccsizedict={}
    count=1

    # traverse px_array from left to right and from top to bottom
    for i in range(image_height):
        for j in range(image_width):
        # if any unvisited and 1 or 255 value pixel is found, then start bsf traversal from that value
            if not visited[i][j] and px_array[i][j]!=0:
                # get number of values in bfs traversal and add it into ccsizedict
                value_list=bfs_traversal(px_array, visited, i, j, image_width, image_height, ccimg, count)
                ccsizedict[count]=value_list
                count+=1


    return (ccimg, ccsizedict)

def separateArraysToRGB(px_array_r, px_array_g, px_array_b, image_width, image_height):
    new_array = [[[0 for c in range(3)] for x in range(image_width)] for y in range(image_height)]

    for y in range(image_height):
        for x in range(image_width):
            new_array[y][x][0] = px_array_r[y][x]
            new_array[y][x][1] = px_array_g[y][x]
            new_array[y][x][2] = px_array_b[y][x]

    return new_array





# This is our code skeleton that performs the barcode detection.
# Feel free to try it on your own images of barcodes, but keep in mind that with our algorithm developed in this assignment,
# we won't detect arbitrary or difficult to detect barcodes!
def main():

    command_line_arguments = sys.argv[1:]

    SHOW_DEBUG_FIGURES = True

    # this is the default input image filename
    filename = "Barcode6"
    input_filename = "images/"+filename+".png"

    if command_line_arguments != []:
        input_filename = command_line_arguments[0]
        SHOW_DEBUG_FIGURES = False

    output_path = Path("output_images")
    if not output_path.exists():
        # create output directory
        output_path.mkdir(parents=True, exist_ok=True)

    output_filename = output_path / Path(filename+"_output.png")
    if len(command_line_arguments) == 2:
        output_filename = Path(command_line_arguments[1])

    # we read in the png file, and receive three pixel arrays for red, green and blue components, respectively
    # each pixel array contains 8 bit integer values between 0 and 255 encoding the color values
    (image_width, image_height, px_array_r, px_array_g, px_array_b) = readRGBImageToSeparatePixelArrays(input_filename)

    # setup the plots for intermediate results in a figure
    fig1, axs1 = pyplot.subplots(2, 2)
    axs1[0, 0].set_title('Input red channel of image')
    axs1[0, 0].imshow(px_array_r, cmap='gray')
    axs1[0, 1].set_title('Input green channel of image')
    axs1[0, 1].imshow(px_array_g, cmap='gray')
    axs1[1, 0].set_title('Input blue channel of image')
    axs1[1, 0].imshow(px_array_b, cmap='gray')


    # STUDENT IMPLEMENTATION here
    # step1. Convert to greyscale and Normalise
    px_array = computeRGBtoGreyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)
    # step2. Apply Standard Deviation Filter
    px_array = applyStdDevFilter(px_array, image_width, image_height)
    # step3. Apply Gaussian Filter
    px_array = applyGaussianFilter(px_array, image_width, image_height)
    px_array = applyGaussianFilter(px_array, image_width, image_height)
    # step4. Apply Thresholding
    px_array = computeThreshold(px_array, 20, image_width, image_height)
    # step5. Apply Erosion & Dilation
    px_array = applyErosion(px_array, image_width, image_height)
    px_array = applyErosion(px_array, image_width, image_height)
    px_array = applyErosion(px_array, image_width, image_height)
    px_array = applyDilation(px_array, image_width, image_height)
    px_array = applyDilation(px_array, image_width, image_height)
    # step6. Apply Connected Component
    px_array, box_dimensions = connectedComponent(px_array, image_width, image_height)
    
    barcode_region = box_dimensions[1]   #barcode_region is a list of first value of dictionary
    total_foreground_pixels = 0
    for key in box_dimensions.keys():
        total_foreground_pixels += box_dimensions[key][0]
    for key in box_dimensions.keys():
        if barcode_region[0] / total_foreground_pixels < box_dimensions[key][0] / total_foreground_pixels:
            barcode_region = box_dimensions[key]
    bar_width = barcode_region[1]
    bar_height = barcode_region[2]
    bar_min_x = barcode_region[3]
    bar_min_y = barcode_region[4]
    bar_max_x = barcode_region[5]
    bar_max_y = barcode_region[6]

    #px_array = px_array_r

    # Compute a dummy bounding box centered in the middle of the input image, and with as size of half of width and height
    # Change these values based on the detected barcode region from your algorithm
    

    # The following code is used to plot the bounding box and generate an output for marking
    # Draw a bounding box as a rectangle into the input image
    
    axs1[1, 1].set_title('Final image of detection')
    #axs1[1, 1].imshow(px_array, cmap='gray')
    axs1[1, 1].imshow(separateArraysToRGB(px_array_r, px_array_g, px_array_b, image_width, image_height))
    
    rect = Rectangle((bar_min_y, bar_min_x), bar_max_y - bar_min_y, bar_max_x - bar_min_x, linewidth=2,
                     edgecolor='g', facecolor='none')
    
    axs1[1, 1].add_patch(rect)

    # write the output image into output_filename, using the matplotlib savefig method
    extent = axs1[1, 1].get_window_extent().transformed(fig1.dpi_scale_trans.inverted())
    pyplot.savefig(output_filename, bbox_inches=extent, dpi=600)

    if SHOW_DEBUG_FIGURES:
        # plot the current figure
        pyplot.show()


if __name__ == "__main__":
    main()