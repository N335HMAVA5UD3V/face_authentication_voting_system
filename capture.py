import numpy as np
import os
import cv2
import face_recognition
import pickle

path = r"D:\deep_learning_projects\voting_system\faces"

images = []
labels = []
mylist = os.listdir(path)

for cl in mylist:
    imgpath = os.path.join(path, cl)

    current_image = cv2.imread(imgpath)
    images.append(current_image)
    labels.append(cl[:-4])


def find_encodings(images):
    encode_list = []
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        face_in_frame = face_recognition.face_locations(img)
        encode = face_recognition.face_encodings(img,face_in_frame)[0]
        encode_list.append(encode)
    return encode_list

encodelist_knownfaces = find_encodings(images)

video = cv2.VideoCapture(0)
while True:
    frame, img= video.read()
    if not frame:
        break
    face_in_frame = face_recognition.face_locations(img)
    encoded_face = face_recognition.face_encodings(img,face_in_frame)
    for encoded_face, faceloc in zip(encoded_face, face_in_frame):
        matches = face_recognition.compare_faces(encodelist_knownfaces,encoded_face)
        face_distance = face_recognition.face_distance(encodelist_knownfaces,encoded_face)
        matchindex = np.argmin(face_distance)

        if matches[matchindex]:
            name = labels[matchindex]
            labels.append(name)

            y1,x2,y2,x1 = faceloc
            cv2.rectangle(img,(x1,y1), (x2,y2), (0,255,0), 2)
            cv2.putText(img,name,(x1,y1), cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255), 2)
    cv2.imshow('Recognized Faces', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Save encodings and corresponding labels to a file using pickle
with open('known_faces_encodings.pkl', 'wb') as f:
    pickle.dump({'encodings': encodelist_knownfaces, 'labels': labels}, f)
