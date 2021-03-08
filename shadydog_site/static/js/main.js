function get_facebook_data(url){

	fetch("/facebook_config/")
	.then((result) => { return result.json(); })
	.then((data) => {
		
		const access_token = data.access_token;
		fetch("https://graph.facebook.com/oauth/access_token?"+access_token+"&grant_type=client_credentials")
		.then((result) => { return result.json(); })
		.then((data) => {
			console.log(data.access_token);
			
			fetch("https://graph.facebook.com/shadydogdesign/insights/page_impressions_unique&access_token=" + data.access_token)
			.then((result) => { return result.json(); })
			.then((data) => {
				console.log(data);
			})

		})
	});

}

function get_instagram_data(){
	//url = "https://www.instagram.com/shadydogdesign/"
	//https://www.instagram.com/p/CLnKyMSJRmU/
	//https://graph.facebook.com/v10.0/instagram_oembed?url=https://www.instagram.com/shadydogdesign/&access_token=474049620289634|92adae7d7dbdb2cf9d007e1e45c16326
	fetch("https://graph.facebook.com/v10.0/instagram_oembed?url=https://www.instagram.com/p/CLnKyMSJRmU/&omitscript=true&maxwidth=320&access_token=474049620289634|92adae7d7dbdb2cf9d007e1e45c16326")
		.then((result) => { return result.json(); })
		.then((data) => {
			console.log(data);
			console.log(data.thumbnail_width);
			document.getElementById("insta").innerHTML= data.html

		})

}

function process_order(the_total_str){
	
	csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	
	the_data = {
		order_total: the_total_str
	}

	fetch("/process_order/",{
		method: "POST",
		body: JSON.stringify(the_data),
		headers: {"Content-type": "application/json; charset=UTF-8",
		'X-CSRFToken': csrftoken}
	})
	.then((result) => { return result.json();} )	
	.then((data) => {
		console.log(data)
		if (data.order_created == false){
			populate_pop_up_message("Somehow your ", "Cart", " has corrupted and we cannot process this order. Please select your items again.", false);
			
		}else{
			// Redirect to success page
			window.location.href = "/success"+ data.return_url_string;
		}


	});


}

function get_stripe_checkout(item, disc_amt, disc_code, disc_desc){

	var the_item_id = item.id;
	var the_coupon = ""

	fetch("/stripe_config/")
	.then((result) => { return result.json(); })
	.then((data) => {
		// initialise Stripe.js
		const stripe = Stripe(data.publicKey);
		
		// Get coupon code
		fetch("/create_stripe_coupon/")
		.then((result) => { return result.json(); })
		.then((data) => {
			
			if (data.success == false){
				
				populate_pop_up_message("Somehow your ", "Discount Code", " was not accepted by Stripe and we cannot proceed to payment. Please select Paypal payment method or try again later.", false);
		
			}else{
				console.log(data.couponCode)
				the_coupon = data.couponCode

				if (the_coupon==""){
					the_url = "/create_checkout_session/" + the_item_id + "/"
				}else{
					the_url = "/create_checkout_session/" + the_item_id + "/" + the_coupon + "/"
				}

				// Get Checkout Session ID
				fetch(the_url)
				.then((result) => { return result.json(); })
				.then((data) => {
					
					if (data.order_created == false){
						populate_pop_up_message("Somehow your ", "Cart", " has corrupted and we cannot proceed to payment. Please select your items again.", false);
				
					}else{
						// Redirect to Stripe Checkout
						return stripe.redirectToCheckout({sessionId: data.sessionId})
					}
				})
				.then((res) =>{
				console.log(res);
				});
			}

		
		})
		

	});
	
}

function get_stripe_checkout_WORKING(item){

	var the_item_id = item.id;
	fetch("/stripe_config/")
	.then((result) => { return result.json(); })
	.then((data) => {
		// initialise Stripe.js
		const stripe = Stripe(data.publicKey);

		// Get Checkout Session ID
		fetch("/create_checkout_session/" + the_item_id + "/")
		.then((result) => { return result.json(); })
		.then((data) => {
			

			if (data.order_created == false){
				populate_pop_up_message("Somehow your ", "Cart", " has corrupted and we cannot proceed to payment. Please select your items again.", false);
		
			}else{
				// Redirect to Stripe Checkout
				return stripe.redirectToCheckout({sessionId: data.sessionId})
			}
		})
		
		.then((res) =>{
			console.log(res);
		});
	});
	
}

