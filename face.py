import streamlit as st
import pandas as pd
import pickle
import face_recognition
import cv2
import os

# Load encodings and labels from the file

with open('known_faces_encodings.pkl', 'rb') as f:
    data = pickle.load(f)
    encodelist_knownfaces = data['encodings']
    labels = data['labels']

# Function to recognize faces in an image
def recognize_face(frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    for encoding in face_encodings:
        matches = face_recognition.compare_faces(encodelist_knownfaces, encoding)
        if True in matches:
            return labels[matches.index(True)]
    return "unknown"


def capture_images():
    video = cv2.VideoCapture(0)
    # Capture image button
    if st.button('Capture Image'):
        ret, frame = video.read()
        if ret:
            st.image(frame, channels="BGR", caption='Captured Image')
            # Perform face recognition
            name = recognize_face(frame)
            if name == "unknown":
                st.warning("Face not detected.")
            else:
                st.write("Recognized:", name)
                st.session_state.name = name  # Store the recognized name in session state
                st.session_state.step_index = 3  # Move to the Vote step
        return name
    return None

# Function to perform voting
def vote(name):
    st.title("Vote")
    voted_file = 'results.xlsx'
    if os.path.exists(voted_file):
        voted_list = pd.read_excel(voted_file)
    else:
        voted_list = pd.DataFrame(columns=['Name', 'Candidate'])

    selected_candidate = st.radio("Select candidate:", ("Candidate 1", "Candidate 2", "Candidate 3"))
    if st.button("Vote"):
        if selected_candidate:
            if name != "unknown":
                if name in voted_list['Name'].values:
                    st.error("You have casted your vote")
                    st.session_state.step_index = 2
                else:
                    st.success("Your vote was successful")
                    new_vote = pd.DataFrame({'Name': [name], 'Candidate': [selected_candidate]})
                    # Concatenate the new vote DataFrame with the existing voted_list DataFrame
                    voted_list = pd.concat([voted_list, new_vote], ignore_index=True)
                    # Save the updated DataFrame back to the Excel file
                    voted_list.to_excel(voted_file, index=False)
                    st.session_state.step_index = 2
        else:
            st.warning("Please select a candidate to vote for.")   
            
st.sidebar.title('Navigation')
steps = ['Home', 'Admin', 'Capture Images', 'Vote']
current_step_index = st.session_state.get('step_index', 0)
navigation = st.sidebar.radio("Go to", steps[current_step_index:])


if navigation == 'Home':
    st.title('Home')
    st.write('Welcome to Smart Voting System!')
    st.session_state.step_index = 1

elif navigation == 'Admin':
    if current_step_index == 1:
        st.title('Admin')
        email = st.text_input('UserId')
        password = st.text_input('Password', type='password')
        if st.button('Login'):
            if (email == 'admin@voting.com') and (password == 'admin'):
                st.success('Admin login successful')
                st.session_state.step_index = 2
            else:
                st.error('Invalid credentials')


elif navigation == 'Capture Images':
    if current_step_index == 2:
        st.title('Capture Images')
        name = capture_images()
        if name:
            st.session_state.images_captured = True
            st.session_state.name = name
            st.session_state.step_index = 3
        else:
            st.session_state.images_captured = False
            
elif navigation == 'Vote':
    if current_step_index == 3:
        if st.session_state.get('images_captured'):
            vote(st.session_state.get('name'))
        else:
            st.write("please capture image first")
            st.session_state.step_index = 2
            
            
    
        