import numpy as np
import cv2
import imutils
from imutils.object_detection import non_max_suppression
from object_tracker import ImageObject
from scene import Scene

# https://www.pyimagesearch.com/2015/11/09/pedestrian-detection-opencv/
# https://www.theimpossiblecode.com/blog/backgroundsubtractorcnt-opencv-3-3-0/
# https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=12&cad=rja&uact=8&ved=2ahUKEwjErd_QsbTeAhWDiiwKHQWmAXcQFjALegQICBAC&url=http%3A%2F%2Fwww.mdpi.com%2F1424-8220%2F17%2F12%2F2864%2Fpdf&usg=AOvVaw0Z--0buthONx7l6UuDC15-
# Dataset - http://www.iro.umontreal.ca/~labimage/Dataset/

CAMERA_MATRIX_8 = np.matrix('470.561316433381705 0 355.172484892247837; 0 425.594571513702249 231.057027802762576; 0 0 1')
DIST_8 = np.matrix('-0.412750560124808 0.148158881927254 -0.002749158333180 -0.000425978486412 0.000000000000000')

class BS:
    def __init__(self, bs, learnrate=[-1, -1]):
        self.bs = bs
        self.fgmask = None
        self.learnrate = learnrate

    def get_mask(self, frame):
        if self.fgmask is None:
            self.fgmask = self.bs.apply(frame, self.fgmask, self.learnrate[0])
        else:
            self.fgmask = self.bs.apply(frame, self.fgmask, self.learnrate[1])
        return self.fgmask

class GSOC(BS):
    def __init__(self):
        fgbg = cv2.bgsegm.createBackgroundSubtractorGSOC()
        super().__init__(fgbg, [0, 0.001])

class MOG2(BS):
    def __init__(self):
        fgbg = cv2.createBackgroundSubtractorMOG2(500, 16, 0)
        super().__init__(fgbg, [0, 0.001])

class CNT(BS):
    def __init__(self):
        fgbg = cv2.bgsegm.createBackgroundSubtractorCNT()#15, True, 15*60, False)
        super().__init__(fgbg)

def undistort_frame(frame):
    fh, fw = frame.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(CAMERA_MATRIX_8,DIST_8,(fw,fh),1,(fw,fh))
    frame_undist = cv2.undistort(frame, CAMERA_MATRIX_8, DIST_8, None, newcameramtx)
    x,y,w,h = roi
    return frame_undist[y:y+h, x:x+w]

def denoise_mask(fgmask):

    thresh = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    thresh = cv2.dilate(thresh, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)), iterations=1)
    thresh = cv2.erode(thresh, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)), iterations=2)
    return thresh

cap = cv2.VideoCapture('/home/nagybalint/code/iot-home-security/src/raspberry_sec/module/falldetector/chute02/cam8.avi')
#cap = cv2.VideoCapture(0)

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

bs = CNT()

i = 0

scene = Scene()

while(1):
    ret, frame_orig = cap.read()
    if not ret:
        break
    roi = None
    #frame = undistort_frame(frame_orig)
    frame = frame_orig.copy()
    #frame = cv2.GaussianBlur(frame,(5,5),1)
    #noise_free = cv2.medianBlur(frame, 3)

    #frame = imutils.resize(frame, width=min(500, frame.shape[1]))

    fgmask = bs.get_mask(frame)

    if True:    
        mask = denoise_mask(fgmask)
    else:
        mask = fgmask.copy()

    _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rects = []
    #rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    #rects = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    objects = []

    for contour in contours:
        obj = ImageObject(0, contour, frame)
        if obj.get_area() < 1000:
            continue
        if obj.get_area() > 30000:
            continue
        if obj.detect_human():
            #print(f"HUMAN {i}")
            i += 1
        objects.append(obj)

    for o in objects:
        scene.add_object(o)

    for i, o in scene.objects.items():
        o.draw(frame)


    cv2.imshow('f',mask)
    cv2.imshow('fr', frame)
    k = cv2.waitKey(1) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()