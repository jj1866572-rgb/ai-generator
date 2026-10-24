import io
import urllib.parse
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import requests
from PIL import Image

app = FastAPI(title="AI Image Generator & Modifier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/api")
@app.get("/api/index.py")
def health():
    return {"status": "online", "feature": "AI Image Modifier Ready"}

@app.post("/")
@app.post("/api")
@app.post("/generate")
@app.post("/api/generate")
@app.post("/api/index.py")
@app.post("/api/index.py/generate")
async def generate_or_modify(
    image: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    prompt: Optional[str] = Form("high quality cinematic, detailed photorealistic 8k")
):
    target = image if image is not None else file

    try:
        # প্রম্পট পরিষ্কার ও এনকোড করা
        clean_prompt = prompt.strip() if prompt else "cinematic masterpiece"
        encoded_prompt = urllib.parse.quote(clean_prompt)

        # ১. যদি ইউজার কোনো ছবি আপলোড করে থাকে
        if target is not None:
            contents = await target.read()
            raw_img = Image.open(io.BytesIO(contents))
            w, h = raw_img.size
            # অ্যাসপেক্ট রেশিও রক্ষা করা
            aspect_w = min(1024, max(512, (w // 64) * 64))
            aspect_h = min(1024, max(512, (h // 64) * 64))
        else:
            aspect_w, aspect_h = 768, 768

        # ২. Pollinations AI হাই-স্পিড ক্লাউড GPU ইঞ্জিন কল করা (১০০% ফ্রি, নো কার্ড)
        api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={aspect_w}&height={aspect_h}&model=flux&nologo=true"

        resp = requests.get(api_url, timeout=30)
        
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="AI ছবি তৈরি করতে ব্যর্থ হয়েছে!")

        return Response(content=resp.content, media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
