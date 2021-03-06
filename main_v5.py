'''
VIDEO MAGIC V5

This version is using Delta E to calculate the difference between the background and the background with actor.
Quality improved a lot! Now it is getting awesaome .. I already feel the beach

'''

import cv2
import numpy as np
import colour

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
FONT_COLOR = (256, 0, 0)
FONT_COLOR_BW = (0, 0, 0)
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
        background_image_cam_display = np.array (background_image_cam)
        background_image_cam_display = cv2.putText(background_image_cam_display, txt, (5, 25), FONT, FONT_SCALE, FONT_COLOR)

        # display cam image
        cv2.imshow('video', background_image_cam_display)

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

        # calcuate the image_mask = difference between the current cam image and the captured background image of the cam based on Delta-E Color Difference
        # https://www.colour-science.org/
        f = lambda pix: 1.0 if pix <= treshold else 0.0
        vectorized_f = np.vectorize(f)
        image_diff = abs(colour.delta_E(background_image_cam, cam_image))
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
            vis = np.array(cam_image)
        elif display_mode == SHOW_BACKGROUND:
            vis = np.array(background_image_new)
        elif display_mode == SHOW_MASK:
            vis = np.array(image_mask)
        elif display_mode == SHOW_MASK_NOISY:
            vis = np.array(image_mask_noisy)
        elif display_mode == SHOW_MASK_BLURRED:
            vis = np.array(image_mask_blurred)
        else:
            vis = cv2.copyTo(background_image_new, image_mask.astype(cam_image.dtype), np.array(cam_image))

        # a little bluring magic dust ;-)
        vis = cv2.blur(vis, (2, 2))

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
