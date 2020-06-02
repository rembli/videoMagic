# https://answers.opencv.org/question/202017/how-to-use-gstreamer-pipeline-in-opencv/
# https://stackoverflow.com/questions/45544877/write-in-gstreamer-pipeline-from-opencv-in-python
# https://www.pyimagesearch.com/2016/02/22/writing-to-video-with-opencv/

import cv2

def main():

    cap = cv2.VideoCapture(0)

    # fourcc = four character codec; fow Windows only the combination MJPG and .avi-file worked
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    
    # Write to file - Important:
    # 1. specify output shape EXACTLY like the input shape
    # 2. for Windows only the combination MJPG and .avi-file worked
    out = cv2.VideoWriter ("VideoMagic/video_writer_example.avi", fourcc, 20, (640, 480), True)

    if not cap.isOpened():
        print('VideoCapture not opened')
        exit(0)

    if not out.isOpened():
        print('VideoWriter not opened')
        exit(0)

    while True: 
        _, frame = cap.read ()
        
        # print (frame.shape)
        # --> (480, 640, 3)

        cv2.imshow('myVideo', frame)
        out.write(frame)

        if cv2.waitKey(1) == 27: # ESC:
            break

    cv2.destroyAllWindows() 
    out.release()

main()
