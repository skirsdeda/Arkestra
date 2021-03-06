from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
import django.http as http
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from links.link_functions import object_links
from models import Person, Building, Membership, Entity

from django.utils import simplejson
from django.conf import settings

applications = getattr(settings, 'INSTALLED_APPS')

if 'publications' in applications:
    from publications.models import BibliographicRecord
    from publications.models import Researcher # required for publications

def contacts_and_people(request, slug):
    slug = slug or getattr(Entity.objects.base_entity(), "slug", None)
    entity = get_object_or_404(Entity, slug=slug, external_url=None)

    # for the menu, because next we mess up the path
    request.auto_page_url = request.path
    # request.path = entity.get_website.get_absolute_url() # for the menu, so it knows where we are
    request.current_page = entity.get_website
    template = entity.get_template()
    main_page_body_file = "contacts_and_people/entity_contacts_and_people.html"
    # meta values - title and meta
    title = _("Contact information for %s") % entity
    meta = {
        "description": _("Addresses, phone numbers, staff lists and other contact information"),
        }

    people, initials = entity.get_people_and_initials()

    # only show pagetitle if there are people
    if people:
        pagetitle = _("Contacts & people")
    else:
        pagetitle = u""

    # are there Key People to show?
    if entity.get_key_people(): # if so we will show a list of people with key roles, then a list of other people
        people_list_heading = _(u"Also")
        # now remove the Key People from the people list
        people = [ person for person in people if person not in set([role.person for role in entity.get_key_people()])]
    else: # otherwise, just a list of the people with roles
        people_list_heading = _(u"People")
    people = entity.get_roles_for_members(people) # convert the list of Persons into a list of Members
    search_fields = [
        {
            "field_name": "name",
            "field_label": "Name",
            "placeholder": "Surname or first name",
            "search_keys": [
                "given_name__icontains",
                "surname__icontains",
                ],
            },
        {
            "field_name": "role",
            "field_label": "Roles",
            "placeholder": "All roles",
            "search_keys": [
                "member_of__role__icontains",
                ]
            }
        ]
    people_qs = entity.get_people()
    search = False
    for search_field in search_fields:
        field_name = search_field["field_name"]
        if field_name in request.GET:
            query = request.GET[field_name]
            search_field["value"] = query
            if query:
                search = True

            q_object = Q()
            for search_key in search_field["search_keys"]:
                lookup = {search_key: query}
                q_object |= Q(**lookup)
            people_qs = people_qs.distinct().filter(q_object)
    if search:
        people_qs = entity.get_roles_for_members(people_qs)
    return render_to_response(
        "arkestra_utilities/entity_auto_page.html", # this is a catch-all template, that then uses includes to bring in extra information
        {
            "entity":entity,
            "pagetitle": pagetitle,
            "entity.website.template": template,
            "main_page_body_file": main_page_body_file,
            "email": entity.email,
            "title": title,
            "meta": meta,
            "precise_location": entity.precise_location,
            "intro_page_placeholder": entity.contacts_page_intro,
            "phone": entity.phone_contacts.all(),
            "full_address" : entity.get_full_address,
            "building" : entity.get_building,
            "people": people,
            "people_list_heading": people_list_heading,
            "initials_list": initials,
            "search_fields": search_fields,
            "people_qs": people_qs,
            "search": search,
        },
        RequestContext(request),
        )

def people(request, slug=getattr(Entity.objects.base_entity(), "slug", None), letter=None):
    """
    Responsible for lists of people
    """
    # general values needed to set up and construct the page and menus
    slug = slug or getattr(Entity.objects.base_entity(), "slug", None)
    entity = get_object_or_404(Entity, slug=slug, external_url=None)
    # for the menu, because next we mess up the path
    request.auto_page_url = entity.get_auto_page_url("contact-entity")
    # request.path = entity.get_website.get_absolute_url() # for the menu, so it knows where we are
    request.current_page = entity.get_website
    template = entity.get_template()
    main_page_body_file = "includes/people_list_with_index.html"
    # meta values - title and meta
    meta = {
        u"description": _("People in %s") % entity,
        }
    title = _("%s: people") % entity
    # content values
    people, initials = entity.get_people_and_initials()
    if letter:
        people = entity.get_people(letter)
        title = _(("%s, people by surname: %s")) % (entity, letter.upper())
    return render_to_response(
        "arkestra_utilities/entity_auto_page.html",
        {
            "entity":entity,
            "pagetitle": entity,
            "entity.website.template": template,
            "main_page_body_file": main_page_body_file,

            "title": title,
            "meta": meta,

            "people": people,
            "initials_list": initials,
            "letter": letter,
        },
        RequestContext(request),
    )

