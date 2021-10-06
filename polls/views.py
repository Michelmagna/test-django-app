from django.http import HttpResponse
from rest_framework.decorators import api_view
import cv2
import numpy as np
import boto3
from botocore.exceptions import ClientError
import base64
import json

def comparar_rostros(bytes_imagen1, bytes_imagen2):
    #bytes_1 = bytes(bytes_imagen1, 'utf-8')
    #bytes_2 = bytes(bytes_imagen2, 'utf-8')
    bytes_1 = bytes_imagen1
    bytes_2 = bytes_imagen2

    with open("carnet.txt", "w") as file:
        file.write(str(bytes_1))
    with open("foto.txt", "w") as file:
        file.write(str(bytes_2))
    cliente = boto3.client("rekognition")
    try: 
        respuesta = cliente.compare_faces(SourceImage = {"Bytes": bytes_1},
                                                        TargetImage = {"Bytes": bytes_2},
                                                        SimilarityThreshold = 60,
                                                        QualityFilter = "AUTO")                                        
        #QuealityFilter = NONE|AUTO|LOW|MEDIUM|HIGH
        values = []
        if respuesta and respuesta["ResponseMetadata"]["HTTPStatusCode"] == 200:
            #UnmatchedFaces
            for i in respuesta ["UnmatchedFaces"]:
                print(i)
            for i in respuesta["FaceMatches"]:
                values.append(str(i["Similarity"]))
        if len(values) == 0:
            return [0]
        else:
            return values
    except ClientError:
        print("Error con la api")



@api_view(['GET','POST'])
def index(request):
    if request.method == "POST":
        #print(type(request.data["file"].read()))
        print(request.data["file"].read())
        base64_bytes_carnet = request.data["carnet_image"].encode('utf-8')
        base64_bytes_face = request.data["face_image"].encode('utf-8')
        bytesArray_carnet = base64.decodebytes(base64_bytes_carnet)
        bytesArray_face = base64.decodebytes(base64_bytes_face)
        similarityValue = float(comparar_rostros(bytesArray_carnet, bytesArray_face)[0])
        jsonResponse = {"similarity": similarityValue}
        return HttpResponse(json.dumps(jsonResponse))
    else:
        return HttpResponse("Metodo Get")

