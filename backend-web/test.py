import io
import httpx
import time
from PIL import Image
from ultralytics import YOLO

model = YOLO("models/weights.pt")
url = "https://webcams.nyctmc.org/api/cameras/a3058350-1552-459f-8379-2fd06895e70a/image"
raw = httpx.get(url, params={"t": int(time.time() * 1000)}).content
image = Image.open(io.BytesIO(raw)).convert("RGB")

for r in model.predict(source=image, conf=0.25, verbose=False):
    if r.boxes is None or len(r.boxes) == 0:
        print("NO BOXES")
    else:
        for cls, conf in zip(r.boxes.cls.tolist(), r.boxes.conf.tolist()):
            print(model.names[int(cls)], round(conf, 3))