def people_search(request):
    """
    People search accross all entities (uses ajax_people_search view)
    """
    entity = Entity.objects.base_entity()
    # for the menu, because next we mess up the path
    #request.auto_page_url = entity.get_auto_page_url("contact-entity")
    # request.path = entity.get_website.get_absolute_url() # for the menu, so it knows where we are
    request.current_page = entity.get_website
    template = entity.get_template()
    main_page_body_file = "includes/people_search.html"
    # meta values - title and meta
    meta = {
        u"description": _("Contact search"),
        }
    title = _("Contact search")
    # content values
    # --

    return render_to_response(
        "arkestra_utilities/entity_auto_page.html",
        {
            "entity":entity,
            "pagetitle": entity,
            "entity.website.template": template,
            "main_page_body_file": main_page_body_file,

            "title": title,
            "meta": meta,

        },
        RequestContext(request),
    )
    
def publications(request, slug):
    entity = Entity.objects.get(slug=slug)
    request.current_page = entity.website
    return render_to_response(
        "contacts_and_people/publications.html",
        {"entity":entity,},
        RequestContext(request),
    )


def person(request, slug, active_tab=""):
    """
    Responsible for the person pages
    """
    person = get_object_or_404(Person, slug=slug, active=True)
    person.links = object_links(person)
    # we have a home_role, but we should also provide a role, even where it's good enough to give us an address
    home_role = person.get_role
    if home_role:
        entity = home_role.entity
    entity = person.get_entity # don't rely on home_role.entity - could be None or overridden

    building = person.get_building

    contact = person.get_please_contact()
    email = contact.email
    phone = contact.phone_contacts.all()

    if person.please_contact:
        precise_location = None
    else:
        precise_location = person.precise_location
    access_note = person.access_note

    if home_role:
        description = ", ".join((home_role.__unicode__(), entity.__unicode__()))
        request.current_page = entity.get_website
    else:
        description = Entity.objects.base_entity().__unicode__()
        request.current_page = Entity.objects.base_entity().get_website

    meta = {
        "description": ": ".join((person.__unicode__(), description))
    }

    if entity:
        template = entity.get_template()
    else: # no memberships, no useful information
        template = Entity.objects.base_entity().get_template()

    tabs_dict = { # information for each kind of person tab
        "default": {
            "tab": "contact",
            "title": "Contact information",
            "address": "",
            "meta_description_content": person,
        },
        "research": {
            "tab": "research",
            "title": "Research",
            "address": "research",
            "meta_description_content": unicode(person) + " - research interests",
        },
        "publications": {
            "tab": "publications",
            "title": "Publications",
            "address": "publications",
            "meta_description_content": unicode(person) + " - publications",
        },
    }

    # mark the active tab, if there is one
    if active_tab:
        try:
            tabs_dict[active_tab]["active"] = True
        except KeyError:
            raise http.Http404

    # add tabs to the list of tabs
    tabs = []
    tabs.append(tabs_dict["default"])

    if 'publications' in applications:
        try:
            if person.researcher and person.researcher.publishes:
                tabs.append(tabs_dict["research"])
                tabs.append(tabs_dict["publications"])
        except Researcher.DoesNotExist:
            pass

    # were there any tabs created?
    if tabs:
        if not active_tab:
            # find out what to add to the url for this tab
            active_tab=tabs[0]["address"]
            # mark the tab as active for the template
            tabs[0]["active"]=True
        # fewer than 2? not worth having tabs!
        if len(tabs)==1:
            tabs=[]

    meta_description_content = tabs_dict[active_tab or "default"]["meta_description_content"]
    if active_tab:
        active_tab = "_" + active_tab

    meta = {
        "description": meta_description_content,
        }

    # there's a problem here - pages such as Cardiff's /person/dr-kathrine-jane-craig/ don't
    # get the menu right - why?
    # print "****", request.auto_page_url, request.path, request.current_page, entity.get_website

    return render_to_response(
        "contacts_and_people/person%s.html" % active_tab,
        {
            "person":person, # personal information
            "home_role": home_role, # entity and position
            "entity": entity,
            "template": template, # from entity
            "building": building,
            "email": email, # from person or please_contact
            "precise_location": precise_location, # from person, or None
            "contact": contact, # from person or please_contact
            "phone": phone,
            "full_address" : person.get_full_address,
            "access_note": access_note, # from person
            "tabs": tabs,
            "tab_object": person,
            "active_tab": active_tab,
            # "news_and_events": news_and_events,
            "meta": meta,
            # "links": links,
        },
        RequestContext(request),
    )

