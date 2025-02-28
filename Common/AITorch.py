import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
import cv2


class SiameseNetwork(nn.Module):
    def __init__(self):
        super(SiameseNetwork, self).__init__()
        self.cnn = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        self.fc = nn.Linear(1000, 128)

    def forward_once(self, x):
        output = self.cnn(x)
        output = self.fc(output)
        return output

    def forward(self, input1, input2):
        output1 = self.forward_once(input1)
        output2 = self.forward_once(input2)
        return output1, output2


class SiameseNetworkAnalysis:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SiameseNetwork().to(self.device)
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def imageEncoder(self, img):
        img = Image.fromarray(img).convert('RGB')
        img = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.model.forward_once(img)
        return output

    def generateScore(self, image1, image2):
        img1 = cv2.imread(image1, cv2.IMREAD_UNCHANGED)
        img2 = cv2.imread(image2, cv2.IMREAD_UNCHANGED)
        img1 = self.imageEncoder(img1)
        img2 = self.imageEncoder(img2)
        cos = nn.CosineSimilarity(dim=1, eps=1e-6)
        cos_scores = cos(img1, img2)
        score = round(float(cos_scores[0]) * 100, 2)
        return score


if __name__ == '__main__':
    snn = SiameseNetworkAnalysis()
    print(snn.generateScore("origin.png", "Key.png"))
