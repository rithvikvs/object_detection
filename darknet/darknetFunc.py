from ctypes import *
import os
import glob

lib = CDLL(os.path.join(os.path.dirname(__file__),"libdarknet.so"), RTLD_GLOBAL)

train_detector = lib.train_detector
train_detector.argtypes = [c_char_p, c_char_p, c_char_p]

test_detector = lib.test_detector
test_detector.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]

#train_detector(b'/usr/share/qgis/python/plugins/object_detection/darknetTesting/obj.data', b'/usr/share/qgis/python/plugins/object_detection/darknetTesting/yolov3_training.cfg', b'/usr/share/qgis/python/plugins/object_detection/darknetTesting/obj.data/darknet53.conv.74')

#make_image = lib.make_image
#make_image.argtypes = [c_int, c_int, c_int]
#make_image.restype = IMAGE
