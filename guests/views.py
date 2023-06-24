import base64
from collections import namedtuple
import random
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
from guests import csv_import
from guests.invitation import get_invitation_context, INVITATION_TEMPLATE, guess_party_by_invite_id_or_404, \
    send_invitation_email
from guests.models import Guest, MEALS, Party, INVITATION_ID_LENGTH
from guests.save_the_date import get_save_the_date_context, send_save_the_date_email, SAVE_THE_DATE_TEMPLATE, \
    SAVE_THE_DATE_CONTEXT_MAP


class GuestListView(ListView):
    model = Guest


@login_required
def export_guests(request):
    export = csv_import.export_guests()
    response = HttpResponse(export.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all-guests.csv'
    return response


@login_required
def dashboard(request):
    parties_with_pending_invites = Party.objects.filter(
        is_attending=None
    ).order_by('category', 'name')
    parties_with_unopen_invites = parties_with_pending_invites.filter(invitation_opened=None)
    parties_with_open_unresponded_invites = parties_with_pending_invites.exclude(invitation_opened=None)
    attending_guests = Guest.objects.filter(is_attending=True)
    meal_breakdown = attending_guests.exclude(meal=None).values('meal').annotate(count=Count('*'))
    category_breakdown = attending_guests.values('party__category').annotate(count=Count('*'))
    return render(request, 'guests/dashboard.html', context={
        'couple_name': settings.BRIDE_AND_GROOM,
        'guests': Guest.objects.filter(is_attending=True).count(),
        'possible_guests': Guest.objects.exclude(is_attending=False).count(),
        'not_coming_guests': Guest.objects.filter(is_attending=False).count(),
        'pending_invites': parties_with_pending_invites.count(),
        'pending_guests': Guest.objects.filter(is_attending=None).count(),
        'guests_without_meals': guests_without_meals,
        'parties_with_unopen_invites': parties_with_unopen_invites,
        'parties_with_open_unresponded_invites': parties_with_open_unresponded_invites,
        'unopened_invite_count': parties_with_unopen_invites.count(),
        'total_invites': Party.objects.count(),
        'meal_breakdown': meal_breakdown,
        'category_breakdown': category_breakdown,
    })


def invitation(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    if party.invitation_opened is None:
        # update if this is the first time the invitation was opened
        party.invitation_opened = datetime.utcnow()
        party.save()
    mainGuestAttends = False
    if request.method == 'POST':
        for response in _parse_invite_params(request.POST):
            guest = Guest.objects.get(pk=response.guest_pk)
            assert guest.party == party
            if guest.is_plus_one and not mainGuestAttends:
                guest.is_attending = False
                guest.plus_one_name = None
                guest.meal = None
                guest.is_allergic = None
                guest.allergic = None
            else:
                guest.is_attending = response.is_attending
                mainGuestAttends = guest.is_attending
                if response.is_attending:
                    guest.plus_one_name = response.plus_one_name if guest.is_plus_one else None
                    guest.meal = response.meal
                    guest.is_allergic = response.is_allergic
                    guest.allergic = response.allergic if guest.is_allergic else None
                else:
                    guest.meal = None
                    guest.is_allergic = None
                    guest.allergic = None   
            guest.save()
            party.save()
        party.is_attending = party.any_guests_attending
        party.save()
        if party.is_attending:
            transportation = request.POST.get('transportation')
            party.transportationNeeded = True if transportation == 'needed' else False
            party.friSatAccommodation = True if request.POST.get('friSat') else False
            party.satSunAccommodation = True if request.POST.get('SatSun') else False
        print(request.POST.get('prefersPhone'))
        print(request.POST.get('prefersEmail'))
        party.phoneNumber = request.POST.get('phoneNumber') if request.POST.get('prefersPhone') else None
        party.emailAddress = request.POST.get('emailAddress') if request.POST.get('prefersEmail') else None
        if request.POST.get('comments'):
            comments = request.POST.get('comments')
            party.comments = comments if not party.comments else '{}; {}'.format(party.comments, comments)  
        party.save()
        return HttpResponseRedirect(reverse('rsvp-confirm', args=[invite_id]))
    return render(request, template_name='guests/invitation.html', context={
        'party': party,
        'meals': MEALS+[('is_allergic', 'alergia')],
        'couple_name_genitive': settings.BRIDE_AND_GROOM_GENITIVE,
        'wedding_date': settings.WEDDING_DATE,
        'wedding_location': settings.WEDDING_LOCATION,
        'website': settings.WEDDING_WEBSITE_URL
    })

def rsvp(request):
    if request.method == "POST":
        if request.POST.get("rsvp"):
            invite_id = request.POST.get("rsvp")
            if Party.objects.filter(invitation_id=invite_id).exists():
                return HttpResponseRedirect(reverse('invitation', args=[invite_id]))
            else:
                return HttpResponseRedirect(reverse('rsvp-invalid'))
    return render(request, template_name='guests/rsvp.html', context={
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
        'rsvp_code_length': INVITATION_ID_LENGTH,
        'couple_name_genitive': settings.BRIDE_AND_GROOM_GENITIVE,
        'website': settings.WEDDING_WEBSITE_URL,
    })


def rsvp_invalid(request):
    return render(request, template_name='guests/rsvp-invalid.html', context={
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
        'rsvp_code_length': INVITATION_ID_LENGTH,
        'couple_name_genitive': settings.BRIDE_AND_GROOM_GENITIVE,
        'website': settings.WEDDING_WEBSITE_URL,
    })

InviteResponse = namedtuple('InviteResponse', ['guest_pk', 'is_attending', 'plus_one_name', 'meal', 'is_allergic', 'allergic'])


def _parse_invite_params(params):
    responses = {}
    for param, value in params.items():
        if param.startswith('attending'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['attending'] = True if value == 'yes' else False
            responses[pk] = response
        if param.startswith('plus_one'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['plus_one_name'] = value
            responses[pk] = response
        elif param.startswith('meal'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['meal'] = value
            responses[pk] = response
        elif param.startswith('is_allergic'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['is_allergic'] = True if value == 'on' else False
            responses[pk] = response
        elif param.startswith('allergic'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['allergic'] = value
            responses[pk] = response

    for pk, response in responses.items():
        if 'is_allergic' not in response.keys():
            response['is_allergic'] = False if response['attending'] else None
        yield InviteResponse(pk, response['attending'], response.get('plus_one_name', None), response.get('meal', None), response['is_allergic'], response.get('allergic', None))


def rsvp_confirm(request, invite_id=None):
    party = guess_party_by_invite_id_or_404(invite_id)
    return render(request, template_name='guests/rsvp-confirmation.html', context={
        'party': party,
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
        'website': settings.WEDDING_WEBSITE_URL,
        'couple_name_genitive': settings.BRIDE_AND_GROOM_GENITIVE
    })


@login_required
def invitation_email_preview(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    context = get_invitation_context(party)
    return render(request, INVITATION_TEMPLATE, context=context)


@login_required
def invitation_email_test(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    send_invitation_email(party, recipients=[settings.DEFAULT_WEDDING_TEST_EMAIL])
    return HttpResponse('sent!')


def save_the_date_random(request):
    template_id = random.choice(SAVE_THE_DATE_CONTEXT_MAP.keys())
    return save_the_date_preview(request, template_id)


def save_the_date_preview(request, template_id):
    context = get_save_the_date_context(template_id)
    context['email_mode'] = False
    return render(request, SAVE_THE_DATE_TEMPLATE, context=context)


@login_required
def test_email(request, template_id):
    context = get_save_the_date_context(template_id)
    send_save_the_date_email(context, [settings.DEFAULT_WEDDING_TEST_EMAIL])
    return HttpResponse('sent!')


def _base64_encode(filepath):
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read())
