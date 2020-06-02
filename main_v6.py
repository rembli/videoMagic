'''
VIDEO MAGIC V6

This version is using a dynamic background from another video stream.
Spacy!

'''

import cv2
import numpy as np
import colour

BACKGROUND_VIDEO = "VideoMagic/space.mp4"

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
FONT_COLOR = (256, 0, 0)
FONT_COLOR_BW = (0, 0, 0)
FONT_THICKNESS = 2

def main(display_mode = SHOW_MIXED, treshold=THRESHOLD, blur_factor=BLUR_FACTOR, sharp_factor=SHARP_FACTOR):

    cap = cv2.VideoCapture(0)
    cap_background = cv2.VideoCapture(BACKGROUND_VIDEO)

    #####################################################################################
    # PREPARATION
    #####################################################################################

    # function to load next background image from video stream and prepare it (esp. scale size)
    def get_next_background_image(cap_background, width, height):
        _, background_image_new = cap_background.read()
        b_height, b_width, _ = background_image_new.shape

        scale_width = width/b_width
        padding = int((height - (b_height*scale_width))/2)
        background_image_new = cv2.resize(background_image_new, (width, int(b_height*scale_width)))
        background_image_new = cv2.copyMakeBorder(background_image_new, padding, padding, 0, 0, borderType=cv2.BORDER_CONSTANT, value=0)
        return background_image_new

    # capture background from cam
    while True:
        # capture from cam 
        _, background_image_cam = cap.read()
        
        # place text on image
        txt = "GET OUT OF THE SCREEN TO CAPTURE THE BACKGROUND THEN PRESS 'SPACE'"
        background_image_cam_display = np.array (background_image_cam)
        background_image_cam_display = cv2.putText(background_image_cam_display, txt, (5, 25), FONT, FONT_SCALE, FONT_COLOR)

        # display cam image
        cv2.imshow('video', background_image_cam_display)

        # wait for user input
        if cv2.waitKey(1) == ord(' '):
            break

    height, width, _ = background_image_cam.shape

    #####################################################################################
    # IMAGE MAGIC
    #####################################################################################

    while True:
        _, cam_image = cap.read()

        # calcuate the image_mask = difference between the current cam image and the captured background image of the cam
        # Delta-E Color Difference delivers the best quality
        # BUT this is the MOST EXPENSIVE OPERATION
        image_diff = abs(colour.delta_E(background_image_cam, cam_image))

        # thresholding the difference between the two images
        f = lambda pix: 1.0 if pix <= treshold else 0.0
        vectorized_f = np.vectorize(f)
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

        #####################################################################################
        # DISPLAY MODE
        #####################################################################################

        if display_mode == SHOW_CAM:
            vis = cam_image
        elif display_mode == SHOW_MASK:
            vis = image_mask
        elif display_mode == SHOW_MASK_NOISY:
            vis = image_mask_noisy
        elif display_mode == SHOW_MASK_BLURRED:
            vis = image_mask_blurred
        else:
            background_image_new = get_next_background_image(cap_background, width, height)
            vis = cv2.copyTo(background_image_new, image_mask.astype(cam_image.dtype), cam_image)

        # place text on image
        font_color = FONT_COLOR
        if display_mode == SHOW_MASK or display_mode == SHOW_MASK_BLURRED or display_mode == SHOW_MASK_NOISY:
            font_color = FONT_COLOR_BW

        txt = "THRESHOLD "+str(treshold)
        cv2.putText(vis, txt, (5, 25), FONT, FONT_SCALE, font_color)

        txt = "BLUR FACTOR "+str(blur_factor)
        cv2.putText(vis, txt, (5, 45), FONT, FONT_SCALE, font_color)

        txt = "SHARPNESS "+str(sharp_factor)
        cv2.putText(vis, txt, (5, 65), FONT, FONT_SCALE, font_color)

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

        elif k == ord('d') and sharp_factor <= 0.9:
            sharp_factor = sharp_factor + 0.1
        elif k == ord('s') and sharp_factor >= 0.1:
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
