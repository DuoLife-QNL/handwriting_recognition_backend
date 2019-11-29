import numpy as np
import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision import transforms
from PIL import Image
import cv2

class Letter:
    
    def __init__(self, boxesn, classn, scoren):
        self.boxesn = boxesn
        self.classn = classn
        self.scoren = scoren


class Model:
    CLASS_NAMES = ['__background__', 'A', 'B', 'C', 'D', 'X']
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn()
    num_classes = 6
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model.to(device)
    model.load_state_dict(torch.load('model.pth'))
    model.eval()

    def prediction(self, img, threshold):
        # img = Image.open(img)
        img = cv2.imread(img)
        img[img > 100] = 255
        img = 255 - img
        img = Image.fromarray(img.astype('uint8')).convert('RGB')
        transform = transforms.Compose([transforms.ToTensor()])
        img = transform(img)
        img = img.to(self.device)
        pred = self.model([img]) # Pass the image to the model
        pred_class = [self.CLASS_NAMES[i] for i in list(pred[0]['labels'].to("cpu").numpy())]
        pred_boxes = [[int(i[0]), int(i[1]), int(i[2]), int(i[3])] for i in list(pred[0]['boxes'].to("cpu").detach().numpy())]
        pred_score = list(pred[0]['scores'].to("cpu").detach().numpy())
        pred_t = [pred_score.index(x) for x in pred_score if x >= threshold][-1]
        pred_boxes = pred_boxes[:pred_t+1]
        pred_class = pred_class[:pred_t+1]
        pred_score = pred_score[:pred_t+1]
        for i in range(len(pred_score)):
            pred_score[i] = int(pred_score[i] * 100)
        return pred_boxes, pred_class, pred_score

    def getAns(self, img, threshold):

        pred_boxes, pred_class, pred_score =  self.prediction(img, threshold)
        letters = []
        for i in range(len(pred_boxes)):
            if pred_class[i] != 'X':
                letter = Letter(pred_boxes[i], pred_class[i], pred_score[i])
                letters.append(letter)
                
        letters.sort(key=lambda x: x.boxesn[0] + 2000 * x.boxesn[1])
        new_letters = []
        for i in range(0, len(letters), 5):
            items = letters[i:i+5]
            items.sort(key=lambda x: x.boxesn[0])
            for j in range(len(items)):
                new_letters.append(items[j])
        return new_letters
        

        