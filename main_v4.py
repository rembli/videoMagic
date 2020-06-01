'''
VIDEO MAGIC V4

This version changed from black and white to color.
The change is relativelly simple as we were using vectorized operations.
There are some strange color effects that I cannot explain right now.

'''

import cv2
import numpy as np

BACKGROUND_IMAGE = "VideoMagic/beach.jpg"
#BACKGROUND_IMAGE = "VideoMagic/space.jpg"

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
        _, background_image_cam = cap.read()
        
        # place text on image
        txt = "GET OUT OF THE SCREEN TO CAPTURE THE BACKGROUND THEN PRESS 'SPACE'"
        cv2.putText(background_image_cam, txt, (5, 25), FONT, FONT_SCALE, FONT_COLOR)

        # display cam image
        cv2.imshow('video', background_image_cam)

        # wait for user input
        if cv2.waitKey(1) == ord(' '):
            break

    height, width, _ = background_image_cam.shape

    # load new background image and prepare it (esp. scale size)
    background_image_new = cv2.imread(BACKGROUND_IMAGE)
    b_height, b_width, _ = background_image_new.shape

    scale = width/b_width
    padding = int((height - (b_height*scale))/2)
    background_image_new = cv2.resize(background_image_new, (width, int(b_height*scale)))
    background_image_new = cv2.copyMakeBorder(background_image_new, padding+1, padding+1, 0, 0, borderType=cv2.BORDER_CONSTANT, value=0)

    # capture video and replace old background with new background

    while True:

        #####################################################################################
        # IMAGE MAGIC
        #####################################################################################
                
        _, cam_image = cap.read()

        # calcuate the image_mask = difference between the current cam image and the captured background image of the cam
        f = lambda pix: 1.0 if pix <= treshold else 0.0
        vectorized_f = np.vectorize(f)
        image_diff = abs(cv2.subtract(background_image_cam, cam_image))
        image_mask_noisy = vectorized_f(image_diff)

        # blur the image mask to reduce noise
        if blur_factor > 0:
            image_mask_blurred = cv2.blur(image_mask_noisy, (blur_factor, blur_factor))
        else:
            image_mask_blurred = image_mask_noisy

        # generate sharper mask from blurred mask
        f = lambda pix: 1.0 if pix > sharp_factor else 0.0
        vectorized_f = np.vectorize(f)
        image_mask = vectorized_f(image_mask_blurred)

        # print cam image on top of background according mask       
        image_calculated = cv2.copyTo(background_image_new, image_mask.astype(cam_image.dtype), np.array(cam_image))

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
            image_mask_canvas = np.ones([height, width, 3])*255
            cv2.copyTo(image_mask_canvas, image_mask.astype(cam_image.dtype), image_calculated)

        # place text on image
        txt = "THRESHOLD "+str(treshold)
        cv2.putText(image_calculated, txt, (5, 25), FONT, FONT_SCALE, FONT_COLOR)

        txt = "BLUR FACTOR "+str(blur_factor)
        cv2.putText(image_calculated, txt, (5, 45), FONT, FONT_SCALE, FONT_COLOR)

        txt = "SHARPNESS "+str(sharp_factor)
        cv2.putText(image_calculated, txt, (5, 65), FONT, FONT_SCALE, FONT_COLOR)

        # display modified image
        cv2.imshow('video', image_calculated)

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
