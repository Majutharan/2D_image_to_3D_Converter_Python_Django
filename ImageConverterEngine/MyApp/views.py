from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
import json

import pydicom as dicom
import os
import matplotlib.pyplot as plt
import sys
import glob
import numpy as np


@api_view(["POST"])
def IdealWeight(heightdata):
    try:
        height = json.loads(heightdata.body)
        weight = str(height * 10)
        return JsonResponse("Ideal weight should be:" + weight + " kg", safe=False)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def Upload(request):
    for count, x in enumerate(request.FILES.getlist("files")):
        def handle_uploaded_file(f):
            with open('C:\\Users\\A Majutharan\\Documents\\sajitha\\ImageConverterEngine\\media\\file_' + str(
                    count) + '.dcm',
                      'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

        handle_uploaded_file(x)
    return JsonResponse("successfully uploaded", safe=False)


@api_view(["GET"])
def ImageConvertor(request):
    path = "C:\\Users\\A Majutharan\\Documents\\sajitha\\ImageConverterEngine\\media"
    ct_images = os.listdir(path)
    slices = [dicom.read_file(path + '/' + s, force=True) for s in ct_images]
    slices[0].ImagePositionPatient[2]
    slices = sorted(slices, key=lambda x: x.ImagePositionPatient[2])

    print(slices)
    # Read a dicom file with a ctx manager
    with dicom.dcmread(path + '/' + ct_images[0]) as ds:
        # plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
        print(ds)
        # plt.show()

    fig = plt.figure()
    for num, each_slice in enumerate(slices[:12]):
        y = fig.add_subplot(3, 4, num + 1)
        # print(each_slice)
        y.imshow(each_slice.pixel_array)
    # plt.show()

    for i in range(len(ct_images)):
        with dicom.dcmread(path + '/' + ct_images[i], force=True) as ds:
            plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
            # plt.show()

    # pixel aspects, assuming all slices are the same
    ps = slices[0].PixelSpacing
    ss = slices[0].SliceThickness
    ax_aspect = ps[1] / ps[0]
    sag_aspect = ps[1] / ss
    cor_aspect = ss / ps[0]

    # create 3D array
    img_shape = list(slices[0].pixel_array.shape)
    img_shape.append(len(slices))
    img3d = np.zeros(img_shape)

    # fill 3D array with the images from the files
    for i, s in enumerate(slices):
        img2d = s.pixel_array
        img3d[:, :, i] = img2d

    # plot 3 orthogonal slices
    a1 = plt.subplot(2, 2, 1)
    plt.imshow(img3d.sum(2), cmap=plt.cm.bone)
    a1.set_aspect(ax_aspect)

    a2 = plt.subplot(2, 2, 2)
    plt.imshow(img3d.sum(1), cmap=plt.cm.bone)
    a2.set_aspect(sag_aspect)

    a3 = plt.subplot(2, 2, 3)
    plt.imshow(img3d.sum(0).T, cmap=plt.cm.bone)
    a3.set_aspect(cor_aspect)

    plt.show()
    return JsonResponse("successfully converted", safe=False)


@api_view(["GET"])
def DeleteImages(request):
    folder = 'C:\\Users\\A Majutharan\\Documents\\sajitha\\ImageConverterEngine\\media'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    return JsonResponse("successfully deleted all files", safe=False)
