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
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import urllib
from mezzanine.conf import settings


class Endpoint(TemplateView):
    
    default_response_text = 'Nothing to see here'
    verify_url = settings.PAYPAL_SUBMIT_URL
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(EndPoint, self).dispatch(*args, **kwargs)
        
        
    def do_post(self, url, args):
        return urllib.urlopen(url, urllib.urlencode(args)).read()
    
    def verify(self, data):
        args = {
            'cmd': '_notify-validate',
        }
        args.update(data)
        return self.do_post(self.verify_url, args) == 'VERIFIED'
    
    def default_response(self):
        return HttpResponse(self.default_response_text)
    
    
    def __call__(self, request, uuid):
        r = None
        #print "UUID:",uuid
        #data = dict(request.GET.items())
        #r = self.process(data, uuid)
        
        
        if request.method == 'POST':
            
            ipn_handler = settings.ORDER_IPN_HANDLER_CLASS()
            
            data = dict(request.POST.items())
            # We need to post that BACK to PayPal to confirm it
            if self.verify(data):
                r = ipn_handler.process(data, uuid)
            else:
                r = ipn_handler.process_invalid(data, uuid)
        if r:
            return r
        else:
            return self.default_response()
    
    def process(self, data):
        pass
    
    def process_invalid(self, data):
        pass

        

#class CartidgePaypalIpnEndpoint(Endpoint):
    #def process(self, data, uuid):
        ## Do something with valid data from PayPal - e-mail it to yourself,
        ## stick it in a database, generate a license key and e-mail it to the
        ## user... whatever
        #new_order = Order.objects.filter(callback_uuid=uuid)
        #if order:
            #o = OrderReady(order=new_order)
            #o.save()
        #else:
            #o = OrderFailed(reason="Order not found", uuid=uuid)
            #o.save()
    
    
    #def process_invalid(self, data, uuid):
        ## Do something with invalid data (could be from anywhere) - you 
        ## should probably log this somewhere
        #o = OrderFailed(reason="Could not verify", uuid=uuid)
        #o.save()
    