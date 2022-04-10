import pandas as pd
import spotpy as sp
import streamlit as st

st.set_page_config(
    page_title="Alien Music Recommender",
    page_icon="👽")

st.title(" 👽 alien music recommender")

placeholder = st.empty()



st.text_input("Please enter your song", key="music")

songs = sp.search_song(st.session_state.music)

if st.session_state.music != "":

    option = st.selectbox(
        'Which artist do you prefer?',
         songs["artist"])
    tracks, org, hot_or_not = sp.process_chosen_song(st.session_state.music, option)

    if len(tracks) != 0 and len(org) != 0:
        st.header("Your choice is " + hot_or_not + "!!!")
        if len(org) != 0:
            st.text(org.iloc[0,1])

            st.text(org.iloc[0,0])

            st.text(org.iloc[0,2])

            st.image(org.iloc[0,5])

            if org.iloc[0, 3] != None:

                st.audio(org.iloc[0, 3])

        st.header("Our recommendation!!!")
        if len(tracks) != 0:
            st.text(tracks.iloc[0,1])

            st.text(tracks.iloc[0,0])

            st.text(tracks.iloc[0,2])

            st.image(tracks.iloc[0,5])

            if tracks.iloc[0, 3] != None:

                st.audio(tracks.iloc[0, 3])






