from enum import Enum
from jikanpy import Jikan
from ratelimit import limits, sleep_and_retry

jikan = Jikan()
checked_shows = {}
nobuhiko_okamoto_id = 270

class Position(Enum):
  IS_IN_SHOW = 1
  IS_IN_RELATED_SHOW = 2
  IS_NOT_IN_SHOW = 3

@sleep_and_retry
@limits(calls=1, period=3) # limit API to one call every 2 second
def get_anime(anime_id, **kwargs):
  passed_extension = kwargs.get('extension', None)
  return jikan.anime(anime_id, extension=passed_extension)

@sleep_and_retry
@limits(calls=1, period=3)
def get_person(person_id):
  return jikan.person(person_id)

def is_okamoto_in_anime(anime_id):
  if str(anime_id) in checked_shows.keys():
    return checked_shows[str(anime_id)]

  anime = get_anime(anime_id, extension='characters_staff')
  for c in anime['characters']:
    for va in c['voice_actors']:
      if va['mal_id'] == 270:
        checked_shows[str(anime_id)] = Position.IS_IN_SHOW, c['name']
        return Position.IS_IN_SHOW
      else:
        checked_shows[str(anime_id)] = Position.IS_NOT_IN_SHOW

  return Position.IS_NOT_IN_SHOW

def is_anime_related(anime_id):
  initial_result = is_okamoto_in_anime(anime_id)
  if initial_result == Position.IS_IN_SHOW:
    return Position.IS_IN_SHOW

  voice_actors = []
  anime = get_anime(anime_id, extension='characters_staff')
  for c in anime['characters']:
    for va in c['voice_actors']:
      if va['language'] == 'Japanese':
        voice_actors.append(va)

  for va in voice_actors:
    person = get_person(int(va['mal_id']))
    va_roles = person['voice_acting_roles']
    for role in va_roles:
      if is_okamoto_in_anime(role['anime']['mal_id']) == Position.IS_IN_SHOW:
        checked_shows[str(anime_id)] = Position.IS_IN_RELATED_SHOW, person['name'], role['anime']['name']
        return Position.IS_IN_RELATED_SHOW
      else:
        checked_shows[str(anime_id)] = Position.IS_NOT_IN_SHOW
  
  return Position.IS_NOT_IN_SHOW

def degrees_of_okamoto(anime_id):
  dummy = is_anime_related(anime_id)
  anime_name = get_anime(anime_id)['title']

  if dummy == Position.IS_IN_SHOW:
    print("Nobuhiko Okamoto is in \"" + anime_name + "\", and he plays \"" + checked_shows[str(anime_id)][1] + "\".")
  elif dummy == Position.IS_IN_RELATED_SHOW:
    print("Nobuhiko Okamoto worked with \"" + checked_shows[str(anime_id)][1] + "\" (from \"" + anime_name + "\") on \"" + checked_shows[str(anime_id)][2] + "\".")
  else:
    print("Nobuhiko Okamoto is more than one degree of separation from \"" + anime_name + "\". I know, shocking!") 

if __name__ == "__main__":
  x_3b3 = {"Blue Exorcist": 9919, "Your Name": 32281, "BnHA Season 3": 36456, "Madoka Magica": 9756, "Gekkan Shoujo": 23289, "Cells at Work": 37141, "Dantalian no Shoka": 8915, "Free!": 18507, "Gakuen Babysitters": 35222}
  n_3b3 = {"Dumbbell": 39026, "Eizouken": 39792, "Higashi no Eden": 5630, "Kaguya-sama": 37999, "Kono Suba": 30831, "Evangelion": 30, "Re:Zero": 31240, "Gurren Lagann": 2001, "Usagi Drop": 10162}
  
  for show in n_3b3.values():
    degrees_of_okamoto(show)