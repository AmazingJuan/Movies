from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse
from .models import Movie
from openai import OpenAI
import numpy as np
import os
from dotenv import load_dotenv

#nuevos imports de el workshop 2 

import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64


def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerms':searchTerm, 'movies': movies} )

def about(request):
    return render(request, 'about.html')

def statistics_view(request):
    matplotlib.use('Agg')
    all_movies = Movie.objects.all()

    # Crear un diccionario para almacenar la cantidad de películas por año
    movies_counts_by_year = {}
    movies_counts_by_genre = {}
    # Contar la cantidad de películas por año
    for movie in all_movies:
        year = movie.year if movie.year else 'None'
        genre = movie.genre.split(',')[0] if movie.genre else 'None'

        if year in movies_counts_by_year:
            movies_counts_by_year[year] += 1
        else:
            movies_counts_by_year[year] = 1

        if genre in movies_counts_by_genre:
            movies_counts_by_genre[genre] += 1
        else:
            movies_counts_by_genre[genre] = 1

    # Configurar las posiciones y anchos de las barras
    bar_width = 0.5
    bar_positions = range(len(movies_counts_by_year))
    bar_positions2 = range(len(movies_counts_by_genre))
    # Crear la gráfica de barras
    plt.bar(bar_positions, movies_counts_by_year.values(), width=bar_width, align='center')

    # Personalizar la gráfica
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Movie number')
    plt.xticks(bar_positions, movies_counts_by_year.keys(), rotation=90)

    # Ajustar el espacio en la parte inferior
    plt.subplots_adjust(bottom=0.3)

    # Guardar la gráfica en un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()
    
    # Convertir la imagen a base64
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')

    # Crear la gráfica de barras
    plt.bar(bar_positions2, movies_counts_by_genre.values(), width=bar_width, align='center')

    # Personalizar la gráfica
    plt.title('Movies per genre')
    plt.xlabel('Genre')
    plt.ylabel('Movie number')
    plt.xticks(bar_positions2, movies_counts_by_genre.keys(), rotation=90)

    # Ajustar el espacio en la parte inferior
    plt.subplots_adjust(bottom=0.3)

    # Guardar la gráfica en un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.clf()

    image_png = buffer.getvalue()
    buffer.close()
    graphic2 = base64.b64encode(image_png).decode('utf-8')


    # Renderizar la plantilla con la gráfica
    return render(request, 'statistics.html', {'graphic': graphic, 'graphic2':graphic2})

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email':email})




def recommendation(request):
    searchTerm = request.GET.get('searchMovie')
    best_movie = None
    if(searchTerm):
        # Cargar la API Key
        load_dotenv('api_key.env')
        client = OpenAI(api_key=os.environ.get('openai_api_key'))


        # Función para calcular similitud de coseno
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # Recibir el prompt del usuario (esto se debe recibir desde el formulario de la app)
        prompt = searchTerm

        # Generar embedding del prompt
        response = client.embeddings.create(
            input=[prompt],
            model="text-embedding-3-small"
        )
        prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)

        # Recorrer la base de datos y comparar
        max_similarity = -1

        for movie in Movie.objects.all():
            movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
            similarity = cosine_similarity(prompt_emb, movie_emb)

            if similarity > max_similarity:
                max_similarity = similarity
                best_movie = movie
    return render(request, 'recommendation.html', {'recommended_movie':best_movie})