function get_stripe_checkout_with_deets(item, item_quantity, notes){

	var the_item_id = item.id;
	fetch("/config/")
	.then((result) => { return result.json(); })
	.then((data) => {
		// initialise Stripe.js
		const stripe = Stripe(data.publicKey);

		// Get Checkout Session ID
		fetch("/create-checkout-session-deets/" + the_item_id + "/" + item_quantity + "/")
		.then((result) => { return result.json(); })
		.then((data) => {
			console.log(data);
			// Redirect to Stripe Checkout
			return stripe.redirectToCheckout({sessionId: data.sessionId})
		})
		.then((res) =>{
			console.log(res);
		});
	});
	

}

function contact_msg(){

	populate_pop_up_message("For bulk orders and all other enquiries, contact:<br> ", "<span style='font-size:40px'>Ciara Ryan</span>", " <br> +353 (0)86 451 0004 <br> info@shadydogdesign.com", false);
}



function check_items_for_payment(){

	fetch("/check_missing_fields/")
	.then((result) => { return result.json(); })
	.then((data) => {

		if(data.success == true){

			if (data.missing_address_fields.length == 0){
									
				console.log("Validation all good!");

			}else{
				if (data.missing_address_fields.includes(",")){

					field_noun = "fields are";
				}else{
					field_noun = "field is";
				}

				populate_pop_up_message("Please update your ", "Shipping Address", ". The following " + field_noun + " missing: " + data.missing_address_fields, false);
		
			}

		}else{

			populate_pop_up_message("Somehow your ", "Cart", " has corrupted and we cannot proceed to payment. Please select your items again.", false);
			
		}

	})
	.catch(err => console.log("Issue with checkout validation", err));

}


function return_to_home_page(){

	window.location.href = "/";
}

function view_order_summary(){

	window.location.href = "/order_summary/";

}

function view_order_summary(){

	csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	fetch("/order_summary/",{
		method: "POST",
		headers: {"Content-type": "application/json; charset=UTF-8",
		'X-CSRFToken': csrftoken}
	})
	.then((result) => { return result.json();} )
	.then((data) => {
		if(data.success == true){
			console.log("returned from order summary - all ok there");
		}
	});
	
}

function updateShippingAddress(form_data, postage_type_obj){
	
	csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	
	fetch("/update_shipping_address/",{
		method: "POST",
		body: JSON.stringify(form_data),
		headers: {"Content-type": "application/json; charset=UTF-8",
		'X-CSRFToken': csrftoken}
	})
	.then((result) => { return result.json();} )	
	.then((data) => {
			
			fetch("/get_postage_options/",{
			method: "POST",
			body: JSON.stringify(postage_type_obj),
			headers: {"Content-type": "application/json; charset=UTF-8",
			'X-CSRFToken': csrftoken}
			})

			.then((result) => { return result.json(); })
			.then((data) => {
				
				if (data.cookie_issue == true){
					console.log("Cookies are not enabled");
					populate_pop_up_message(data.cookie_message, "", "", false);
				}
				
				returned_postage_display_obj = data.new_postage_data;
	    		update_postage_display_data(returned_postage_display_obj);

			});

			update_shipping_address_data(data.new_form_data, data.old_form_data);
			updateCartShippingTotal(data.cart_shipping_total);
			updateCartDiscountTotal(data.discount_amount);	
			updateCartFinalTotal(data.cart_final_total);

			document.getElementById('pop_up_address').style.display='none';	
		


	});
	
}

function updateDiscountDetails(form_data){

	csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

	fetch("/update_discount_code/",{
		method: "POST",
		body: JSON.stringify(form_data),
		headers: {"Content-type": "application/json; charset=UTF-8",
		'X-CSRFToken': csrftoken}
	})
	.then((result) => { return result.json();} )
	
	.then((data) => {
		
		if (data.cookie_issue == true){
			console.log("Cookies are not enabled");
			populate_pop_up_message(data.cookie_message, "", "", false);
		}

		if(data.success == true){
			
			update_discount_details_data(data.new_form_data, data.old_form_data,data.discount_message);
			updateCartDiscountTotal(data.discount_amount);
			updateCartFinalTotal(data.cart_final_total);

			
			document.getElementById('pop_up_discount').style.display='none';
	        			
	    }

	});

}


function updateDeliveryDetails(form_data){

	csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

	fetch("/update_delivery_details/",{
		method: "POST",
		body: JSON.stringify(form_data),
		headers: {"Content-type": "application/json; charset=UTF-8",
		'X-CSRFToken': csrftoken}
	})
	.then((result) => { return result.json();} )
	
	.then((data) => {
		
		if (data.cookie_issue == true){
			console.log("Cookies are not enabled");
			populate_pop_up_message(data.cookie_message, "", "", false);
		}

		if(data.success == true){
			
			update_delivery_details_data(data.new_form_data, data.old_form_data);
			document.getElementById('pop_up_instructions').style.display='none';
	        			
	    }

	});
}

