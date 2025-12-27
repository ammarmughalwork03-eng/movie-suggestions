import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


st.set_page_config(
    page_title="🎬 Neon Red Cinema Movie Recommender",
    page_icon="🎥",
    layout="wide"
)


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

st.sidebar.title("🎬 Neon Red Cinema Selector")
mode = st.sidebar.radio("Choose Theme:", ["Dark Mode", "Light Mode"], index=0 if st.session_state.dark_mode else 1, on_change=toggle_mode)


@st.cache_data
def load_movies():
    df = pd.read_csv("movies.csv")
    if "runtime" not in df.columns:
        df["runtime"] = 120
    else:
        df["runtime"] = pd.to_numeric(df["runtime"], errors='coerce').fillna(120).astype(int)
    if "streaming_services" not in df.columns:
        df["streaming_services"] = ""
    else:
        df["streaming_services"] = df["streaming_services"].fillna("")
    return df

movies = load_movies()


cv = CountVectorizer()
genre_matrix = cv.fit_transform(movies["genres"])
similarity = cosine_similarity(genre_matrix)

def recommend(movie_title, top_n=6):
    try:
        idx = movies[movies["title"] == movie_title].index[0]
    except IndexError:
        return []
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = scores[1:top_n+1]
    return [movies.iloc[i[0]] for i in scores]


if "favorites" not in st.session_state:
    st.session_state.favorites = set()


search = st.sidebar.text_input("Search for a movie:")
genre_options = ["All"] + sorted({g for sublist in movies["genres"].str.split() for g in sublist})
selected_genre = st.sidebar.selectbox("Filter by genre:", genre_options)

min_runtime = int(movies["runtime"].min())
max_runtime = int(movies["runtime"].max())
if min_runtime == max_runtime:
    max_runtime += 10

selected_runtime = st.sidebar.slider("Filter by runtime (minutes):", min_runtime, max_runtime, (min_runtime, max_runtime))

all_services = sorted({s.strip() for sublist in movies["streaming_services"].str.split(",") for s in sublist if s.strip()})
selected_services = st.sidebar.multiselect("Filter by streaming service:", all_services)

filtered_movies = movies.copy()
if search:
    filtered_movies = filtered_movies[filtered_movies["title"].str.contains(search, case=False)]
if selected_genre != "All":
    filtered_movies = filtered_movies[filtered_movies["genres"].str.contains(selected_genre)]
filtered_movies = filtered_movies[
    (filtered_movies["runtime"] >= selected_runtime[0]) & (filtered_movies["runtime"] <= selected_runtime[1])
]
if selected_services:
    def has_service(row):
        services = [s.strip() for s in row.split(",")]
        return any(s in services for s in selected_services)
    filtered_movies = filtered_movies[filtered_movies["streaming_services"].apply(has_service)]

selected_movie = st.sidebar.selectbox("Choose a movie:", filtered_movies["title"].values)
num_recs = st.sidebar.slider("Number of recommendations:", 1, 9, 6)


def toggle_fav(title):
    if title in st.session_state.favorites:
        st.session_state.favorites.remove(title)
    else:
        st.session_state.favorites.add(title)

if selected_movie:
    if st.sidebar.button("Remove from Favorites" if selected_movie in st.session_state.favorites else "Add to Favorites"):
        toggle_fav(selected_movie)

st.sidebar.markdown("---")
st.sidebar.header("❤️ My Favorites")
if st.session_state.favorites:
    for fav in st.session_state.favorites:
        st.sidebar.write(f"- {fav}")
else:
    st.sidebar.write("-")


if st.sidebar.button("About This Project"):
    st.sidebar.markdown("""
        <h2>About Neon Red Cinema Movie Recommender</h2>
        <p>This is a Streamlit app built by Ammar for movie recommendations based on genre similarity.</p>
        <p>Features:</p>
        <ul>
            <li>Search and filter movies by genre, runtime, streaming services.</li>
            <li>Add/remove movies to your favorites.</li>
            <li>Neon glowing UI style with dark and light modes.</li>
        </ul>
        <p>© 2025 Ammar</p>
    """, unsafe_allow_html=True)


