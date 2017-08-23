
create table visit (
	id serial primary key,
	ip_address inet,
	user_agent text,
	http_wb boolean,
	https_wb boolean,
	http_ia boolean,
	https_ia boolean,

	asn text,
	asn_cidr text,
	asn_description text,
	asn_country_code text,
	data text,
	created timestamp without time zone default (current_timestamp at time zone 'utc')
);
