import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db import update_problem_status, get_categories, get_statuses


def render_tab_manage(df_filtered):
    st.subheader("📋 Λίστα και Διαχείριση Αναφορών")

    if df_filtered.empty:
        st.warning("Δεν υπάρχουν αναφορές για διαχείριση με τα τρέχοντα φίλτρα.")
        return

    # Χρειάζεται μόνο για το selectbox κατάστασης
    stats = {s['id']: s['name'] for s in get_statuses()}

    # Προετοιμασία πίνακα
    display_df = df_filtered.rename(columns={
        'ticket_id':  'Ticket ID',
        'title':      'Τίτλος',
        'created_at': 'Ημερομηνία'
    }).copy()

    cols_to_show = ['Τίτλος', 'Κατηγορία', 'Κατάσταση', 'Ημερομηνία']
    grid_df = display_df[cols_to_show].copy()
    grid_df.insert(0, 'Επιλογή', False)
    grid_df.insert(0, '#', range(1, len(grid_df) + 1))

    st.markdown("**Επιλέξτε μια αναφορά (τικάρετε το κουτάκι) για να την ενημερώσετε:**")

    edited_df = st.data_editor(
        grid_df,
        hide_index=True,
        width='stretch',
        disabled=['#', 'Τίτλος', 'Κατηγορία', 'Κατάσταση', 'Ημερομηνία']
        # Η "Επιλογή" ΔΕΝ είναι disabled
    )

    # Παίρνουμε το ticket_id από το df_filtered με βάση το index
    selected_rows = edited_df[edited_df["Επιλογή"] == True]
    if not selected_rows.empty:
        selected_ticket = df_filtered.iloc[selected_rows.index[0]]['ticket_id']
    else:
        selected_ticket = ""

    st.write("---")
    st.subheader("✏️ Αλλαγή Κατάστασης Προβλήματος")

    # Αντιστοίχιση αριθμού γραμμής "#N" -> πραγματικό ticket_id, ίδια σειρά με τον πίνακα
    reset_df = df_filtered.reset_index(drop=True)
    num_to_ticket = {i + 1: row['ticket_id'] for i, row in reset_df.iterrows()}
    num_to_title = {i + 1: row['title'] for i, row in reset_df.iterrows()}

    # Προεπιλεγμένος αριθμός: αν έχει γίνει επιλογή πάνω στον πίνακα, τον δείχνουμε
    ticket_to_num = {v: k for k, v in num_to_ticket.items()}
    default_num = ticket_to_num.get(selected_ticket, 1)

    col1, col2 = st.columns(2)
    with col1:
        problem_number = st.number_input(
            "Αριθμός Αναφοράς (#):",
            min_value=1,
            max_value=len(reset_df),
            value=default_num,
            step=1
        )

        # Αν ο αριθμός είναι έγκυρος, δείχνουμε τίτλο για επιβεβαίωση
        if problem_number in num_to_title:
            st.caption(f"📄 {num_to_title[problem_number]}")
            selected_ticket_dd = num_to_ticket[problem_number]
        else:
            st.caption("⚠️ Δεν υπάρχει αναφορά με αυτόν τον αριθμό.")
            selected_ticket_dd = None

    with col2:
        new_status_name = st.selectbox("Επιλέξτε Νέα Κατάσταση:", list(stats.values()))
        status_map = {v: k for k, v in stats.items()}

    admin_comment = st.text_area("Σχόλιο Διαχειριστή:")

    if st.button("💾 Αποθήκευση Αλλαγής"):
        if selected_ticket_dd:
            update_problem_status(selected_ticket_dd, status_map[new_status_name], admin_comment)
            st.success(f"✅ Η αναφορά #{problem_number} ενημερώθηκε!")
            st.rerun()
        else:
            st.error("🚨 Παρακαλώ εισάγετε έγκυρο αριθμό αναφοράς.")