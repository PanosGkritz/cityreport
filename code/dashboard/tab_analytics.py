import streamlit as st
import pandas as pd

# Συνάρτηση που σχεδιάζει το Tab 2 (Στατιστικά & Χάρτης)
def render_tab_analytics(df_filtered):
    st.subheader("Στατιστική Ανάλυση & Γεωγραφικός Χάρτης") 
     
    if df_filtered.empty:
        st.warning("Δεν υπάρχουν δεδομένα για την εμφάνιση στατιστικών. :warning:")
        return

    #   Κάρτες με μετρικά
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Συνολικές Αναφορές", len(df_filtered))
    with col2:
        pending = len(df_filtered[df_filtered['Κατάσταση'] == 'Αναφέρθηκε'])
        st.metric("Νέες Αναφορές", pending)
    with col3:
        in_progress = len(df_filtered[df_filtered['Κατάσταση'] == 'Σε εξέλιξη'])
        st.metric("Σε Εξέλιξη", in_progress)

    st.write("---")

    # Γράφημα ανα κατηγορία (bar charts)
    st.subheader("🗂️ Πλήθος Προβλημάτων ανά Κατηγορία")
    # Ομαδοποιούμε τα δεδομένα για να μετρήσουμε πόσα προβλήματα έχει κάθε κατηγορία
    category_counts = df_filtered['Κατηγορία'].value_counts()
    st.bar_chart(category_counts)

    st.write("---")

    # Γράφημα κατανομής Προτεραιότητας (βάσει των καταχωρήσεων από το Υποσύστημα AI)
    st.subheader("⚡ Κατανομή Προτεραιότητας (AI)")
    st.markdown(
        "*Στατιστικά με βάση τις προτεραιότητες που έχουν καταχωρηθεί από το "
        "Υποσύστημα Τεχνητής Νοημοσύνης (tab 'Υποσύστημα AI').*"
    )

    if 'ai_priority' in df_filtered.columns:
        # Κρατάμε μόνο τις αναφορές που έχουν ήδη αξιολογηθεί από το AI
        priority_data = df_filtered['ai_priority'].dropna()

        if not priority_data.empty:
            priority_counts = priority_data.value_counts()

            # Σταθερή σειρά εμφάνισης Χαμηλή -> Μεσαία -> Υψηλή (αν υπάρχουν)
            order = ['Χαμηλή', 'Μεσαία', 'Υψηλή']
            priority_counts = priority_counts.reindex(
                [p for p in order if p in priority_counts.index]
            ).combine_first(priority_counts)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.bar_chart(priority_counts)
            with col2:
                for level in order:
                    count = int(priority_counts.get(level, 0))
                    if level == 'Υψηλή':
                        st.error(f"⚠️ Υψηλή: {count}")
                    elif level == 'Μεσαία':
                        st.warning(f"⚡ Μεσαία: {count}")
                    else:
                        st.success(f"🟢 Χαμηλή: {count}")

            not_evaluated = len(df_filtered) - len(priority_data)
            if not_evaluated > 0:
                st.caption(f"ℹ️ {not_evaluated} αναφορές δεν έχουν ακόμα αξιολογηθεί από το AI.")
        else:
            st.info("Δεν έχουν καταχωρηθεί ακόμα προτεραιότητες από το Υποσύστημα AI.")
    else:
        st.info("Η στήλη προτεραιότητας δεν είναι διαθέσιμη.")

    st.write("---")

    # Γεογραφικός χάρτης (MAP)
    st.subheader("📍 Γεωγραφική Κατανομή Αναφορών στην Πόλη")
    st.markdown("*Εστιάστε στον χάρτη για να δείτε τα ακριβή σημεία των προβλημάτων.*")
    
    # Το Streamlit για να σχεδιάσει χάρτη θέλει ένα DataFrame με τις στήλες 'latitude' και 'longitude'
    # Επειδή στο κεντρικό αρχείο αλλάξαμε τα ονόματα των στηλών για το UI, ξαναπαίρνουμε τα original ονόματα
    if 'latitude' in df_filtered.columns and 'longitude' in df_filtered.columns:
        map_data = df_filtered[['latitude', 'longitude']].dropna()
        if not map_data.empty:
            st.map(map_data)
        else:
            st.info("Δεν υπάρχουν έγκυρες συντεταγμένες για εμφάνιση στον χάρτη.")
    else:
        st.info("Οι συντεταγμένες δεν είναι διαθέσιμες στο τρέχον φιλτράρισμα.")