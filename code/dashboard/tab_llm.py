import streamlit as st
import os
import sys
from groq import Groq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db import update_problem_priority


def render_tab_ai(df_filtered):
    st.subheader("🤖 Αυτόματη Κατηγοριοποίηση με Τεχνητή Νοημοσύνη (Groq)")
    st.markdown(
        "Επιλέξτε μια υπάρχουσα αναφορά. Το LLM θα διαβάσει την περιγραφή του "
        "πολίτη και θα προτείνει την κατάλληλη κατηγορία και προτεραιότητα. "
        "Με ένα κλικ μπορείτε να καταχωρήσετε την προτεραιότητα στη βάση, ώστε "
        "ο Δήμος να έχει στατιστική εικόνα του τι αναφορές λαμβάνει."
    )

    if df_filtered.empty:
        st.warning("Δεν υπάρχουν αναφορές για ανάλυση με τα τρέχοντα φίλτρα.")
        return

    api_key = st.text_input(
        "Κλειδί API (Groq API Key):",
        type="password",
        help="Εισάγετε το Groq API Key σας από console.groq.com"
    )

    st.write("---")

    # Αντιστοίχιση αριθμού γραμμής "#N" -> πραγματικό ticket_id, ίδια σειρά με τα άλλα tabs
    reset_df = df_filtered.reset_index(drop=True)
    num_to_ticket = {i + 1: row['ticket_id'] for i, row in reset_df.iterrows()}

    problem_number = st.number_input(
        "Αριθμός Αναφοράς (#):",
        min_value=1,
        max_value=len(reset_df),
        value=1,
        step=1,
        key="ai_problem_number"
    )

    selected_ticket = num_to_ticket.get(problem_number)
    if selected_ticket is None:
        st.warning("Δεν υπάρχει αναφορά με αυτόν τον αριθμό.")
        return

    problem_row = df_filtered[df_filtered['ticket_id'] == selected_ticket].iloc[0]
    description_text = problem_row.get('description', '') or ''

    st.markdown(f"**📄 Τίτλος:** {problem_row.get('title', '—')}")
    st.markdown(f"**📝 Περιγραφή:**")
    st.info(description_text if description_text else "Δεν υπάρχει περιγραφή για αυτή την αναφορά.")

    st.write("---")

    if st.button("🧠 Ανάλυση Κειμένου με Groq LLM"):
        if not api_key:
            st.error("🚨 Παρακαλώ εισάγετε πρώτα ένα έγκυρο Groq API Key!")
            return

        if not description_text.strip():
            st.error("🚨 Αυτή η αναφορά δεν έχει περιγραφή για ανάλυση.")
            return

        with st.spinner("Το μοντέλο αναλύει το κείμενο..."):
            try:
                client = Groq(api_key=api_key)

                system_instruction = """
                Είσαι ένας έμπειρος ψηφιακός βοηθός Δήμου. Καθήκον σου είναι να διαβάζεις την περιγραφή ενός προβλήματος από έναν πολίτη και να επιλέγεις ΑΥΣΤΗΡΑ μία από τις ακόλουθες 7 κατηγορίες:
                1. Οδοποιία
                2. Ηλεκτροφωτισμός
                3. Καθαριότητα
                4. Ύδρευση
                5. Πράσινο
                6. Εγκαταλελειμμένα Οχήματα
                7. Βλάβες Δημόσιων Υποδομών

                Επίσης, πρέπει να αξιολογήσεις την Προτεραιότητα σε μία από τις τρεις τιμές: Χαμηλή, Μεσαία, Υψηλή.

                Απάντησε ΑΥΣΤΗΡΑ σε αυτή τη μορφή (μην γράψεις τίποτα άλλο, μην βάζεις αστεράκια ή έντονα γράμματα):
                ΚΑΤΗΓΟΡΙΑ: [Όνομα Κατηγορίας]
                ΠΡΟΤΕΡΑΙΟΤΗΤΑ: [Χαμηλή/Μεσαία/Υψηλή]
                ΑΙΤΙΟΛΟΓΗΣΗ: [Μια σύντομη πρόταση γιατί επιλέχθηκε αυτή η προτεραιότητα]
                """

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": description_text}
                    ],
                    temperature=0.1
                )

                ai_output = response.choices[0].message.content

                lines = ai_output.strip().split('\n')
                cat_result = "Δεν προσδιορίστηκε"
                priority_result = "Δεν προσδιορίστηκε"
                reason_result = ""

                for line in lines:
                    if line.startswith("ΚΑΤΗΓΟΡΙΑ:"):
                        cat_result = line.replace("ΚΑΤΗΓΟΡΙΑ:", "").strip()
                    elif line.startswith("ΠΡΟΤΕΡΑΙΟΤΗΤΑ:"):
                        priority_result = line.replace("ΠΡΟΤΕΡΑΙΟΤΗΤΑ:", "").strip()
                    elif line.startswith("ΑΙΤΙΟΛΟΓΗΣΗ:"):
                        reason_result = line.replace("ΑΙΤΙΟΛΟΓΗΣΗ:", "").strip()

                # Αποθηκεύουμε στο session_state ώστε να επιβιώσει μετά το rerun του κουμπιού καταχώρησης
                st.session_state['ai_cat_result'] = cat_result
                st.session_state['ai_priority_result'] = priority_result
                st.session_state['ai_reason_result'] = reason_result
                st.session_state['ai_analyzed_ticket'] = selected_ticket

            except Exception as e:
                st.error(f"🚨 Σφάλμα κατά την επικοινωνία με το Groq: {e}")

    # Εμφάνιση αποτελεσμάτων αν έχει γίνει ανάλυση για αυτό το ticket
    if st.session_state.get('ai_analyzed_ticket') == selected_ticket:
        cat_result = st.session_state['ai_cat_result']
        priority_result = st.session_state['ai_priority_result']
        reason_result = st.session_state['ai_reason_result']

        st.write("---")
        st.subheader("🎯 Αποτελέσματα Ανάλυσης AI")

        col1, col2 = st.columns(2)
        with col1:
            st.success(f"📌 **Προτεινόμενη Κατηγορία:** {cat_result}")
        with col2:
            if "Υψηλή" in priority_result:
                st.error(f"⚠️ **Προτεραιότητα:** {priority_result}")
            elif "Μεσαία" in priority_result:
                st.warning(f"⚡ **Προτεραιότητα:** {priority_result}")
            else:
                st.info(f"🟢 **Προτεραιότητα:** {priority_result}")

        if reason_result:
            st.markdown(f"**💡 Αιτιολόγηση Μοντέλου:** *{reason_result}*")

        st.write("---")
        if st.button("✅ Καταχώρηση Προτεραιότητας στη Βάση"):
            update_problem_priority(selected_ticket, priority_result)
            st.success(
                f"✅ Η προτεραιότητα '{priority_result}' καταχωρήθηκε για την αναφορά #{problem_number}. "
                f"Τα στατιστικά θα ανανεωθούν αυτόματα."
            )
            del st.session_state['ai_analyzed_ticket']
            st.rerun()