def place(request, slug, active_tab=""):
    """
    Receives active_tab from the slug.

    The template receives "_" + active_tab to identify the correct template (from includes).
    """
    place = get_object_or_404(Building, slug=slug)
    tabs_dict = { # information for each kind of place page
        "about": {
            "tab": "about",
            "title": "About",
            "address": "",
            "meta_description_content": place.summary,
        },
        "map": {
            "tab": "map",
            "title": "Map",
            "address": "map",
            "meta_description_content": "Map for " + place.identifier(),
        },
        "getting-here": {
            "tab": "getting-here",
            "title": "Getting here",
            "address": "getting-here",
            "meta_description_content": "How to get to " + place.identifier(),
        },
        "events": {
            "tab": "events",
            "title": "What's on here",
            "address": "events",
            "meta_description_content": "What's on at " + place.identifier(),
        },
    }

    # mark the active tab, if there is one
    if active_tab:
        tabs_dict[active_tab]["active"] = True

    # add tabs to the list of tabs
    tabs = [tabs_dict["about"]]
    if place.has_map():
        tabs.append(tabs_dict["map"])
    if (place.getting_here and place.getting_here.cmsplugin_set.all()) \
        or (place.access_and_parking and place.access_and_parking.cmsplugin_set.all()):
        tabs.append(tabs_dict["getting-here"])
    if place.events:
        tabs.append(tabs_dict["events"])

    if not active_tab:
        # find out what to add to the url for this tab
        active_tab=tabs[0]["address"]
        # mark the tab as active for the template
        tabs[0]["active"]=True
    # fewer than 2? not worth having tabs!
    if len(tabs)==1:
        tabs=[]

    meta_description_content = tabs_dict[active_tab or "about"]["meta_description_content"]
    if active_tab:
        active_tab = "_" + active_tab

    meta = {
        "description": meta_description_content,
        }
    page = Entity.objects.base_entity().get_website
    request.current_page = page
    template = page.get_template()

    # the three lines above were those below - which look quite wrong

    # if default_entity:
    #     page = default_entity.get_website
    #     request.current_page = page
    #     template = page.get_template()
    # else:
    #     page =  entity.get_website
    #     request.current_page = page # for the menu, so it knows where we are
    #     template = page.get_template()

    return render_to_response(
        "contacts_and_people/place%s.html" % active_tab,
        {
        "place":place,
        "tabs": tabs,
        "tab_object": place,
        "active_tab": active_tab,
        "template": template,
        "meta": meta,
        },
        RequestContext(request),        )


def ajaxGetMembershipForPerson(request):
    #Which person was/is selected
    try:
        person_id = int( request.GET.get("person_id") )
    except ValueError:
        person_id = 0
    #If editing a current displayrole
    try:
        displayrole_id = int( request.GET.get("displayrole_id") )
    except ValueError:
        displayrole_id = 0
    #If editing a current membership
    try:
        membership_id = int( request.GET.get("membership_id") )
    except ValueError:
        membership_id = 0
    #Server response to AJAX
    response = http.HttpResponse()
    #BLANK option
    response.write ('<option value="">---------</option>')
    #If valid person selected make <option> list of all their existing memberships
    if (person_id > 0 ):
        membership_forperson_list = Membership.objects.filter(person__id = person_id).order_by('entity__name')
        for membership in membership_forperson_list:
            #dont include this membership if it is the one we are editing
            if membership.id != membership_id:
                #add a SELECTED clause if this is the display_role that was previously chosen
                if membership.id == displayrole_id:
                    is_selected = " selected "
                else:
                    is_selected = ""
                #return an <option> entry for that membership
                response.write('<option ' + is_selected + ' value="' + unicode(membership.id) + '">' + \
                                     unicode(membership.entity) + ' - ' + unicode(membership.role) + \
                                 '</option>')
    #Done
    return response

def ajax_people_search(request):
    from django.db.models import Count
    
    search_terms = request.GET.get('search_terms', '')
    obj_skip = int(request.GET.get('obj_skip', 0))
    obj_return = int(request.GET.get('obj_return', 20))
    get_entities_list = bool(request.GET.get('get_entities_list', False))
    filter_by_entity_id = int(request.GET.get('filter_by_entity_id', 0))
    # naive search by surname only for now
    people = Person.objects.filter(surname__icontains=search_terms).distinct() # distinct is needed because of select_related
    if filter_by_entity_id > 0:
        people = people.filter(entities__id=filter_by_entity_id)
    entities = Entity.objects.filter(people__in=people).select_related('building').annotate(Count('members'))
    people_details = people.select_related('member_of').prefetch_related('phone_contacts')
    people_view = people_details[obj_skip:obj_skip+obj_return]

    entities_to_ret = {}
    if get_entities_list:
        for e in entities:
            e_t_r = {
                'name': e.name,
                'inst_address': [ee.name for ee in reversed(e._get_institutional_address)],
                'postal_address': e.get_postal_address,
                'members_count': e.members__count,
            }
            entities_to_ret[e.pk] = e_t_r

    people_to_ret = []
    for p in people_view:
        p_t_r = {
            'name': unicode(p),
            'email': p.email,
            'phones': ', '.join(unicode(pc) for pc in p.phone_contacts.all()),
            'role': p.get_role.role if p.get_role else '',
            'entity_id': p.get_entity.pk if p.get_entity else '',
        }
        people_to_ret.append(p_t_r)

    ret = {
        'entities': entities_to_ret,
        'people': people_to_ret,
        'people_count': people.count(),
    }
    return http.HttpResponse(content=simplejson.dumps(ret, ensure_ascii=False, indent=4), mimetype='application/json; charset=utf-8')
    


