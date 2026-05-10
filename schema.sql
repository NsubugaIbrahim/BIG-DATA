CREATE TABLE patents (
	patent_id TEXT, 
	title TEXT, 
	filing_date DATETIME, 
	abstract TEXT, 
	year INTEGER
);

CREATE TABLE inventors (
	inventor_id TEXT, 
	patent_id TEXT, 
	location_id TEXT, 
	name TEXT, 
	country TEXT, 
	state TEXT, 
	city TEXT, 
	latitude FLOAT, 
	longitude FLOAT
);

CREATE TABLE companies (
	company_id TEXT, 
	patent_id TEXT, 
	name TEXT
);

CREATE TABLE locations (
	location_id TEXT, 
	country TEXT, 
	state TEXT, 
	city TEXT, 
	latitude FLOAT, 
	longitude FLOAT
);

CREATE TABLE relationships (
	inventor_id TEXT, 
	patent_id TEXT, 
	company_id TEXT
);

