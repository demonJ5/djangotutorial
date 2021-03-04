from recommender.forms import SearchForm, CuratorForm
from django.shortcuts import render
from django.http import Http404, JsonResponse
from .models import *
from .forms import *
from django.views.decorators.http import require_POST, require_GET
import numpy as np

# Container for track features
class TrackFeatures:
    acousticness = 0
    danceability = 0
    duration = 0
    energy = 0
    instrumentalness = 0
    key = 0
    liveness = 0
    loudness = 0
    mode = 0
    speechiness = 0
    tempo = 0
    valence = 0

# Container for weighted average config
# 
# Weights affect each feature's weight in the average. These change with
# user configuration.
#
# Normalizers are multipliers that bring the differing feature types to be
# approximately around the same average. This is done by finding a multiplier
# that brings the average value of that feature to ~100. This is hardly perfect.
class WeightedAvgCfg:
    # Weights
    acousticness_weight = 5
    danceability_weight = 5
    energy_weight = 5
    instrumentalness_weight = 5
    key_weight = 5
    liveness_weight = 5
    loudness_weight = 5
    mode_weight = 5
    speechiness_weight = 5
    tempo_weight = 5
    valence_weight = 5
    # Normalizer
    ACOUSTICNESS_NORMALIZER = 199.237
    DANCEABILITY_NORMALIZER = 186.482
    ENERGY_NORMALIZER = 207.905
    INSTRUMENTALNESS_NORMALIZER = 512.906
    KEY_NORMALIZER = 19.215
    LIVENESS_NORMALIZER = 473.047
    LOUDNESS_NORMALIZER = -8.491
    MODE_NORMALIZER = 142.218
    SPEECHINESS_NORMALIZER = 944.320
    TEMPO_NORMALIZER = 0.855
    VALENCE_NORMALIZER = 190.386

    def weight_sum():
        return (acousticness_weight + danceability_weight
                + energy_weight + instrumentalness_weight + key_weight
                + liveness_weight + loudness_weight + mode_weight
                + speechiness_weight + tempo_weight + valence_weight)

# Calculate the gestalt values using the provided configuration
# Gestalt is calculated as sum[feature * feature_normalizer * (feature_weight / 
# total_weight)]
def calc_gestalt(p_features, p_cfg):
    # Find weight values
    total_weight = p_cfg.weight_sum()
    acousticness_mult = p_cfg.acousticness_weight/total_weight
    danceability_mult = p_cfg.danceability_weight/total_weight
    energy_mult = p_cfg.energy_weight/total_weight
    instrumentalness_mult = p_cfg.instrumentalness_weight/total_weight
    key_mult = p_cfg.key_weight/total_weight
    liveness_mult = p_cfg.liveness_weight/total_weight
    loudness_mult = p_cfg.loudness_weight/total_weight
    mode_mult = p_cfg.mode_weight/total_weight
    speechiness_mult = p_cfg.speechiness_weight/total_weight
    tempo_mult = p_cfg.tempo_weight/total_weight
    valence_mult = p_cfg.valence_mult/total_weight
    # Calculate gestalt
    acousticness_factor = (p_features.acousticness * acousticness_mult
                            * p_cfg.ACOUSTICNESS_NORMALIZER)
    danceability_factor = (p_features.danceability * danceability_mult
                            * p_cfg.DANCEABILITY_NORMALIZER)
    energy_factor = (p_features.energy * energy_mult
                            * p_cfg.ENERGY_NORMALIZER)
    instrumentalness_factor = (p_features.instrumentalness
                            * instrumentalness_mult
                            * p_cfg.INSTRUMENTALNESS_NORMALIZER)
    key_factor = (p_features.key * key_mult
                            * p_cfg.KEY_NORMALIZER)
    liveness_factor = (p_features.liveness * liveness_mult
                            * p_cfg.LIVENESS_NORMALIZER)
    loudness_factor = (p_features.loudness * loudness_mult
                            * p_cfg.LOUDNESS_NORMALIZER)
    mode_factor = (p_features.mode * mode_mult
                            * p_cfg.MODE_NORMALIZER)
    speechiness_factor = (p_features.speechiness * speechiness_mult
                            * p_cfg.SPEECHINESS_NORMALIZER)
    tempo_factor = (p_features.tempo * tempo_mult
                            * p_cfg.TEMPO_NORMALIZER)
    valence_factor = (p_features.valence * valence_mult
                            * p_cfg.VALENCE_NORMALIZER)
    return (acousticness_factor + danceability_factor + energy_factor
            + instrumentalness_factor + key_factor + liveness_factor
            + loudness_factor + mode_factor + speechiness_factor
            + tempo_factor + valence_factor)

def find_albums(artist, from_year = None, to_year = None):
    query = Musicdata.objects.filter(artists__contains = artist)
    if from_year is not None:
        query = query.filter(year__gte = from_year)
    if to_year is not None:
        query = query.filter(year__lte = to_year)
    return list(query.order_by('-popularity').values('id','name','year'))
    

@require_POST
def searchform_post(request):
    # create a form instance and populate it with data from the request:
    form = SearchForm(request.POST)
    # check whether it's valid:
    if form.is_valid():
        # process the data in form.cleaned_data as required
        from_year = None if form.cleaned_data['from_year'] == None else int(form.cleaned_data['from_year'])
        to_year = None if form.cleaned_data['to_year'] == None else int(form.cleaned_data['to_year'])
        albums = find_albums(
                form.cleaned_data['artist'],
                from_year,
                to_year
            )
            
        # Random 3 of top 10 popular albums
        albums = list(np.random.permutation(albums[:10]))[:3] 
        return render(request, 'recommender/searchform.html', {'form': form, 'albums': albums })
    else:
        raise Http404('Something went wrong')


@require_GET
def searchform_get(request):
    form = SearchForm()
    return render(request, 'recommender/searchform.html', {'form': form})

@require_POST
def curator_post(request):
    #form = SearchForm(request.POST)
    form = CuratorForm()
    return render(request, 'recommender/curatorpage.html', {'form': form})

@require_GET
def curator_get(request):
    form = CuratorForm()
    return render(request, 'recommender/curatorpage.html', {'form': form})