function updateCountryName(country_code, el_id){
	
	fetch("/get_country/" + country_code + "/")
	.then((result) => { return result.json(); })
	.then((data) => {
		
		if(data.success == true){

			document.getElementById(el_id).innerHTML = data.country_name + " (" + country_code + ")";
			updateCartShippingCountryName(data.country_name);
		}

	})
	.catch(err => console.log("Country Name not returned", err));

}


function populate_pop_up_message(message_part_1, message_fancy_part, message_part_2, show_footer, message_action_button){

	if (show_footer == false){

		show_it = 'none';

	}else{

		show_it = 'block';

	}

	document.getElementById('message_part_1').innerHTML=message_part_1;
	document.getElementById('message_fancy_part').innerHTML=message_fancy_part;
	document.getElementById('message_part_2').innerHTML=message_part_2;
	document.getElementById('message_footer').style.display=show_it;
	if (show_footer){
		document.getElementById('message_action_button').innerHTML = message_action_button;
	}


	document.getElementById('pop_up_message').style.display='block';

}

function create_action_button(action_function_name, var1, isStrVar1, var2, isStrVar2){
	//<span id="message_action_button" class="w3-btn w3-border w3-black w3-border-white w3-hover-white w3-round w3-small" style="margin-top:5px"></span>
	//deleteItemFromCart(product_id,product_name);
	
	remove_action_button();

	if (isStrVar1){

		formatted_var_1 = "('" + var1 + "'"

	}else{

		formatted_var_1 = "(" + var1 
	}

	if (isStrVar2){

		formatted_var_2 = ",'" + var2 + "')"

	}else{

		formatted_var_2 = "," + var2 + ")"
	}
	
	var span = document.createElement('span');
	span.setAttribute ('id', 'message_action_button');
	span.setAttribute ('class', 'w3-btn w3-border w3-black w3-border-white w3-hover-white w3-round w3-small');
	span.setAttribute ('style', 'margin-top:5px');
	span.setAttribute ('onclick', action_function_name + formatted_var_1 + formatted_var_2 );

	var footer = document.getElementById('message_footer');
	footer.insertBefore(span, footer.childNodes[0]);
	
	//console.log(document.getElementById('message_footer'));
}



function remove_action_button(){

	var lstContainer = document.getElementById("message_footer");
    var footer_area = lstContainer.getElementsByClassName("w3-btn");
    for (var i = 0; i < footer_area.length; i++) {
        if (footer_area[i].id == 'message_action_button'){
	        footer_area[i].remove();
	    }
    }

}


function create_country_flag(country_code){
	//<img class="w3-border w3-border-white" style="margin-bottom:0px;" id="id_shipping_address_country_flag_ro" src="{{ country.flag }}" />
	remove_country_flag();

	var lstContainer = document.getElementById("content_body");
	var flag_imgs = lstContainer.getElementsByClassName("add_flag_img");
	for (var i = 0; i < flag_imgs.length; i++) {

		var span = document.createElement('img');
		span.setAttribute ('class', 'flag_img w3-border w3-border-white');
		span.setAttribute ('style', 'margin-bottom:0px');
		span.setAttribute("src", "/static/flags/"+ country_code.toLowerCase() + ".gif");

	    flag_imgs[i].appendChild(span);
	   
    }
	
}

function remove_country_flag(){

	var lstContainer = document.getElementById("content_body");
    var the_flag_imgs = lstContainer.getElementsByClassName("flag_img");
    
    for (var i = 0; i < the_flag_imgs.length; i++) {
    	
    	the_flag_imgs[i].remove();
    	i=i-1;   
    }

    updateCartShippingCountryName("");
}

function updateInnerHTML(idName,className,newInnerHTML){

	if (idName.length >0){

		document.getElementById(idName).innerHTML = newInnerHTML;

	}

	if (className.length >0){

		elList = document.querySelectorAll("." + className);
	    var i;
	    for(i=0; i < elList.length; i++){
	    	elList[i].innerHTML = newInnerHTML;
	    }
	}

}

function updateCartItemCount(new_total){

	updateInnerHTML("","cart_item_count",new_total);

}

function updateCartShippingCountryName(new_name){

	updateInnerHTML("", "country_name", new_name);
}

function updateShippingDisplayCost(new_value,postageType){

	updateInnerHTML(cost_id, "", new_value);
}

function updateCartSubTotal(new_total){

	updateInnerHTML("","cart_subtotal",new_total);
}

function updateCartShippingTotal(new_total){

	updateInnerHTML("","cart_shipping_total",new_total);
}

function updateCartDiscountTotal(new_total){

	updateInnerHTML("","cart_discount_total",new_total);
}

function updateCartFinalTotal(new_total){

	updateInnerHTML("","cart_final_total",new_total);
}

