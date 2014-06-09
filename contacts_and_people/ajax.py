import json
from dajaxice.decorators import dajaxice_register

@dajaxice_register
def contacts_search(request):
    return json.dumps({})
