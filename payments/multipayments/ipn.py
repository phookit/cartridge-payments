"""
Classes for accepting PayPal's Instant Payment Notification messages in a 
Django application (or Django-on-App-Engine):

https://www.paypal.com/ipn

Usage:

from paypal import Endpoint  # Or AppEngineEndpoint as Endpoint

class MyEndPoint(Endpoint):
    def process(self, data):
        # Do something with valid data from PayPal - e-mail it to yourself,
        # stick it in a database, generate a license key and e-mail it to the
        # user... whatever
        
    def process_invalid(self, data):
        # Do something with invalid data (could be from anywhere) - you 
        # should probably log this somewhere

These methods can optionally return an HttpResponse - if they don't, a 
default response will be sent.

Then in urls.py:

    (r'^endpoint/$', MyEndPoint()),

"data" looks something like this:

{
    'business': 'your-business@example.com',
    'charset': 'windows-1252',
    'cmd': '_notify-validate',
    'first_name': 'S',
    'last_name': 'Willison',
    'mc_currency': 'GBP',
    'mc_fee': '0.01',
    'mc_gross': '0.01',
    'notify_version': '2.4',
    'payer_business_name': 'Example Ltd',
    'payer_email': 'payer@example.com',
    'payer_id': '5YKXXXXXX6',
    'payer_status': 'verified',
    'payment_date': '11:45:00 Aug 13, 2008 PDT',
    'payment_fee': '',
    'payment_gross': '',
    'payment_status': 'Completed',
    'payment_type': 'instant',
    'receiver_email': 'your-email@example.com',
    'receiver_id': 'CXZXXXXXQ',
    'residence_country': 'GB',
    'txn_id': '79F58253T2487374D',
    'txn_type': 'send_money',
    'verify_sign': 'AOH.JxXLRThnyE4toeuh-.oeurch23.QyBY-O1N'
}
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import urllib
from mezzanine.utils.importing import import_dotted_path
from mezzanine.conf import settings

handler = lambda s: import_dotted_path(s) if s else lambda *args: None

ipn_handler = handler(settings.ORDER_IPN_HANDLER_CLASS)()

@csrf_exempt
def _do_post(url, args):
    return urllib.urlopen(url, urllib.urlencode(args)).read()


@csrf_exempt
def _verify(data):
    args = { 'cmd': '_notify-validate' }
    args.update(data)
    return _do_post(settings.PAYPAL_SUBMIT_URL, args) == 'VERIFIED'


@csrf_exempt
def EndPoint(request, uuid):
    r = None
    data = dict(request.POST.items())
    ipn_handler.process(data, uuid)

    if request.method == 'POST':
        print "GOT POST"    
        data = dict(request.POST.items())
        print "GOT DATA AS DICT"
        # We need to post that BACK to PayPal to confirm it
        if _verify(data):
            print "VERIFIED"
            r = ipn_handler.process(data, uuid)
        else:
            print "NOT VERIFIED"
            r = ipn_handler.process_invalid(data, uuid)
    if r:
        return r
    return HttpResponse('Nothing to see here')


