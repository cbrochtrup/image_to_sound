#!/usr/bin/env python 

import os

import numpy as np
from scipy import signal
import PIL
import PIL.Image
import PIL.ImageStat
import soundfile as sf
from fire import Fire


def image_to_stft(image_in, rescaling, fs, out_length=-1):
  """
  Convert image to fft and rescale pixels to 
  """
  img = PIL.Image.open(image_in).convert(mode='L').transpose(PIL.Image.FLIP_TOP_BOTTOM)
  if out_length > 0:
    # scipy istft assumes returns a signal with number of samples about equal to img.size[0] * img.size[1]
    needed_pixels = int(out_length * fs / img.size[1])
    img = img.resize((needed_pixels, img.size[1]))
  img_min, img_max = PIL.ImageStat.Stat(img).extrema[0]
  
  
  # This rescalilng gives the spectrogram more dynamic range in darks parts images which
  # seems to be more important than the bright regions.
  normalized_fft_arr = ((np.array(img) - img_min)/(img_max - img_min)) ** rescaling
  return normalized_fft_arr
  

def stft_to_file(fft_arr, fs, out_file_name):
  """
  Convert fft array to sound and write to file
  """
  t, xrec = signal.istft(fft_arr, fs)
  xrec = (((xrec + min(xrec))) * (2 ** (15)-1) / xrec.ptp()).astype(np.int16)
  sf.write(out_file_name, xrec, fs)


def image_to_sound(image_in, out_file=None, out_duration=-1, rescale=10, fs=41000):
  """
  out_durations is in units of seconds
  rescale rescales the fft with magnitude in the range [0,1]
    fft_new = fft_old ** rescale
  rescale > 1 will give more dynamic range to dark values of image
  rescale < 1 will give more dynamic range to light values of image
  """
  img_stft = image_to_stft(image_in, rescale, fs, out_duration)

  if out_file is None :
    out_file = os.path.splitext(os.path.basename(image_in))[0] + '.wav'
  stft_to_file(img_stft, fs, out_file)


if __name__ == '__main__':
  Fire(image_to_sound)
