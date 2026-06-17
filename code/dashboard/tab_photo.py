import streamlit as st
import os

def render_tab_photo(df_filtered):
    st.subheader("📷 Προβολή Φωτογραφιών Αναφοράς")
    
    if df_filtered.empty:
        st.warning("Δεν υπάρχουν αναφορές με τα τρέχοντα φίλτρα.")
        return

    # 1. Reset index για να έχουμε καθαρούς αύξοντες αριθμούς (1, 2, 3...)
    reset_df = df_filtered.reset_index(drop=True)
    
    # 2. Φτιάχνουμε λεξικά για να βρίσκουμε εύκολα τον τίτλο και τη φωτογραφία από τον αριθμό
    num_to_title = {i + 1: row['title'] for i, row in reset_df.iterrows()}
    num_to_photo = {i + 1: row.get('photo_path') for i, row in reset_df.iterrows()}

    # 3. Πεδίο εισαγωγής αριθμού με μοναδικό key
    problem_number = st.number_input(
        "Αριθμός Αναφοράς (#):",
        min_value=1,
        max_value=len(reset_df),
        value=1,
        step=1,
        key="photo_tab_number_input" # Η μαγική λέξη που λύνει το error
    )
    
    st.write("---")

    # Ελέγχουμε αν ο αριθμός είναι έγκυρος
    if problem_number in num_to_title:
        # Δείχνουμε τον τίτλο της αναφοράς
        st.markdown(f"### 📄 Αναφορά #{problem_number}: {num_to_title[problem_number]}")
        
        photo_path = num_to_photo[problem_number]
        
        # 4. Έλεγχος φωτογραφίας
        if photo_path and str(photo_path).strip() != "" and str(photo_path).lower() != "none":
            
            # Βρίσκουμε το απόλυτο path της εικόνας
            clean_path = str(photo_path).replace('code/', '') 
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            full_path = os.path.join(base_dir, clean_path)

            # Αν το αρχείο υπάρχει στον φάκελο uploads
            if os.path.exists(full_path):
                st.image(full_path, caption=f"Φωτογραφία αναφοράς: {num_to_title[problem_number]}", use_container_width=True)
            else:
                st.info(f"ℹ️ Η βάση αναφέρει το αρχείο '{photo_path}', αλλά η φωτογραφία δεν βρέθηκε στον φάκελο. (Αναμονή για υλοποίηση Upload από το backend)")
        else:
            st.info("ℹ️ Ο πολίτης δεν επισύναψε φωτογραφία για αυτή την αναφορά.")
    else:
        st.warning("⚠️ Δεν βρέθηκε αναφορά με αυτόν τον αριθμό.")