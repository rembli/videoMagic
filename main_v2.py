'''
Simple cam program
'''

import cv2
import numpy as np

THRESHOLD = 25
BLUR_FACTOR = 40
SHARP_FACTOR = 0.8

SHOW_MIXED = 0
SHOW_CAM = 1
SHOW_BACKGROUND = 2
SHOW_MASK = 3
SHOW_MASK_NOISY = 4
SHOW_MASK_BLURRED = 5

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
FONT_COLOR = (255, 0, 0) 
FONT_THICKNESS = 2

def main(display_mode = SHOW_MIXED, treshold=THRESHOLD, blur_factor=BLUR_FACTOR, sharp_factor=SHARP_FACTOR):
    ''' main
    '''
    cap = cv2.VideoCapture(0)


    #####################################################################################
    # PREPARATION
    #####################################################################################

    # capture background from cam
    while True:
        # capture from cam 
        _, image = cap.read()
        background_image_cam = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # place text on image
        txt = "GET OUT OF THE SCREEN TO CAPTURE THE BACKGROUND THEN PRESS 'SPACE'"
        cv2.putText(image, txt, (5, 25), FONT, FONT_SCALE, FONT_COLOR)

        # display cam image
        cv2.imshow('video', image)

        # wait for user input
        if cv2.waitKey(1) == ord(' '):
            break

    height, width = background_image_cam.shape

    # load new background image and prepare it (esp. scale size)
    background_image_new = cv2.imread('VideoMagic/beach.jpg', cv2.IMREAD_GRAYSCALE)
    b_height, b_width = background_image_new.shape

    scale = width/b_width
    padding = int((height - (b_height*scale))/2)
    background_image_new = cv2.resize(background_image_new, (width, int(b_height*scale)))
    background_image_new = cv2.copyMakeBorder(background_image_new, padding+1, padding+1, 0, 0, borderType=cv2.BORDER_CONSTANT, value=0)

    # capture video and replace old background with new background

    while True:

        #####################################################################################
        # IMAGE MAGIC
        #####################################################################################
                
        _, image = cap.read()
        cam_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # calcuate the image_mask = difference between the current cam image and the captured background image of the cam
        image_mask_noisy = np.empty([height, width])
        for y in range(height): 
            for x in range(width):
                pix = abs((int)(background_image_cam[y, x])-(int)(cam_image[y, x]))
                if pix <= treshold:
                    image_mask_noisy[y,x] = True
                else:
                    image_mask_noisy[y,x] = False

        # blur the image mask to reduce noise
        if blur_factor > 0:
            image_mask_blurred = cv2.blur(image_mask_noisy, (blur_factor, blur_factor))
        else:
            image_mask_blurred = image_mask_noisy

        # generate sharper mask from blurred mask
        image_mask = np.empty([height, width])
        for y in range(height):
            for x in range(width):
                pix = image_mask_blurred[y,x]
                if pix > sharp_factor:
                    image_mask[y,x] = True
                else:
                    image_mask[y,x] = False

        # print cam image on top of background according mask
        image_calculated = np.array(background_image_new)

        for y in range(height):
            for x in range(width):
                pix = image_mask[y, x]
                if not pix:
                    image_calculated[y, x] = cam_image[y, x]

        #####################################################################################
        # DISPLAY MODE
        #####################################################################################

        if display_mode == SHOW_CAM:
            image_calculated = cam_image
        elif display_mode == SHOW_BACKGROUND:
            image_calculated = background_image_new
        elif display_mode == SHOW_MASK:
            image_calculated = image_mask
        elif display_mode == SHOW_MASK_NOISY:
            image_calculated = image_mask_noisy
        elif display_mode == SHOW_MASK_BLURRED:
            image_calculated = image_mask_blurred

        # convert binary masks to float values
        if display_mode == SHOW_MASK or display_mode == SHOW_MASK_BLURRED or display_mode == SHOW_MASK_NOISY:
            image_calculated = np.float32(image_calculated)
        # convert image to color
        vis = cv2.cvtColor(image_calculated, cv2.COLOR_GRAY2BGR)

        # place text on image
        txt = "THRESHOLD "+str(treshold)
        cv2.putText(vis, txt, (5, 25), FONT, FONT_SCALE, FONT_COLOR)

        txt = "BLUR FACTOR "+str(blur_factor)
        cv2.putText(vis, txt, (5, 45), FONT, FONT_SCALE, FONT_COLOR)

        txt = "SHARPNESS "+str(sharp_factor)
        cv2.putText(vis, txt, (5, 65), FONT, FONT_SCALE, FONT_COLOR)

        # display modified image
        cv2.imshow('video', vis)

        #####################################################################################
        # COMMANDS
        #####################################################################################

        k = cv2.waitKey(1)
        if k == -1:
            continue
        elif k == 27: # ESC
            break
        
        elif k == ord('+'):
            treshold = treshold + 5
        elif k == ord('-') and treshold >= 5:
            treshold = treshold - 5

        elif k == ord('b'):
            blur_factor = blur_factor + 5
        elif k == ord('n') and blur_factor >= 5:
            blur_factor = blur_factor - 5

        elif k == ord('s') and sharp_factor <= 0.9:
            sharp_factor = sharp_factor + 0.1
        elif k == ord('d') and sharp_factor >= 0.1:
            sharp_factor = sharp_factor - 0.1

        elif k == ord(" "):
            display_mode = SHOW_MIXED
        elif k == ord("0"):
            display_mode = SHOW_CAM
        elif k == ord("1"):
            display_mode = SHOW_MASK_NOISY
        elif k == ord("2"):
            display_mode = SHOW_MASK_BLURRED
        elif k == ord("3"):
            display_mode = SHOW_MASK

        else:
            print ("Pressed:", k) # else print its value

    cap.release()
    cv2.destroyAllWindows()


###############################################################

print ('''
    HOW-TO
    ==========================================================
    Change display mode:
    SPACE:  mixed mode
    1:      noisy image
    2:      blurred image
    3:      sharp image mask
    0:      original cam 
    ----------------------------------------------------------
    +/-:    threshold
    b/n:    blur factor
    s/d:    sharpness
    ==========================================================
    ESC:    Quit Video Magic
''')

main()
