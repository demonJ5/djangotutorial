from recommender.forms import SearchForm, CuratorForm
from django.shortcuts import render
from django.http import Http404, JsonResponse
from .models import *
from .forms import *
from django.views.decorators.http import require_POST, require_GET
from django.db.models import F, Func
import numpy as np

# Container for track features
class TrackFeatures:
    acousticness = 0
    danceability = 0
    energy = 0
    instrumentalness = 0
    key = 0
    liveness = 0
    loudness = 0
    mode = 0
    speechiness = 0
    tempo = 0
    valence = 0

    # Required to allow initialization of the feature class with only one
    # expression. (As in ORM queries)
    def set_features(self, p_acou, p_danc, p_en, p_inst, p_key, p_live,
                     p_loud, p_mode, p_spee, p_temp, p_vale):
        self.acousticness = p_acou
        self.danceability = p_danc
        self.energy = p_en
        self.instrumentalness = p_inst
        self.key = p_key
        self.liveness = p_live
        self.loudness = p_loud
        self.mode = p_mode
        self.speechiness = p_spee
        self.tempo = p_temp
        self.valence = p_vale
        return self
        

# Container for weighted average config
# 
# Weights affect each feature's importance in the average. These change with
# user configuration and are relative. IE: If all weights are 1, it is identical
# to all weights being 10.
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
    # Normalization multipliers determined internally based on database averages
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

    def weight_sum(self):
        return (self.acousticness_weight + self.danceability_weight
                + self.energy_weight + self.instrumentalness_weight + self.key_weight
                + self.liveness_weight + self.loudness_weight + self.mode_weight
                + self.speechiness_weight + self.tempo_weight + self.valence_weight)

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
    valence_mult = p_cfg.valence_weight/total_weight
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
        from_year = None if form.cleaned_data['from_year'] == None else \
                int(form.cleaned_data['from_year'])
        to_year = None if form.cleaned_data['to_year'] == None else \
                int(form.cleaned_data['to_year'])
        albums = find_albums(
                form.cleaned_data['artist'],
                from_year,
                to_year
            )
            
        # Random 3 of top 10 popular albums
        albums = list(np.random.permutation(albums[:10]))[:3] 
        return render(request, 'recommender/searchform.html', {'form': form, 
                'albums': albums })
    else:
        raise Http404('Something went wrong')


@require_GET
def searchform_get(request):
    form = SearchForm()
    return render(request, 'recommender/searchform.html', {'form': form})

@require_POST
def curator_post(request):
    form = CuratorForm(request.POST)
    if form.is_valid():
        # Retrieve user input
        in_title = form.cleaned_data['id_title']
        in_w_acous = form.cleaned_data['id_acousticness_weight']
        in_w_dance = form.cleaned_data['id_danceability_weight']
        in_w_energ = form.cleaned_data['id_energy_weight']
        in_w_instr = form.cleaned_data['id_instrumentalness_weight']
        in_w_key   = form.cleaned_data['id_key_weight']
        in_w_liven = form.cleaned_data['id_liveness_weight']
        in_w_loudn = form.cleaned_data['id_loudness_weight']
        in_w_mode  = form.cleaned_data['id_mode_weight']
        in_w_speec = form.cleaned_data['id_speechiness_weight']
        in_w_tempo = form.cleaned_data['id_tempo_weight']
        in_w_valen = form.cleaned_data['id_valence_weight']
        # Debug printout #
        # print('Found title %s and weights %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f' \
        #        % (in_title, in_w_acous, in_w_dance, in_w_energ, 
        #        in_w_instr, in_w_key, in_w_liven, in_w_loudn, in_w_mode, 
        #        in_w_speec, in_w_tempo, in_w_valen))

        # Establish config for weights in weight_cfg
        weight_cfg = WeightedAvgCfg()
        weight_cfg.acousticness_weight = in_w_acous
        weight_cfg.danceability_weight = in_w_dance
        weight_cfg.energy_weight = in_w_energ
        weight_cfg.instrumentalness_weight = in_w_instr
        weight_cfg.key_weight = in_w_key  
        weight_cfg.liveness_weight = in_w_liven
        weight_cfg.loudness_weight = in_w_loudn
        weight_cfg.mode_weight = in_w_mode 
        weight_cfg.speechiness_weight = in_w_speec
        weight_cfg.tempo_weight = in_w_tempo
        weight_cfg.valence_weight = in_w_valen
        # Find the ID and features of the reference track in ref_title_id
        # and ref_title_features
        ref_query = Musicdata.objects.filter(name__icontains = in_title)\
                .values()[:1]
        ref_song = ref_query[0]
        ref_title_id = ref_song['id']
        ref_title_features = TrackFeatures()
        ref_title_features.acousticness = ref_song['acousticness']
        ref_title_features.danceability = ref_song['danceability']
        ref_title_features.energy = ref_song['energy']
        ref_title_features.instrumentalness = ref_song['instrumentalness']
        ref_title_features.key = ref_song['key']
        ref_title_features.liveness = ref_song['liveness']
        ref_title_features.loudness = ref_song['loudness']
        ref_title_features.mode = ref_song['mode']
        ref_title_features.speechiness = ref_song['speechiness']
        ref_title_features.tempo = ref_song['tempo']
        ref_title_features.valence = ref_song['valence']
        # Debug printout #
        # print('Divined reference song\'s ID %s' % ref_title_id)

        # Compute the gestalt value for the reference track and generate
        # query sorted by the difference between the reference gestalt and
        # other tracks' gestalts
        ref_gestalt = calc_gestalt(ref_title_features, weight_cfg)
        # Debug printout #
        # print('Reference gestalt is %f' % ref_gestalt)
        track_query = Musicdata.objects.exclude(id = ref_title_id)
        # Annotate each entry with calculated gestalt values according to our
        # user-defined weights
        annotated_query = track_query.annotate(gestalt = calc_gestalt(
                TrackFeatures().set_features(F('acousticness'), 
                F('danceability'), F('energy'), F('instrumentalness'), F('key'),
                F('liveness'), F('loudness'), F('mode'), F('speechiness'), 
                F('tempo'), F('valence')), weight_cfg)) 
        # Find the absolute difference between our reference song's gestalt and
        # all other songs
        annotated_diffs = annotated_query.annotate(gestalt_diff = Func(
                ref_gestalt - F('gestalt'), function='ABS'))
        # Find the smallest three differences; the most similar tracks
        annotated_ordered_ids = annotated_diffs.order_by('gestalt_diff')\
                .values('id', 'name', 'gestalt')[:3]
        tracks = list(annotated_ordered_ids)

        # Debug printout #
        # print('Final curation list')
        # print(tracks)
        return render(request, 'recommender/curatorpage.html', {'form': form,
                'tracks': tracks, 'ref_song': ref_song })
    else:
        raise Http404('Something went wrong in fetching the curation')

@require_GET
def curator_get(request):
    form = CuratorForm()
    return render(request, 'recommender/curatorpage.html', {'form': form})
