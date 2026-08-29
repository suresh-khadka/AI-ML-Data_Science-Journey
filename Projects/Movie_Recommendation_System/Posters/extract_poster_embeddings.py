import os
import pickle
import torch
from torchvision import models, transforms
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTER_DIR = os.path.join(BASE_DIR, 'posters')

resnet = models.resnet50(pretrained=True)
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])
resnet.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

downloaded = pickle.load(open(os.path.join(BASE_DIR, 'movies_with_posters.pkl'), 'rb'))
embeddings = {}

for movie_id in downloaded:
    path = os.path.join(POSTER_DIR, f"{movie_id}.jpg")
    try:
        img = Image.open(path).convert('RGB')
        tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            emb = resnet(tensor).squeeze().numpy()
        embeddings[movie_id] = emb
    except Exception as e:
        print(f"Skipping {movie_id}: {e}")

pickle.dump(embeddings, open(os.path.join(BASE_DIR, 'poster_embeddings.pkl'), 'wb'))
print(f"Extracted embeddings for {len(embeddings)} posters.")