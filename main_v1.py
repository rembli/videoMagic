'''
VIDEO MAGIC V1

This version is a first working version.
But it looks that I am not really on the beach but somehow caucht in twilight zone.

'''

import cv2

def main():
    ''' main
    '''
    cap = cv2.VideoCapture(0)

    # capture background from cam
    while True:
        _, image = cap.read()
        background_image_cam = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imshow('video', background_image_cam)

        if cv2.waitKey(1) == ord (' '): # SPACE
            break

    height, width = background_image_cam.shape

    # load new background image and prepare it
    background_image_new = cv2.imread('VideoMagic/beach.jpg', cv2.IMREAD_GRAYSCALE)
    b_height, b_width = background_image_new.shape

    scale = width/b_width
    padding = int((height - (b_height*scale))/2)
    background_image_new = cv2.resize(background_image_new, (width, int(b_height*scale)))
    background_image_new = cv2.copyMakeBorder(background_image_new, padding+1, padding+1, 0, 0, borderType=cv2.BORDER_CONSTANT, value=0)
    background_image_new_inverted = cv2.bitwise_not(background_image_new)

    # capture video and replace old background with new background
    while True:
        _, image = cap.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        image_diff = cv2.subtract (background_image_cam, image)
        image_add = cv2.addWeighted(background_image_new_inverted, 0.8, image_diff, 1.0, 0)
        image_add_inverted = cv2.bitwise_not(image_add)

        cv2.imshow('video',image_add_inverted)

        if cv2.waitKey(1) == 27: # ESC:
            break

    cap.release()
    cv2.destroyAllWindows()

main()
