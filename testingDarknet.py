from darknet import darknetFunc

dsDataFilePath = b'/usr/share/qgis/python/plugins/object_detection/workspace/data/car_dataset/car_dataset.data'
newModelConfigPath = b'/usr/share/qgis/python/plugins/object_detection/workspace/detectors/car/car.cfg'
baseWeights = b'/media/sf_Shared_Folder/default.weights'

darknetFunc.train_detector(dsDataFilePath, newModelConfigPath, baseWeights)
