# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

import math
from enum import Enum
from io import BytesIO

import aiohttp
from PIL import Image, ImageOps, ImageEnhance


class DeepfryTypes(Enum):
    """
    Enum for the various possible effects added to the image.
    """
    RED = 1
    BLUE = 2


class Colours:
    RED = (254, 0, 2)
    YELLOW = (255, 255, 15)
    BLUE = (36, 113, 229)
    WHITE = (255,) * 3


# TODO: Replace face recognition API with something like OpenCV.
async def deepfry(img: Image, *, token: str = None, api_url: str = None, session: aiohttp.ClientSession = None,
                  kind=DeepfryTypes.RED) -> Image:
    """
    Deepfry an image.
    img: PIL.Image - Image to deepfry.
    [token]: str - Token to use for Microsoft facial recognition API. If this is not supplied, lens flares will not be added.
    [url_base]: str = 'westcentralus' - API base to use. Only needed if your key's region is not `westcentralus`.
    [session]: aiohttp.ClientSession - Optional session to use with API requests. If provided, may provide a bit more speed.
    Returns: PIL.Image - Deepfried image.
    """
    img = img.copy().convert('RGB')

    if kind not in DeepfryTypes:
        raise ValueError(f'Unknown deepfry type "{kind}", expected a value from deeppyer.DeepfryTypes')

    if token and api_url:
        req_url = f'{api_url}/detect?returnFaceId=false&returnFaceLandmarks=true'  # WHY THE FUCK IS THIS SO LONG
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': token,
            'User-Agent': 'DeepPyer/1.0',
            'Content-Length': str(len(img.tobytes()))
        }

        b = BytesIO()
        img.save('flare.png')
        b.seek(0)

        if session:
            async with session.post(req_url, headers=headers, data=b.read()) as r:
                face_data = await r.json()
        else:
            async with aiohttp.ClientSession() as s, s.post(req_url, headers=headers, data=b.read()) as r:
                face_data = await r.json()

        if 'error' in face_data:
            err = face_data['error']
            code = err.get('code', err.get('statusCode'))
            msg = err['message']

            raise Exception(f'Error with Microsoft Face Recognition API\n{code}: {msg}')

    # Crush image to hell and back
    img = img.convert('RGB')
    width, height = img.width, img.height
    img = img.resize((int(width ** .75), int(height ** .75)), resample=Image.LANCZOS)
    img = img.resize((int(width ** .88), int(height ** .88)), resample=Image.BILINEAR)
    img = img.resize((int(width ** .9), int(height ** .9)), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, 4)

    # Generate red and yellow overlay for classic deepfry effect
    r = img.split()[0]
    r = ImageEnhance.Contrast(r).enhance(2.0)
    r = ImageEnhance.Brightness(r).enhance(1.5)

    if kind == DeepfryTypes.RED:
        r = ImageOps.colorize(r, Colours.RED, Colours.YELLOW)
    elif kind == DeepfryTypes.BLUE:
        r = ImageOps.colorize(r, Colours.BLUE, Colours.WHITE)

    # Overlay red and yellow onto main image and sharpen the hell out of it
    img = Image.blend(img, r, 0.75)
    img = ImageEnhance.Sharpness(img).enhance(100.0)

    if token and face_data:
        landmarks = face_data[0]['faceLandmarks']

        # Get size and positions of eyes, and generate sizes for the flares
        eye_left_width = math.ceil(landmarks['eyeLeftInner']['x'] - landmarks['eyeLeftOuter']['x'])
        eye_left_height = math.ceil(landmarks['eyeLeftBottom']['y'] - landmarks['eyeLeftTop']['y'])
        eye_left_corner = (landmarks['eyeLeftOuter']['x'], landmarks['eyeLeftTop']['y'])
        flare_left_size = eye_left_height if eye_left_height > eye_left_width else eye_left_width
        flare_left_size *= 4
        eye_left_corner = tuple(math.floor(x - flare_left_size / 2.5 + 5) for x in eye_left_corner)

        eye_right_width = math.ceil(landmarks['eyeRightOuter']['x'] - landmarks['eyeRightInner']['x'])
        eye_right_height = math.ceil(landmarks['eyeRightBottom']['y'] - landmarks['eyeRightTop']['y'])
        eye_right_corner = (landmarks['eyeRightInner']['x'], landmarks['eyeRightTop']['y'])
        flare_right_size = eye_right_height if eye_right_height > eye_right_width else eye_right_width
        flare_right_size *= 4
        eye_right_corner = tuple(math.floor(x - flare_right_size / 2.5 + 5) for x in eye_right_corner)

        # Copy and resize flares
        flare = Image.open('flare.png')
        flare_left = flare.copy().resize((flare_left_size,) * 2, resample=Image.BILINEAR)
        flare_right = flare.copy().resize((flare_right_size,) * 2, resample=Image.BILINEAR)

        del flare

        img.paste(flare_left, eye_left_corner, flare_left)
        img.paste(flare_right, eye_right_corner, flare_right)

    return img
