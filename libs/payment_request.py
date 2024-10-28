from sslcommerz_lib import SSLCOMMERZ
from libs.transaction_id import generate_transaction_id
from libs.link import frontend_link
def payment_request(amount,user):
        settings = { 'store_id': 'tfbfo671efb41acdf3', 'store_pass': 'tfbfo671efb41acdf3@ssl', 'issandbox': True }
        sslcz = SSLCOMMERZ(settings)
        post_body = {}
        post_body['total_amount'] = amount
        post_body['currency'] = "BDT"
        post_body['tran_id'] = generate_transaction_id()
        post_body['success_url'] = f"{frontend_link}/transactions"
        post_body['fail_url'] = f"{frontend_link}/deposit"
        post_body['cancel_url'] = f"{frontend_link}/deposit"
        post_body['emi_option'] = 0
        post_body['cus_name'] = user.username
        post_body['cus_email'] = user.email
        post_body['cus_phone'] = user.profile.phone_no
        post_body['cus_add1'] = user.profile.street_address
        post_body['cus_city'] = user.profile.city
        post_body['cus_country'] = "Bangladesh"
        post_body['shipping_method'] = "NO"
        post_body['multi_card_name'] = ""
        post_body['num_of_item'] = 1
        post_body['product_name'] = "Test"
        post_body['product_category'] = "Test Category"
        post_body['product_profile'] = "general"


        response = sslcz.createSession(post_body) # API response
        
        return response['GatewayPageURL']