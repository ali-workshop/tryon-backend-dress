import io
from PIL import Image
from google.genai import types
from app.gemini_client import get_gemini_client

PROMPT = """
# **Full-Body Dress Replacement Prompt (Strict Clothing Removal + Dress-Only Output)**

**TASK:**
Replace **ALL existing clothing** on the model in Image 1 with the **full-body dress shown in Image 2**.
Absolutely **no original clothing may remain visible**, including pants, shorts, sleeves, or waistband outlines.

---

## **HARD REQUIREMENTS (STRICT RULES)**

### **1. Full Clothing Removal — ABSOLUTE (NO PANTS ALLOWED)**
- Remove ALL original clothing on the model from **neck to ankles**, without exception.
- **Pants, shorts, leggings, jeans, or ANY lower-body garment must be completely removed.**
- Do NOT leave:
  - pants waistband
  - pants color bleed-through
  - pants outlines or folds
  - pants shadows under the dress
  - double-layer clothing
- The model must appear to be wearing **only the dress**, with no clothing underneath.

---

## **2. Dress Integrity — DO NOT ALTER THE GARMENT**
The dress from Image 2 must be transferred **exactly as it is**, including:
- true colors
- original patterns
- original textures
- material shine and shadows
- stitching, graphics, logos
- wrinkles, folds, creases
- fabric imperfections
- watermarks or brand marks
- any tags or print details

**NO:**
- redesign
- cleanup
- smoothing
- recoloring
- repairing
- pattern alteration

The dress must remain **100% identical** to the original garment image.

---

## **3. Realistic Application of the Dress**
- Fit the dress naturally to the model’s torso, waist, hips, and full legs.
- Ensure continuous, uninterrupted full-body coverage as a proper dress.
- Maintain natural fabric tension, flow, draping, and body contours.
- No clipping, no overlap, no double layers.

---

## **4. Identity & Scene Preservation — ABSOLUTE**
Do NOT change:
- the model’s face or expression
- hair or hairstyle
- body shape or proportions
- pose
- arms/hands
- background
- lighting

Only the clothing may be changed.

---

## **NEGATIVE INSTRUCTIONS — AVOID AT ALL COSTS**
- ANY visibility of pants, shorts, leggings, jeans, or lower-body clothing
- waistband lines, pant leg outlines, shadows from pants
- multi-layer clothing (dress over pants)
- blur, artifacts, distortions
- incorrect pose or warped limbs
- wrong face, skin, or lighting changes
- unfinished dress or cut-off hem
- improper blending or CGI appearance
- pattern distortion or recoloring

---

## **IMAGES**
- **Image 1:** Model
- **Image 2:** Dress (must be applied without any modification)

---

## **FINAL DOUBLE-CHECK (MANDATORY)**
Before producing the final output, verify ALL of the following:

1. **NO pants are visible anywhere — not above, beneath, or through the dress.**
2. **The dress fully replaces ALL clothing from neck to ankles with zero traces of the original outfit.**
3. **The dress matches Image 2 EXACTLY: colors, patterns, textures, and all micro-details preserved.**
4. **The model’s face, body, pose, hair, background, and lighting remain unchanged.**
5. **The dress fits naturally without artifacts, clipping, or dual-layer clothing.**
"""

def run_tryon(model_file_path: str, garment_file_path: str):
    client = get_gemini_client()

    # Upload both files to Gemini
    model_file = client.files.upload(file=model_file_path)
    garment_file = client.files.upload(file=garment_file_path)

    # Request to Gemini
    response = client.models.generate_content(
        model="models/gemini-2.5-flash-image",
        contents=[
            
            model_file,
            garment_file,
            types.Part(text=PROMPT),
        ]
    )

    # Extract image bytes
    image_bytes = None
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data and "image" in part.inline_data.mime_type:
                image_bytes = part.inline_data.data  # already raw bytes
                break
    
    if not image_bytes:
        raise Exception("❌ Gemini returned no image. Full response:\n" + str(response))
    
    return image_bytes
