# I/O functionality for ODMax
import os
import cv2
import ffmpegcv
from odmax import helpers
from datetime import datetime
import gpxpy
import piexif
from PIL import Image

# high level variables
PATH = os.path.dirname(__file__)
gpx_fmt_fn = os.path.join(PATH, "gpx.fmt")
if os.name == "posix":
    null_output = "/dev/null 2>&1"
else:
    null_output = "nul"

# pil uses specific encoder names such as "jpeg", translate if necessary using the below dict
pil_encoders = {
    "jpg": "jpeg"
}


def to_pil(array):
    """
    Converts ND-array into PIL object

    :param array: ND-array with colors (3rd dimension) in RGB order
    :return: PIL image
    """
    return Image.fromarray(array)


def open_file(fn):
    """
    Open file for reading by cv2.

    :param fn: video file (cv2 compatible)
    :return: cv2 pointer to file
    """
    assert(isinstance(fn, str)), "No valid file provided, should be of type str"
    assert(os.path.isfile(fn)), f"File {fn} was not found"
    if isinstance(fn, str):
        # try to open file with openCV
        f = ffmpegcv.VideoCapture(fn, pix_fmt='rgb24')
        return f
    else:
        raise TypeError(f"{fn} should be a string pointing to a path")

def get_frame_number(f, time):
    """
    Get the frame number belonging to the defined time in seconds.

    :param f: pointer to opened video file
    :param time: seconds from start of video
    :return:
    """
    fps = f.fps
    frame_count = len(f)
    return int(min(frame_count, time * fps))

def read_frame(f, n):
    """
    Reads frame number n from opened video file f.

    :param f: pointer to opened video file
    :param n: frame number
    :return: img, blob containing frame
    """
    assert isinstance(n, int), f"{n} is not an integer"
    # check if frame is beyond length of movie
    nframes = len(f)
    if n > len(f):
        raise ValueError(f"The requested frame number {n} is larger than the available frames {nframes}")
    # wind to the right frame number

    # extract this frame
    success, img = f.read()
    if success:
        return img
    else:
        raise IOError(f"The requested frame {n} could not be extracted. Perhaps the videofile is damaged.")


def write_frame(img, fn, encoder="jpg", exif_dict={}):
    """
    Writes a frame to a file or bytestream. If a 6-face cube list is provided, 6 files will be written using
    "F", "R", "B", "L", "U", "D" as suffixes for "front", "right", "back", "left", "up" and "down".

    :param img: ndarray or list of 6 ndarrays of size [H, W, 3]
    :param fn: path or io.BytesIO object to write frame to
    :param encoder: PIL compatible encoder to use for writing
    :param exif_dict: dictionary with EXIF tag groups and tags within groups (e.g. "GPS")
    :return:
    """

    # determine PIL encoder
    if encoder in pil_encoders:
        # translate
        p_encoder = pil_encoders[encoder]
    else:
        p_encoder = encoder
    try:
        exif = piexif.dump(exif_dict)
    except:
        raise ValueError(f"EXIF dict is invalid {exif_dict}")
    # now save with the intended metadata and filename
    to_pil(img).save(fn, p_encoder.lower(), exif=exif)

def get_exif(fn, fn_out):
    """
    Reads the exif tag from a video and writes it to a file.

    :param fn: video filename
    :param fn_out: text file to write exif tag to
    :return:
    """
    if not(os.path.isfile(fn)):
        raise IOError(f"File {fn} does not exist")
    if not(os.path.isdir(os.path.split(fn_out)[0])):
        raise IOError(f"Path {os.path.split(fn_out)[0]} is not available")
    # FIXME: complete this code
    raise NotImplementedError("Not implemented yet")


def get_gpx(fn):
    """
    Reads the gpx track from a video and writes it to a file.

    :param fn: video filename
    :return: parsed gpx data
    """
    if not(os.path.isfile(fn)):
        raise IOError(f"File {fn} does not exist")
    return gpxpy.parse(helpers.exiftool('-ee', '-p', f"{gpx_fmt_fn}", fn))


