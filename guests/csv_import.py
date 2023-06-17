import csv
import io
import random
import string
from guests.models import Party, Guest, INVITATION_ID_LENGTH


def _random_uuid():
    return ''.join([random.choice(string.digits) for _ in range(INVITATION_ID_LENGTH)])

def import_guests(path):
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        first_row = True
        for row in reader:
            if first_row:
                first_row = False
                continue
            if len(row) == 6:
                party_name, first_name, last_name, is_child, category, invitation_id = row[:6]
            else:
                party_name, first_name, last_name, is_child, category = row[:5]
                invitation_id = _random_uuid()
            if not party_name:
                print ('skipping row {}'.format(row))
                continue
            party = Party.objects.get_or_create(name=party_name)[0]
            party.category = category
            if not party.invitation_id:
                party.invitation_id = invitation_id
            party.save()
            guest = Guest.objects.get_or_create(party=party, first_name=first_name, last_name=last_name)[0]
            guest.is_child = _is_true(is_child)
            guest.save()


def export_guests():
    headers = [
        'party_name', 'first_name', 'last_name',
        'is_child', 'category', 'is_attending',
        'rehearsal_dinner', 'meal', 'email', 'comments'
    ]
    file = io.StringIO()
    writer = csv.writer(file)
    writer.writerow(headers)
    for party in Party.in_default_order():
        for guest in party.guest_set.all():
            if guest.is_attending:
                writer.writerow([
                    party.name,
                    guest.first_name,
                    guest.last_name,
                    guest.is_child,
                    party.category,
                    guest.is_attending,
                    party.rehearsal_dinner,
                    guest.meal,
                    guest.email,
                    party.comments,
                ])
    return file


def _is_true(value):
    value = value or ''
    return value.lower() in ('y', 'yes', 't', 'true', '1')
