#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:27:19 2023

@author: sand-jrd
"""

from vip_hci.fits import open_fits
import matplotlib.pyplot as plt
import numpy as np
import photutils
from vip_hci.preproc import cube_crop_frames
from matplotlib.patches import Circle


#%% Params

path_cube = "./my_folder/my_cube.fits"

nb_app = 5
shape = 201
app_size = 8

same_fig = True 


# %% Crops + mask
cube = open_fits(path_cube)

if shape<cube.shape[1]: cube = cube_crop_frames(cube, shape)
else : shape = cube.shape[1]

def circle(shape: tuple, r: float, offset=(0.5, 0.5)):
    """ Create circle of 1 in a 2D matrix of zeros"
       
       Parameters
       ----------

       shape : tuple
           shape x,y of the matrix
       
       r : float
           radius of the circle
       offset : (optional) float
           offset from the center
       
       Returns
       -------
       M : ndarray
           Zeros matrix with a circle filled with ones
       
    """
    assert(len(shape) == 2 or len(shape) == 3)
    if isinstance(offset, (int, float)): offset = (offset, offset)

    nb_f  = shape[0]  if len(shape) == 3 else 0
    shape = shape[1:] if len(shape) == 3 else shape

    M = np.zeros(shape)
    w, l = shape
    for x in range(0, w):
        for y in range(0, l):
            if pow(x - (w // 2) + offset[0], 2) + pow(y - (l // 2) + offset[1], 2) < pow(r, 2):
                M[x, y] = 1

    if nb_f: M = np.tile(M, (nb_f, 1, 1))

    return M
pup = circle((shape,shape),shape//2) - circle((shape,shape),8)

cube = cube * pup
nb_frame = cube.shape[0]

#%% Select app position

plt.close("all")
img = cube[0]

plt.imshow(np.sqrt(abs(img)))
apps = plt.ginput(n=nb_app)
plt.close()

#%% Mesure flux points

flx_apps =[]
app_img =[]
for app_coo in apps:
    siftx = app_coo[0]
    sifty = app_coo[1]
    
    fwhm_aper = photutils.CircularAperture([siftx,sifty], app_size)
    app_img.append(fwhm_aper.to_mask().to_image(img.shape))
    flx_apps.append(np.array([photutils.aperture_photometry(frame, fwhm_aper,method='exact')["aperture_sum"] for frame in cube]))
    

#%% Plot

colors = ["tab:orange","tab:blue","tab:green","tab:purple","tab:red","black", "tab:pink"]

plt.figure("Flux variations in the different appertures")

ii=1
for flx in flx_apps : 
    if not same_fig : plt.subplot(1,nb_app,ii), 
    plt.plot([1]*nb_frame, color="lightgray")
    plt.plot(flx/flx[0], color=colors[ii-1], label="Apperture "+str(ii))
    ii+=1

plt.legend()

fig, ax = plt.subplots()
img = cube[4]
plt.imshow(np.sqrt(abs(img)))

ii=1
for app_coo in apps:
    xx = app_coo[0]
    yy = app_coo[1]
    circ = Circle((xx,yy),app_size, color=colors[ii-1])
    ax.add_patch(circ)
    plt.text(xx+app_size+2,yy+app_size+2, str(ii), color="white", size=10 )
    ii+=1

