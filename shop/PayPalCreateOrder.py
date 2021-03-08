from shop.paypal_auth import PayPalClient
from paypalcheckoutsdk.orders import OrdersCreateRequest

class CreateOrder(PayPalClient):

	#2. Set up your server to receive a call from the client
	""" This is the sample function to create an order. It uses the
	JSON body returned by buildRequestBody() to create an order."""

	def create_order(self, purchase_items,site_name,return_url,cancel_url,debug=True):
		
		request = OrdersCreateRequest()
		request.prefer('return=representation')
		#3. Call PayPal to set up a transaction
		request.request_body(self.build_request_body(purchase_items,site_name,return_url,cancel_url))
		response = self.client.execute(request)

		if debug:
			print('Status Code: ', response.status_code)
			print('Status: ', response.result.status)
			print('Order ID: ', response.result.id)
			print('Intent: ', response.result.intent)
			print('Links:')

		return_link = ""
		for link in response.result.links:
			print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
			print('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
	                     response.result.purchase_units[0].amount.value))
			if link.rel =='approve':
				return_link = link.href

		return response

	"""Setting up the JSON request body for creating the order. Set the intent in the
	request body to "CAPTURE" for capture intent flow."""
	@staticmethod
	def build_request_body(purchase_items,site_name,return_url,cancel_url):
		"""Method to create body with CAPTURE intent"""
		return \
		  {
		    "intent": "CAPTURE",
		    "application_context": {
		      "brand_name": site_name,
		      "landing_page": "BILLING",
		      "shipping_preference": "SET_PROVIDED_ADDRESS",
		      "user_action": "PAY_NOW",
		      "return_url": return_url,
		      "cancel_url": cancel_url,
		    },
		    "purchase_units": purchase_items
		  }

"""This is the driver function that invokes the createOrder function to create
   a sample order."""
if __name__ == "__main__":
	
	CreateOrder().create_order(purchase_items="", site_name="", return_url="", cancel_url="", debug=True)



		