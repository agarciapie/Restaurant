import streamlit as st         # Llibreria per crear apps web interactives
import json                    # Per guardar i carregar dades en format JSON
import os                      # Per operacions amb fitxers

USERS_FILE = "users.json"      # Fitxer on es guarden els usuaris

# Carrega els usuaris del fitxer JSON
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Desa els usuaris al fitxer JSON
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)

# Retorna el nom del fitxer de restaurants per a cada usuari
def get_user_data_file(username):
    return f"{username}_restaurants.json"

# Carrega la llista de restaurants d'un usuari
def load_restaurants(username):
    file = get_user_data_file(username)
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Desa la llista de restaurants d'un usuari
def save_restaurants(username, data):
    file = get_user_data_file(username)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# Registra un nou usuari si no existeix
def register_user(users, username, password):
    if username in users:
        return False
    users[username] = password
    save_users(users)
    return True

# Comprova si l'usuari i contrasenya són correctes
def authenticate(users, username, password):
    return users.get(username) == password

# --- Modern CSS per millorar l'aparença ---
st.markdown("""
    <style>
    .main {background-color: #f7f7f9;}
    .stApp {background-color: #f7f7f9;}
    .stButton>button {background-color: #009688; color: white; border-radius: 6px;}
    .stTextInput>div>input, .stTextArea>div>textarea {border-radius: 6px;}
    .stSlider>div {color: #009688;}
    .stForm {background-color: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px #ddd;}
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ Registre de Restaurants")  # Títol principal de l'app

users = load_users()  # Carrega usuaris
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Pantalla d'inici de sessió/registre
if not st.session_state.logged_in:
    st.subheader("Inici de sessió / Registre")
    username = st.text_input("Usuari")
    password = st.text_input("Contrasenya", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar"):
            if authenticate(users, username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Sessió iniciada!")
                st.rerun()  # Recarrega la pàgina
            else:
                st.error("Usuari o contrasenya incorrectes.")
    with col2:
        if st.button("Crear compte"):
            if register_user(users, username, password):
                st.success("Compte creat! Ara pots iniciar sessió.")
            else:
                st.error("Aquest usuari ja existeix.")
    st.stop()  # Atura l'execució fins que l'usuari s'identifica

username = st.session_state.username
restaurants = load_restaurants(username)  # Carrega restaurants de l'usuari

# Menú lateral per navegar entre seccions
menu = st.sidebar.radio(
    "Menú",
    ("Presentació", "Restaurants registrats", "Afegir restaurant"),
    index=0
)

# Pàgina de presentació amb imatge i instruccions
if menu == "Presentació":
    st.image(
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
        use_container_width=True,
        caption="Benvingut/da a la teva agenda de restaurants!"
    )
    st.markdown("""
    ### Què pots fer amb aquesta aplicació?
    - **Registrar** restaurants que visites amb tota la informació rellevant.
    - **Valorar** i afegir comentaris personals.
    - **Consultar** la teva llista privada de restaurants.
    - **Editar o eliminar** qualsevol fitxa.
    - Les dades són privades per cada usuari.

    #### Com funciona?
    1. Accedeix amb el teu usuari.
    2. Utilitza el menú lateral per afegir o consultar restaurants.
    3. Pots editar o eliminar qualsevol restaurant des de la llista.

    ---
    """)

# Formulari per afegir un nou restaurant
elif menu == "Afegir restaurant":
    st.subheader("Afegeix un restaurant")
    with st.form("add_restaurant"):
        nom = st.text_input("Nom del restaurant")
        adreca = st.text_input("Adreça")
        telefon = st.text_input("Telèfon reserves")
        mapa = st.text_input("Enllaç de mapa (Google Maps)")
        comentaris = st.text_area("Comentaris")
        valoracio = st.slider("Valoració", 1, 5, 3)
        submit = st.form_submit_button("Guardar")
        if submit and nom:
            restaurants.append({
                "nom": nom,
                "adreca": adreca,
                "telefon": telefon,
                "mapa": mapa,
                "comentaris": comentaris,
                "valoracio": valoracio
            })
            save_restaurants(username, restaurants)
            st.success("Restaurant guardat!")
            st.rerun()  # Recarrega la pàgina per mostrar la nova llista

# Llista de restaurants registrats amb opció d'editar
elif menu == "Restaurants registrats":
    st.subheader("Restaurants registrats")
    if not restaurants:
        st.info("Encara no has registrat cap restaurant.")
    for idx, r in enumerate(restaurants):
        st.markdown(f"**{r['nom']}** ({r['valoracio']}/5)")
        st.write(f"Adreça: {r['adreca']}")
        st.write(f"Telèfon: {r['telefon']}")
        if r['mapa']:
            st.markdown(f"[Veure al mapa]({r['mapa']})")
        st.write(f"Comentaris: {r['comentaris']}")
        edit_key = f"edit_{idx}"
        if st.button("Editar", key=edit_key):
            st.session_state.edit_idx = idx
        st.markdown("---")

# Formulari per editar o eliminar un restaurant
if "edit_idx" in st.session_state:
    idx = st.session_state.edit_idx
    r = restaurants[idx]
    st.subheader(f"Edita el restaurant: {r['nom']}")
    with st.form("edit_restaurant"):
        nom = st.text_input("Nom del restaurant", value=r["nom"])
        adreca = st.text_input("Adreça", value=r["adreca"])
        telefon = st.text_input("Telèfon reserves", value=r["telefon"])
        mapa = st.text_input("Enllaç de mapa (Google Maps)", value=r["mapa"])
        comentaris = st.text_area("Comentaris", value=r["comentaris"])
        valoracio = st.slider("Valoració", 1, 5, r["valoracio"])
        submit = st.form_submit_button("Desar canvis")
        cancel = st.form_submit_button("Cancel·lar")
        delete = st.form_submit_button("Eliminar")
        if submit:
            restaurants[idx] = {
                "nom": nom,
                "adreca": adreca,
                "telefon": telefon,
                "mapa": mapa,
                "comentaris": comentaris,
                "valoracio": valoracio
            }
            save_restaurants(username, restaurants)
            st.success("Restaurant actualitzat!")
            del st.session_state.edit_idx
            st.rerun()
        if cancel:
            del st.session_state.edit_idx
            st.rerun()
        if delete:
            restaurants.pop(idx)
            save_restaurants(username, restaurants)
            st.success("Restaurant eliminat!")
            del st.session_state.edit_idx
            st.rerun()