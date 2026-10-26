"""Find where the speaker sits in a landscape frame so the 9:16 crop keeps their face in shot.

  python face.py <master.mp4> [start end]   -> prints JSON {crop_x, crop_w, face_cx, found, frames}

Samples frames across the clip (or a time range), finds the largest face in each, and uses the
median centre. If no face is found it falls back to the centre and says so.
"""
import json, os, sys, subprocess
import numpy as np
import cv2
import ce_util as U

CASCADE = os.path.join(U.ASSETS, "haarcascade_frontalface_default.xml")
YUNET = os.path.join(U.ASSETS, "face_detection_yunet_2023mar.onnx")


def detector(w, h):
    """YuNet (OpenCV 4.8+ and 5) is the better finder; the older Haar cascade is the fallback."""
    if hasattr(cv2, "FaceDetectorYN") and os.path.exists(YUNET):
        d = cv2.FaceDetectorYN.create(YUNET, "", (w, h), 0.7, 0.3, 50)
        def find(gray):
            _, f = d.detect(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))
            return [] if f is None else [tuple(int(v) for v in r[:4]) for r in f]
        return find
    if hasattr(cv2, "CascadeClassifier"):
        c = cv2.CascadeClassifier(CASCADE)
        return lambda g: list(c.detectMultiScale(g, scaleFactor=1.1, minNeighbors=6, minSize=(w // 16, w // 16)))
    raise RuntimeError("No face finder available in this OpenCV build.")


def grab(path, t, w, h):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1",
                        "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    if len(p.stdout) != w * h:
        return None
    return np.frombuffer(p.stdout, np.uint8).reshape(h, w)


def locate(path, start=None, end=None, samples=14):
    info = U.video_info(path)
    W, H = info["width"], info["height"]
    crop_w = int(round(H * 9 / 16 / 2) * 2)
    if info["portrait"] or crop_w >= W:
        return {"crop_x": 0, "crop_w": W, "face_cx": W // 2, "found": True, "portrait": True, "frames": 0}
    s = start if start is not None else 0.5
    e = end if end is not None else max(s + 1, info["duration"] - 0.5)
    sw = 640; sh = int(round(H * sw / W))
    find = detector(sw, sh)
    cxs, sizes = [], []
    for t in np.linspace(s, e, samples):
        g = grab(path, t, sw, sh)
        if g is None:
            continue
        faces = find(g)
        if len(faces):
            x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            cxs.append((x + fw / 2) * W / sw); sizes.append(fh * H / sh)
    if not cxs:
        cx = W / 2; found = False
    else:
        cx = float(np.median(cxs)); found = True
    crop_x = int(min(max(cx - crop_w / 2, 0), W - crop_w))
    crop_x -= crop_x % 2
    return {"crop_x": crop_x, "crop_w": crop_w, "face_cx": round(cx), "found": found, "portrait": False,
            "frames": len(cxs), "spread_px": round(float(np.std(cxs)), 1) if cxs else None}


if __name__ == "__main__":
    a = sys.argv
    r = locate(a[1], float(a[2]) if len(a) > 3 else None, float(a[3]) if len(a) > 3 else None)
    print(json.dumps(r))
