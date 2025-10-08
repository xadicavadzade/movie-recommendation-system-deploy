# simple_app.py - Film Rating (Sadə və Aydın Struktur)

from flask import Flask, render_template_string, request, jsonify
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session'

# Model və veriləri yüklə
print("Yüklənir...")
with open('movie_rating_model.pkl', 'rb') as f:
    model = pickle.load(f)

movies_df = pd.read_csv('movies_for_web.csv')
ratings_df = pd.read_csv('ratings.csv')

# Ən populyar filmləri tap (test üçün)
popular_movies = (
    ratings_df.groupby('movieId')
    .size()
    .sort_values(ascending=False)
    .head(10)
    .index.tolist()
)

# Username database
users_database = {}  # {username: {'userId': id, 'ratings': {movieId: rating}}}
next_user_id = int(ratings_df['userId'].max()) + 1

print(f"✓ {len(movies_df)} film mövcuddur")
print(f"✓ Başlanğıc user ID: {next_user_id}")

# HTML Template
HTML_PAGE = '''
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Film Reytinq Təxmini 🎥</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 650px;
            width: 100%;
            padding: 40px;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2em;
        }
        
        .section {
            display: none;
        }
        
        .section.active {
            display: block;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
        }
        
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
            transition: all 0.3s;
        }
        
        button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .secondary-btn {
            background: #6c757d;
            margin-top: 10px;
        }
        
        .secondary-btn:hover {
            background: #5a6268;
        }
        
        .movie-rating {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            transition: all 0.3s;
        }
        
        .movie-rating:hover {
            background: #e3f2fd;
            transform: scale(1.01);
        }
        
        .movie-rating label {
            flex: 1;
            margin: 0;
            font-size: 14px;
            color: #333;
        }
        
        .stars-container {
            display: flex;
            gap: 5px;
        }
        
        .star {
            font-size: 20px;
            color: #ddd;
            cursor: pointer;
            transition: color 0.2s;
        }
        
        .star.filled {
            color: #ffd700;
        }
        
        .result {
            margin-top: 25px;
            padding: 25px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 15px;
            color: white;
            text-align: center;
            animation: bounceIn 0.5s ease;
        }
        
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .result h2 {
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: #1565c0;
            font-size: 14px;
            border-left: 5px solid #2196f3;
        }
        
        .welcome-msg {
            background: #fff3e0;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            color: #ef6c00;
            font-weight: bold;
        }
        
        .favorites {
            margin-top: 15px;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            text-align: left;
        }
        
        .favorites h3 {
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        
        .favorite-movie {
            margin: 5px 0;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Film Reytinq Təxmini 🎥⭐</h1>
        
        <!-- 1. GİRİŞ / QEYDİYYAT -->
        <div id="loginSection" class="section active">
            <div class="info-box">
                İstifadəçi adınızı daxil edin. Yeni adsınızsa qeydiyyatdan keçəcəyik! 🚀
            </div>
            
            <div class="input-group">
                <label>İstifadəçi Adınız:</label>
                <input type="text" id="username" placeholder="Məsələn: ali_2024">
            </div>
            
            <button onclick="login()">Davam Et 🔑</button>
        </div>
        
        <!-- 2. REYTİNQ TESTİ (Yeni istifadəçilər üçün) -->
        <div id="ratingTestSection" class="section">
            <div class="welcome-msg" id="welcomeMsg"></div>
            <div class="info-box">
                10 populyar filmə reytinq verin (⭐ 0.5-5 arası). Ən azı 3 film seçin! 😊
            </div>
            
            <div id="ratingsList"></div>
            
            <button onclick="completeTest()">Testi Tamamla 🎉</button>
            <button class="secondary-btn" onclick="logout()">Geri 🔙</button>
        </div>
        
        <!-- 3. TƏXMİN PANEL (Qeydiyyatlı istifadəçilər üçün) -->
        <div id="predictSection" class="section">
            <div class="welcome-msg" id="predictWelcome"></div>
            
            <div class="input-group">
                <label>Film seçin:</label>
                <select id="movieSelect"></select>
            </div>
            
            <button onclick="makePrediction()">Təxmin Et! ⭐</button>
            <button class="secondary-btn" onclick="logout()">Çıxış 🚪</button>
            
            <div id="resultBox" style="display: none;"></div>
        </div>
    </div>
    
    <script>
        let allMovies = [];
        let popularMovies = [];
        let currentUsername = null;
        let currentUserId = null;
        let testRatings = {};
        
        // Səhifə yükləndikdə
        window.addEventListener('DOMContentLoaded', async () => {
            // Bütün filmləri yüklə
            const response = await fetch('/api/movies');
            allMovies = await response.json();
            
            const select = document.getElementById('movieSelect');
            select.innerHTML = allMovies.map(m => 
                `<option value="${m.movieId}">${m.title}</option>`
            ).join('');
            
            // Populyar filmləri yüklə
            const popResponse = await fetch('/api/popular-movies');
            popularMovies = await popResponse.json();
            
            renderRatingInputs();
        });
        
        // Rating inputları yarat
        function renderRatingInputs() {
            const container = document.getElementById('ratingsList');
            container.innerHTML = popularMovies.map(movie => {
                const movieId = movie.movieId;
                return `
                    <div class="movie-rating">
                        <label>${movie.title} 🎞️</label>
                        <div class="stars-container" data-movie-id="${movieId}">
                            ${[0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5].map(rating => 
                                `<i class="fas fa-star star" data-rating="${rating}" onclick="setRating(${movieId}, ${rating})"></i>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        // Star rating set et
        function setRating(movieId, rating) {
            testRatings[movieId] = rating;
            const container = document.querySelector(`[data-movie-id="${movieId}"]`);
            container.querySelectorAll('.star').forEach((star) => {
                const starRating = parseFloat(star.dataset.rating);
                if (starRating <= rating) {
                    star.classList.add('filled');
                } else {
                    star.classList.remove('filled');
                }
            });
        }
        
        // Giriş
        async function login() {
            const username = document.getElementById('username').value.trim();
            if (!username) {
                alert('İstifadəçi adınızı daxil edin! 😊');
                return;
            }
            
            const response = await fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username.toLowerCase()})
            });
            
            const data = await response.json();
            currentUsername = data.username;
            currentUserId = data.userId;
            
            if (data.isNew) {
                // Yeni istifadəçi - Rating testinə göndər
                document.getElementById('welcomeMsg').innerHTML = 
                    `Xoş gəldin, ${username}! 🎉<br>Sən yeni istifadəçisən. Gəl filmlərə reytinq verək!`;
                
                showSection('ratingTestSection');
                testRatings = {};
                document.querySelectorAll('.star').forEach(s => s.classList.remove('filled'));
            } else {
                // Köhnə istifadəçi - Predict panelinə göndər
                document.getElementById('predictWelcome').innerHTML = 
                    `Yenidən xoş gəldin, ${username}! 🎉`;
                
                showSection('predictSection');
            }
        }
        
        // Rating testini tamamla
        async function completeTest() {
            const ratingsCount = Object.keys(testRatings).length;
            if (ratingsCount < 3) {
                alert('Ən azı 3 filmə reytinq verin! 😊');
                return;
            }
            
            const response = await fetch('/complete-test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: currentUsername,
                    userId: currentUserId,
                    ratings: testRatings
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Test tamamlandı! İndi film təxminləri ala bilərsiniz! 🎉');
                document.getElementById('predictWelcome').innerHTML = 
                    `Xoş gəldin, ${currentUsername}! 🎉`;
                showSection('predictSection');
            }
        }
        
        // Təxmin et
        async function makePrediction() {
            const movieId = document.getElementById('movieSelect').value;
            
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: currentUsername,
                    movieId: parseInt(movieId)
                })
            });
            
            const data = await response.json();
            
            // Nəticəni göstər
            const resultBox = document.getElementById('resultBox');
            resultBox.innerHTML = `
                <div class="result">
                    <h2>${data.predicted_rating.toFixed(2)} ⭐</h2>
                    <p>${data.movie_title}</p>
                    ${data.user_favorites && data.user_favorites.length > 0 ? `
                        <div class="favorites">
                            <h3>Sizin Favoritləriniz 🎉</h3>
                            ${data.user_favorites.map(f => 
                                `<div class="favorite-movie">⭐ ${f.title} (${f.rating})</div>`
                            ).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
            resultBox.style.display = 'block';
        }
        
        // Çıxış
        function logout() {
            currentUsername = null;
            currentUserId = null;
            testRatings = {};
            document.getElementById('username').value = '';
            document.getElementById('resultBox').style.display = 'none';
            showSection('loginSection');
        }
        
        // Section göstər
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(sectionId).classList.add('active');
        }
    </script>
</body>
</html>
'''

