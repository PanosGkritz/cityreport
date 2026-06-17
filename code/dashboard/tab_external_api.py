import streamlit as st
import requests


def get_address_from_coords(lat, lon):
    """
    Καλεί το εξωτερικό REST API του OpenStreetMap (Nominatim) για να
    μετατρέψει συντεταγμένες (lat, lon) σε αναγνωστή διεύθυνση.
    Δωρεάν, δεν απαιτεί API key.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json"}
    # Το Nominatim απαιτεί User-Agent header, αλλιώς απορρίπτει το request
    headers = {"User-Agent": "CityReportApp/1.0"}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def render_tab_external(df_filtered):
    st.subheader("🌍 Υποσύστημα Εύρεσης Διεύθυνσης")
    st.markdown(
        "Το σύστημα CityReport αποθηκεύει κάθε αναφορά με συντεταγμένες "
        "(latitude/longitude). Εδώ μπορείτε να επιλέξετε μια υπάρχουσα αναφορά "
        "και να ανακτήσετε αυτόματα την αναγνωστή διεύθυνσή της μέσω του "
        "**OpenStreetMap Nominatim API** (εξωτερική υπηρεσία geocoding)."
    )

    if df_filtered.empty:
        st.warning("Δεν υπάρχουν αναφορές για επεξεργασία με τα τρέχοντα φίλτρα.")
        return

    st.write("---")

    # Αντιστοίχιση αριθμού γραμμής "#N" -> πραγματικό ticket_id
    reset_df = df_filtered.reset_index(drop=True)
    num_to_ticket = {i + 1: row['ticket_id'] for i, row in reset_df.iterrows()}

    problem_number = st.number_input(
        "Αριθμός Αναφοράς (#):",
        min_value=1,
        max_value=len(reset_df),
        value=1,
        step=1,
        key="external_api_problem_number"
    )

    selected_ticket = num_to_ticket.get(problem_number)
    if selected_ticket is None:
        st.warning("Δεν υπάρχει αναφορά με αυτόν τον αριθμό.")
        return

    problem_row = df_filtered[df_filtered['ticket_id'] == selected_ticket].iloc[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Τίτλος", problem_row.get('title', '—'))
    with col2:
        lat = problem_row.get('latitude')
        st.metric("Latitude", f"{lat:.4f}" if lat else "—")
    with col3:
        lon = problem_row.get('longitude')
        st.metric("Longitude", f"{lon:.4f}" if lon else "—")

    st.write("")

    if lat and lon:
        if st.button("📍 Εύρεση Διεύθυνσης"):
            with st.spinner("Κλήση στο OpenStreetMap Nominatim API..."):
                try:
                    data = get_address_from_coords(lat, lon)

                    if "display_name" in data:
                        st.success(f"📌 **Πλήρης Διεύθυνση:** {data['display_name']}")

                        address = data.get("address", {})
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.info(f"**Δρόμος:**\n{address.get('road', '—')}")
                        with col2:
                            st.info(
                                f"**Περιοχή:**\n"
                                f"{address.get('suburb', address.get('city_district', '—'))}"
                            )
                        with col3:
                            st.info(
                                f"**Πόλη:**\n"
                                f"{address.get('city', address.get('town', '—'))}"
                            )
                    else:
                        st.warning("Δεν βρέθηκε διεύθυνση για αυτές τις συντεταγμένες.")

                except requests.exceptions.RequestException as e:
                    st.error(f"🚨 Σφάλμα κατά την κλήση του εξωτερικού API: {e}")
    else:
        st.caption("Δεν υπάρχουν έγκυρες συντεταγμένες για αυτή την αναφορά.")