from shop.paypal_auth import PayPalClient
from paypalcheckoutsdk.orders import OrdersCaptureRequest

class CaptureOrder(PayPalClient):

	#2. Set up your server to receive a call from the client
	"""this sample function performs payment capture on the order.
	Approved order ID should be passed as an argument to this function"""

	def capture_order(self, order_id, debug=True):
		
		request = OrdersCaptureRequest(order_id)
		request.prefer('return=representation')
		#3. Call PayPal to capture an order
		response = self.client.execute(request)
	
		#4. Save the capture ID to your database. Implement logic to save capture to your database for future reference.

		if debug:
			print('Status Code: ', response.status_code)
			print('Status: ', response.result.status)
			print('Order ID: ', response.result.id)
			print('Links:')

		return_link = ""
		for link in response.result.links:
			print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
		
		print('Capture Ids: ')
		for purchase_unit in response.result.purchase_units:
			for capture in purchase_unit.payments.captures:
				print('\t', capture.id)
		print("Buyer:")
		print("\tEmail Address: {}\n\tName: {}".format(response.result.payer.email_address, 
			response.result.payer.name.given_name + " " + response.result.payer.name.surname))

		return response


"""This driver function invokes the capture order function.
Replace Order ID value with the approved order ID. """
if __name__ == "__main__":
	order_id = 'REPLACE-WITH-APPORVED-ORDER-ID'
	CaptureOrder().capture_order(order_id, debug=True)