# API Routes
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/movies')
def get_movies():
    movies_list = movies_df[['movieId', 'title']].to_dict('records')
    return jsonify(movies_list)

@app.route('/api/popular-movies')
def get_popular_movies():
    popular_movies_data = movies_df[movies_df['movieId'].isin(popular_movies)][['movieId', 'title']]
    return jsonify(popular_movies_data.to_dict('records'))

@app.route('/login', methods=['POST'])
def login():
    global next_user_id
    data = request.json
    username = data.get('username').strip().lower()
    
    if username in users_database:
        # Mövcud istifadəçi
        user_data = users_database[username]
        print(f"✓ Mövcud istifadəçi: {username} (ID: {user_data['userId']})")
        return jsonify({
            'isNew': False,
            'userId': user_data['userId'],
            'username': username
        })
    else:
        # Yeni istifadəçi - ID yarat
        user_id = next_user_id
        users_database[username] = {
            'userId': user_id,
            'ratings': {}
        }
        next_user_id += 1
        
        print(f"✓ Yeni istifadəçi yaradıldı: {username} (ID: {user_id})")
        return jsonify({
            'isNew': True,
            'userId': user_id,
            'username': username
        })

@app.route('/complete-test', methods=['POST'])
def complete_test():
    global ratings_df
    
    data = request.json
    username = data.get('username').strip().lower()
    user_id = data.get('userId')
    ratings = data.get('ratings')
    
    # Database-ə əlavə et
    users_database[username]['ratings'] = {int(k): float(v) for k, v in ratings.items()}
    
    # ratings_df-ə əlavə et (model üçün)
    for movie_id, rating in ratings.items():
        new_row = pd.DataFrame([{
            'userId': user_id,
            'movieId': int(movie_id),
            'rating': float(rating),
            'timestamp': 0
        }])
        ratings_df = pd.concat([ratings_df, new_row], ignore_index=True)
    
    print(f"✓ Test tamamlandı: {username}, {len(ratings)} rating əlavə edildi")
    
    return jsonify({'success': True})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    username = data.get('username').strip().lower()
    movie_id = data.get('movieId')
    
    if username not in users_database:
        return jsonify({'error': 'İstifadəçi tapılmadı'}), 404
    
    user_data = users_database[username]
    user_id = user_data['userId']
    
    # Təxmin
    predicted_rating = model.predict([[user_id, movie_id]])[0]
    movie_title = movies_df[movies_df['movieId'] == movie_id]['title'].values[0]
    
    # Favoritləri tap
    favorites = []
    user_ratings = user_data['ratings']
    
    if user_ratings:
        sorted_ratings = sorted(user_ratings.items(), key=lambda x: x[1], reverse=True)[:5]
        for mid, rating in sorted_ratings:
            title = movies_df[movies_df['movieId'] == mid]['title'].values[0]
            favorites.append({
                'title': title,
                'rating': rating
            })
    
    print(f"✓ Təxmin: {username} → {movie_title} = {predicted_rating:.2f}")
    
    return jsonify({
        'predicted_rating': float(predicted_rating),
        'movie_title': movie_title,
        'user_favorites': favorites
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)