function addItemToCart(product_id, product_name, quantity){
	
	fetch("/add_to_cart/" + product_id + "/" + quantity + "/")

	.then((result) => { return result.json(); })
	.then((data) => {
		
		if (data.cookie_issue == true){
			console.log("Cookies are not enabled");
			populate_pop_up_message(data.cookie_message, "", "", false);
			
		}

		if(data.success == true){

			if(data.quantity_added == quantity){
				populate_pop_up_message("Thank you. ", product_name, "(x" + data.quantity_added + ") has been added to your Cart.", false);
			}else{
				populate_pop_up_message("Thank you. ", product_name, "(x" + data.quantity_added + ") has been added to your Cart. This is less than you requested, due to maximum allowed per order.", false);
			}

			updateCartItemCount(data.new_items_count);
		}

		if(data.success == false){

			populate_pop_up_message("Sorry. ", product_name, "(x" + quantity + ") has not been added to your Cart. Your cart has reached maximum allowed per order.", false);
			
		}

	});
}

function updateCart(product_id, product_name, quantity){

	fetch("/update_cart/" + product_id + "/" + quantity + "/")
		
	.then((result) => { return result.json(); })
	.then((data) => {
		
		if (data.cookie_issue == true){
			console.log("Cookies are not enabled");
			populate_pop_up_message(data.cookie_message, "", "", false);
		}

		if(data.success == true){
				        
	        document.getElementById("quantity_selected_" + product_id).innerHTML= quantity; 
	        document.getElementById("sub_total_" + product_id).innerHTML=data.new_total; 
	    	
	        updateCartItemCount(data.new_items_count);
			updateCartSubTotal(data.cart_subtotal);
					
	    }
	    if(data.success == false){

	    	populate_pop_up_message("Sorry. The quantity for ", product_name, " has not been updated. Your cart has reached maximum allowed per order.", false);
	       			
	    }
	});
	
	
}





function updateShippingCost(postageTypeValue,postageTypeName){
	
	fetch("/update_postage_details/" + postageTypeValue + "/")
		
	.then((result) => { return result.json(); })
	.then((data) => {
		
		if (data.cookie_issue == true){
			console.log("Cookies are not enabled");
			populate_pop_up_message(data.cookie_message, "", "", false);
		}

		if(data.success == true){
				       	    		
	        updateCartShippingTotal(data.postage_fee);
	        updateCartDiscountTotal(data.discount_amount);
	        updateCartFinalTotal(data.cart_final_total);
	        populate_pop_up_message("Your ", "Shipping Costs ", " have been updated to the '" + postageTypeName + "' option (" + data.postage_fee + ")." , false); 
			
	    }
	    if(data.success == false){
	    	
	    	populate_pop_up_message("In order to update your ", "Shipping Costs", ", please ensure you have added a Country to your Shipping Address.", false);
	       			
	    }
	});
	
}

function deleteItemFromCart(product_id,product_name){

	fetch("/delete_item/" + product_id + "/")
		
	.then((result) => { return result.json(); })
	.then((data) => {

		if (data.cookie_issue == true){
			console.log("Cookies are not enabled");
			populate_pop_up_message(data.cookie_message, "", "", false);
		}
		
		if(data.success == true){

			populate_pop_up_message("Ok, ", product_name, " has been removed from your Cart", false);

			document.getElementById(product_id).style.display='none';

			document.getElementById("quantity_selected_" + product_id).innerHTML=0; 
	        document.getElementById("sub_total_" + product_id).innerHTML=data.new_total; 


	        updateCartItemCount(data.new_items_count);	      
			updateCartSubTotal(data.cart_subtotal);
			

	        if (data.cart_subtotal == 0){

	        	document.getElementById("cart_body").style.display='none';
	        	document.getElementById("empty_cart").innerHTML = " is empty";      	

	        }
	  }

	});
	
	
}

function truncate(str, length, ending){

    	if (length == null) {
      		length = 100;
	    }
	    if (ending == null) {
	      ending = '...';
	    }
	    if (str.length > length) {
	      return str.substring(0, length - ending.length) + ending;
	    } else {
	      return str;
	    }

    }

function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

function add_spinner(el_id, show_text){

    document.getElementById(el_id).innerHTML = show_text + " <i class='fa fa-spinner fa-spin fa-fw'></i><span class='sr-only'>" + show_text + "</span>"

}

function remove_spinner(el_id, show_text){

    document.getElementById(el_id).innerHTML = show_text

}

function disable_el(el_id){

    document.getElementById(el_id).className += " w3-disabled"

}



function enable_el(el_id){

    document.getElementById(el_id).className = document.getElementById(el_id).className.replace("w3-disabled", "")
    
}