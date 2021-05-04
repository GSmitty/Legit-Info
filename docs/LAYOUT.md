# Project Layout
The project is based in multiple different areas for each process of the application. 
Many of the commands for setting up and maintaining the database are listed and laid out in the
cfc_app/management folder. These are also listed here in [Description](https://github.com/Call-for-Code-for-Racial-Justice/Legit-Info/blob/main/DESCRIPTION.md).
Some are described by the longer description, but many of them are simply built in Django commands. Seek the Django documentation if you cannot find them in code.

Most of the front-end work is listed directly under the cfc-app folder. HTML Templates
are listed seperately in cfc-app/templates. Anything regarding the profile and user system
is not under cfc-app, but just the users folder from the main directory.

For the front-end and most of the basic data manipulation and entry past the initial database
seeding and creation, simply look to cfc-app.

## cfc-app/forms
forms.py includes the SearchForm class, which is the Django form that is used for the search feature.
Included are the country, state, county, city, and impact fields, which correspond to the individual boxes
of the search for the location fields, and the five (possibly more later) impact areas that could apply to
a search. This project creates new forms as they are necessary to update the dropdown boxes that are present
as the user filters down their search. For example, as United States is chosen, the state field should narrow down
to only states inside the US, just as counties should only list counties within the state chosen above it.

## cfc-app/views
views.py includes all of the views required and linked in urls.py. These include the search function that is used to pull up the search
from SearchForm, the results page from the search, location page, impacts page, laws page, and the functions to download the CSV file for the results,
send the results over email, etc..

## cfc-app/urls
urls.py simply includes the url extensions, with the views.py functions they point to. 

## cfc-app/models
models.py includes the Django data models for the data types used in the search functionality. Locations are the first type, which are objects
that contain many details about a specific location in the world, whether that be a country, state, county, or city. This includes a long or short name,
the id of the location in the Legiscan API, its full hierarchy code, which gives it and its parents in one string, the govlevel of the location, specifically
"city", "state", etc., and its parent directly. Impacts are the second type, which are filters for laws based off of the area of legislation they impact, such
as transportation, healthcare, security, etc.. Next is Criteria, which is created after a search is called, and becomes a combination string of the location
selected, as well as the areas it impacts. This criteria string is then sent to the algorithm that gets the results from the search. There are Law entries,
that include info about the pieces of legislation seeded into the database, with their names, locations, summaries, and now a link to the original pdf the law
was pulled and understood from. There is also a Hash class, but that fits more into utility regarding hashing the database.

# Project Workflow
This project, as stated in the [description](https://github.com/Call-for-Code-for-Racial-Justice/Legit-Info/blob/main/DESCRIPTION.md) file, is a
service that takes legislation from the Legiscan API, and uses IBM's Watson Natural Language Understanding to shrink it into a more readable summary.
Then, the law is placed, in its new shrinked form, into the database, and becomes searchable from the larger search function. This allows the user to easily
see the legislation that is passing their chosen area, and be able to quickly digest it, without having to read an entire document, or a skewed news headline.
The steps to this project running are very simple in isolation. Firstly, the server will load these pdf documents from Legiscan, and run the Watson Natural
Language Understanding on them to create these new summaries. After placing them into the database, which will also be loaded with the list of valid areas, and 
any users in the system, the site will be able to accept any searches from a user to query through it. It also has list pages for all of the different data types listed
in models, being mostly Locations and Impacts for now. This allows the user to see what all of their options are for searches. The project is currently a little limited
in terms of its conveniently available locations, but will expand to be fully autonomous in the future.