dark_css = """
body {
    background-color: #1a0000;
    color: #ff3333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.title-glow {
    font-size: 3em;
    font-weight: 900;
    color: #ff0000;
    text-align: center;
    text-shadow:
        0 0 5px #ff0000,
        0 0 10px #ff0000,
        0 0 20px #ff0000,
        0 0 40px #ff0000,
        0 0 80px #ff0000;
    margin-bottom: 5px;
}
.subtitle {
    text-align: center;
    font-size: 1.2em;
    color: #ff6666aa;
    margin-bottom: 30px;
}
.movie-card {
    background: #330000;
    border-radius: 15px;
    box-shadow:
        0 0 5px #ff0000,
        0 0 10px #ff0000,
        0 0 20px #ff0000,
        0 0 40px #ff0000;
    margin-bottom: 25px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    overflow: hidden;
}
.movie-card:hover {
    transform: scale(1.05);
    box-shadow:
        0 0 10px #ff0000,
        0 0 20px #ff0000,
        0 0 40px #ff0000,
        0 0 80px #ff0000;
}
.movie-info {
    padding: 10px;
    text-align: center;
    color: #ff6666;
}
.movie-title {
    font-weight: 700;
    font-size: 1.2em;
    margin-bottom: 5px;
    color: #ff4c4c;
}
.movie-genres {
    font-style: italic;
    font-size: 0.9em;
    color: #ff9999cc;
    margin-bottom: 8px;
}
.movie-rating {
    font-weight: 600;
    color: #ff6666;
}
a {
    color: inherit;
    text-decoration: none;
}
h1, h3, h4 {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
"""

light_css = """
body {
    background-color: #fff0f0;
    color: #b30000;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.title-glow {
    font-size: 3em;
    font-weight: 900;
    color: #b30000;
    text-align: center;
    text-shadow:
        0 0 3px #b30000,
        0 0 6px #b30000,
        0 0 12px #b30000,
        0 0 24px #b30000;
    margin-bottom: 5px;
}
.subtitle {
    text-align: center;
    font-size: 1.2em;
    color: #cc6666aa;
    margin-bottom: 30px;
}
.movie-card {
    background: #ffe6e6;
    border-radius: 15px;
    box-shadow:
        0 0 3px #b30000,
        0 0 6px #b30000,
        0 0 12px #b30000,
        0 0 24px #b30000;
    margin-bottom: 25px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    overflow: hidden;
}
.movie-card:hover {
    transform: scale(1.05);
    box-shadow:
        0 0 6px #b30000,
        0 0 12px #b30000,
        0 0 24px #b30000,
        0 0 48px #b30000;
}
.movie-info {
    padding: 10px;
    text-align: center;
    color: #b30000;
}
.movie-title {
    font-weight: 700;
    font-size: 1.2em;
    margin-bottom: 5px;
    color: #990000;
}
.movie-genres {
    font-style: italic;
    font-size: 0.9em;
    color: #cc6666cc;
    margin-bottom: 8px;
}
.movie-rating {
    font-weight: 600;
    color: #b30000;
}
a {
    color: inherit;
    text-decoration: none;
}
h1, h3, h4 {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
"""

css = dark_css if st.session_state.dark_mode else light_css
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


st.markdown("<h1 class='title-glow'>🎬 Neon Red Cinema Movie Recommender</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your personal IMDB-style movie recommendation system</div>", unsafe_allow_html=True)
st.write("")


if st.button("Recommend Movies"):
    recommendations = recommend(selected_movie, num_recs)
    if recommendations:
        st.markdown(f"<h3 style='text-align:center; color:#ff4c4c;'>Top {num_recs} movies similar to <b>{selected_movie}</b>:</h3>", unsafe_allow_html=True)
        cols_per_row = 3
        rows = (len(recommendations) + cols_per_row - 1) // cols_per_row
        idx = 0
        for _ in range(rows):
            cols = st.columns(cols_per_row)
            for col in cols:
                if idx < len(recommendations):
                    movie = recommendations[idx]
                    with col:
                        st.markdown(f"""
                        <div class="movie-card">
                            <a href="{movie['imdb_url']}" target="_blank" rel="noopener noreferrer">
                                <img src="{movie['poster_url']}" alt="{movie['title']} poster" style="width:100%; border-radius:15px;">
                            </a>
                            <div class="movie-info">
                                <div class="movie-title">{movie['title']}</div>
                                <div class="movie-genres">{movie['genres']}</div>
                                <div class="movie-rating">⭐ {movie['rating']}</div>
                                <div>Runtime: {movie['runtime']} min</div>
                                <div>Streaming: {movie['streaming_services'] or 'N/A'}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    idx += 1
    else:
        st.warning("No recommendations found 😢")


footer_color = "#b30000" if not st.session_state.dark_mode else "#ff4c4c"
st.markdown("---")
st.markdown(f"<p style='text-align:center; color:{footer_color};'>© 2025 Developed by Ammar | Neon Red Cinema ML App 🤖</p>", unsafe_allow_html=True)
