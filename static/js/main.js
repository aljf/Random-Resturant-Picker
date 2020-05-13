let location_val;
(function($) {

	var	$window = $(window),
		$body = $('body'),
		$document = $(document);

	// Breakpoints.
		breakpoints({
			desktop:   [ '737px',   null     ],
			wide:      [ '1201px',  null     ],
			narrow:    [ '737px',   '1200px' ],
			narrower:  [ '737px',   '1000px' ],
			mobile:    [ null,      '736px'  ]
		});

		// Title Bar.
			$(
				'<div id="titleBar">' +
					'<a href="#sidebar" class="toggle"></a>' +
					'<span class="title">' + $('#logo').html() + '</span>' +
				'</div>'
			)
				.appendTo($body);

})(jQuery);

$( document ).ready(function() {
	let result_modal = document.getElementById("resturant-container");
	let close_btn = document.getElementsByClassName("close")[0];
	$('#form').submit(function(e) {
		e.preventDefault();
	})
	getLocation();

	$('.price-input').click(function() {
		if ($(this).parent().parent().hasClass('price-activated')){
			$(this).parent().parent().removeClass('price-activated');
		} else {
			$(this).parent().parent().addClass('price-activated');
		}	
	})

	$('.distance-input').on('change', function() {
		$('.distance-input').not(this).prop('checked', false);  
		$('.distance-input').not(this).parent().parent().removeClass('distance-activated');
		$(this).parent().parent().addClass('distance-activated');
	});
	$('#form').onsubmit = function() {sendFormData()};
	close_btn.onclick = function() {
		result_modal.style.display = "none";
	  }
	window.onclick = function(event) {
		if (event.target == result_modal) {
		  result_modal.style.display = "none";
		}
	  }
});

function sendFormData() {
	// send ajax to the python server 
	// show the response on the html
	let price_val = '';
	let term_val = '';
	let radius_val;
	// let rating;
	$(".price-input:checked").each(function(){
		if (price_val.length == 0) {
			price_val = price_val + $(this).val();
		} else {
			price_val = price_val + ', ' + $(this).val();
		}
		
	});
	term_val = $('#categories option:selected').text();
	$(".distance-input:checked").each(function(){
		radius_val = $(this).val();
	});
	let formData = {price: price_val, term: term_val, radius: radius_val, location: location_val};
	let str_data = JSON.stringify(formData);
	$.ajax({
		type: "POST",
		url: "/postmethod",
		data: str_data,
		contentType: "application/json;charset=UTF-8",
        dataType: 'json',
		success: function(response){
			console.log(response);
			populateResturant(response);
		}
	})
	
}

function getLocation() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(showPosition);
	  } 
}

function showPosition(position) {
	location_val = [position.coords.latitude, position.coords.longitude];
}

function getFormData() {
	$.get("/getmethod", function(data) {
		response = $.parseJSON(data);
		console.log(response);
	})
}

function populateResturant(response) {
	$('#resturant-container').show();
	let address = response['location']['display_address'][0] + ' ' + response['location']['display_address'][1];
	let encoded_name = encodeURI(response['name']);
	$('#resturant-name').text(response['name']);
	$('#yelp-url').attr("href", response['url']);
	$('.phone-number').text(response['display_phone']);
	$('.resturant-location').text(address);
	$('#google-maps-url').attr("href", 'https://www.google.com/maps/search/?api=1&query=' + encoded_name);
	displayModal();
}

function displayModal() {
	let result_modal = document.getElementById("resturant-container");
	result_modal.style.display = "block";
}