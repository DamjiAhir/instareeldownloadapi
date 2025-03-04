from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import instaloader
import re

app = FastAPI(
   
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://instareeldownload.online"],  # <-- Change "*" to your frontend domain for security
    allow_credentials=True,
    allow_methods=["*"],   # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], 
)

L = instaloader.Instaloader()

INSTAGRAM_URL_PATTERN = r"(?:https?:\/\/)?(?:www\.)?instagram\.com\/(?:reel|p)\/([a-zA-Z0-9_-]+)"

@app.get('/')
def home():
    return {"message":"instagram api is running"}

@app.get('/profile/{username}')
def get_profile(username:str):
    try:
        profile= instaloader.Profile.from_username(L.context,username)
        return {
            "posts":profile.mediacount,
            "username": profile.username,
            "fullname":profile.full_name,
            "followers": profile.followers,
            "following": profile.followees,
            "bio": profile.biography,
            "profile_pic_url": profile.profile_pic_url
        }
    except Exception as e:
        return {"error":str(e)}
    
@app.get("/get-reel")
def get_instagram_reel(url: str):
    try:
        # Extract shortcode from URL
        match = re.search(INSTAGRAM_URL_PATTERN, url)
        if not match:
            return {"error": "Invalid Instagram URL"}

        shortcode = match.group(1)

        # Get post data
        reel = instaloader.Post.from_shortcode(L.context, shortcode)

        # Extract media URLs
        caption = ''
        media_links = ''
        if reel.is_video:
            media_links = reel.video_url
            caption = reel.caption
        else:
            for resource in reel.get_sidecar_nodes():
                media_links.append(resource.video_url if resource.is_video else resource.display_url)

        return {"media_links": media_links,"caption":caption}

    except Exception as e:
        return {"error": str(e)}


@app.get("/get-posts")
def get_instagram_reel(url: str):
    try:
        # Extract shortcode from URL
        match = re.search(INSTAGRAM_URL_PATTERN, url)
        if not match:
            return {"error": "Invalid Instagram URL"}

        shortcode = match.group(1)

        # Get post data
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Extract media URLs
        media_links = []
        if post.is_video:
            media_links.append(post.video_url)
            
        else:
            for resource in post.get_sidecar_nodes():
                media_links.append(resource.video_url if resource.is_video else resource.display_url)

        return {"media_links": media_links}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)