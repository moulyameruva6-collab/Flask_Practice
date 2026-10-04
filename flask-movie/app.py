from flask import Flask,render_template,redirect,request

app = Flask(__name__)
movie_db = {
 "M101": {
 "title": "RRR",
 "director": "S. S. Rajamouli",
 "language": "Telugu",
 "genre": "Action",
 "rating": 8,
 "year": 2022
 },
 "M102": {
 "title": "Pushpa",
 "director": "Sukumar",
 "language": "Telugu",
 "genre": "Action",
 "rating": 7,
 "year": 2021
 },
 "M103": {
 "title": "Jersey",
 "director": "Gowtam Tinnanuri",
 "language": "Telugu",
 "genre": "Drama",
 "rating": 9,
 "year": 2019
 },
 "M104": {
 "title": "Bahubali",
 "director": "S. S. Rajamouli",
 "language": "Telugu",
 "genre": "Action",
 "rating": 9,
 "year": 2015
 },
 "M105": {
 "title": "KGF",
 "director": "Prashanth Neel",
 "language": "Kannada",
 "genre": "Action",
 "rating": 8,
 "year": 2018
 },
 "M106": {
 "title": "3 Idiots",
 "director": "Rajkumar Hirani",
 "language": "Hindi",
 "genre": "Comedy",
 "rating": 9,
 "year": 2009
 }
}

@app.route('/')
def home():
    return render_template("home.html")  
@app.route('/movies')
def get_all_movies():
    return render_template("movies.html", movies=movie_db) 
@app.route("/movies/id=<movie_id>")
def get_movie_details(movie_id):
    if movie_id in movie_db:
        return movie_db[movie_id]
    return "Movie not found"
@app.route("/movies/director=<director_name>")
def get_director_movies(director_name):
    res = []
    for id in movie_db:
        if movie_db[id]["director"]() == director_name():
            res.append(movie_db[id])
    return res if res else "No movies found"
@app.route("/movies/rating=<int:rating>")
def get_rating_movies(rating):
    res = []
    for movie_id in movie_db:
        if movie_db[movie_id]["rating"] == rating:
            res.append(movie_db[movie_id])
    return res if res else "No movies found"
@app.route("/movies/language=<language>")
def get_language_movies(language):
    res = []
    for movie_id in movie_db:
        if movie_db[movie_id]["language"]() == language():
            res.append(movie_db[movie_id])
    return res if res else "No movies found"
@app.route("/movies/genre=<genre>")
def get_genre_movies(genre):
    res = []
    for movie_id in movie_db:
        if movie_db[movie_id]["genre"]() == genre():
            res.append(movie_db[movie_id])
    return res if res else "No movies found"
@app.route("/movies/year=<int:year>")
def get_year_movies(year):
    res = []
    for movie_id in movie_db:
        if movie_db[movie_id]["year"] == year:
            res.append(movie_db[movie_id])
    return res if res else "No movies found for this year"

# movies
@app.route("/movies/language=<language>/genre=<genre>")
def get_language_genre_movies(language, genre):
    res = []
    for movie_id in movie_db:
        if (movie_db[movie_id]["language"]() == language()
                and movie_db[movie_id]["genre"]() == genre()):
            res.append(movie_db[movie_id])
    return res if res else "No movies found"

# add movies
@app.route("/add-movie", methods=['GET', 'POST'])
def add_movie():
    if request.method == 'GET':
        return render_template("add_movie.html")
    if request.method == 'POST':
        movie_id = request.form.get('movie_id')
        title = request.form.get('title')
        director = request.form.get('director')
        language = request.form.get('language')
        genre = request.form.get('genre')
        rating = int(request.form.get('rating'))
        year = int(request.form.get('year'))
        movie_data = {
            "title": title,
            "director": director,
            "language": language,
            "genre": genre,
            "rating": rating,
            "year": year
        }
        movie_db[movie_id] = movie_data
        return redirect('/movies')
    
# search movie
@app.route("/search", methods=["GET", "POST"])
def search_movie():
    movie = None
    searched = False
    if request.method == "POST":
        movie_id = request.form.get("movie_id")
        searched = True
        if movie_id in movie_db:
            movie = movie_db[movie_id]
    return render_template("search.html",movie=movie,searched=searched)

    

# director search
@app.route("/director-search", methods=["GET", "POST"])
def director_search():
    movies = []
    searched = False
    director_name = ""
    if request.method == "POST":
        director_name = request.form.get("director")
        searched = True
        for movie_id, movie in movie_db.items():
            if movie["director"].lower() == director_name.lower():
                movies.append(movie)
    return render_template("director_search.html", movies=movies, director_name=director_name,searched=searched)

# Rating search form - Day 4
@app.route("/rating-search", methods=["GET", "POST"])
def rating_search():

    movies = []
    searched = False
    rating = ""

    if request.method == "POST":
        rating = request.form.get("rating")
        searched = True

        try:
            rating = int(rating)

            for movie_id, movie in movie_db.items():
                if movie["rating"] == rating:
                    movies.append(movie)

        except ValueError:
            return "Rating must be a number"

    return render_template(
        "rating_search.html",
        movies=movies,
        rating=rating,
        searched=searched
    )

#language Search

@app.route("/language-search", methods=["GET", "POST"])
def language_search():
    movies = []
    searched = False
    language = ""

    if request.method == "POST":
        language = request.form.get("language")
        searched = True

        for movie_id, movie in movie_db.items():
            if movie["language"].lower() == language.lower():
                movies.append(movie)

    return render_template(
        "language_search.html",
        movies=movies,
        language=language,
        searched=searched
    )
if __name__ == "__main__":
    app.run(debug=True)