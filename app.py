#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask import abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import sys
from models import *
from models import db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database - DONE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
 
  # Check models.py 


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value

  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  results = Venue.query.distinct(Venue.city, Venue.state).all()
  city_state_data = {}
  for result in results:
    #city_state_data.add( (Venue.city, Venue.state) )
    city_state_data = {
    'city' : result.city,
    'state' : result.state} 
    venues = Venue.query.filter_by(city=result.city, state=result.state).all()
    add_venues = []
    for venue in venues:
      add_venues.append ({
          "id" : venue.id,
          "name" : venue.name,
          "num_upcoming_shows" : len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
        })
      city_state_data['venues'] = add_venues
      #data.append({
       # "city": result.city,
        #"state" : result.state,
        #"venuess" : add_venues
      #})
    data.append(city_state_data)
  return render_template('pages/venues.html', areas=data)
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
 
  data!=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '').strip()

    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    
    venues_list = []
    now = datetime.now()
    for venue in venues:
      venue_shows = Show.query.filter_by(venue_id=venue.id).all()
      num_upcoming_shows = 0
      for show in venue_shows:
        if show.start_time > now:
          num_upcoming_shows += 1


      venues_list.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows,
      })
    
    response = {
      "count": len(venues),
      "data": venues_list
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
# shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)

  past_shows = []
  past_shows_count = 0
  upcoming_shows = []
  upcoming_shows_count = 0
  now = datetime.now()
  for show in venue.shows:
    if show.start_time > now:
      upcoming_shows_count += 1
      upcoming_shows.append({
        "artist_id" : show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link" : show.artist.image_link,
        "start_time" : format_datetime(str(show.start_time))
      })

      if show.start_time < now:
        past_shows_count += 1
        past_shows.append({
        "artist_id" : show.artist_id,
        "artist_name" : show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time" : format_datetime(str(show.start_time))
      })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False
  try:
    if form.validate_on_submit():
      venue = Venue(name=form.name.data,
                      city=form.city.data,
                      state=form.state.data,
                      phone=form.phone.data,
                      address=form.address.data,
                      image_link=form.image_link.data,
                      genres=form.genres.data,
                      facebook_link=form.facebook_link.data,
                      seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data,
                      website_link=form.website_link.data)
      db.session.add(venue)
      # TODO: insert form data as a new Venue record in the db
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      for field, errors in form.errors.items():
          for error in errors:
            flash('Error in {}: {}'.format(getattr(form, field).label.text, error), 'error')
            abort(400)
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    error = False
    try:
      #Venue.query.filter_by(id=venue_id).delete()
      deleteVenue = Venue.query.get(venue_id)
      db.session.delete(deleteVenue)
      db.session.commit()
      print('Deleted')
      flash('Venue has been succesfully deleted')
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An Error occured. Venue could not be deleted.')
    finally:
      db.session.close()

    return redirect(url_for('index'))

  # TODO: Endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record.

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Data returned from querying the database
  data = db.session.query(Artist).order_by('id').all()
  return render_template('pages/artists.html', artists=data)

   
@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', "").strip()

  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  
  artist_list = []
  now = datetime.now() 
  for artist in artists:
    artist_shows = Show.query.filter_by(artist_id=artist.id).all()
    num_upcoming_shows = 0
    for show in artist_shows:
      if show.start_time > now:
        num_upcoming_shows += 1


    artist_list.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
  
  response = {
    "count": len(artists),
    "data": artist_list
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  
  past_shows = []
  past_shows_count = 0
  upcoming_shows = []
  upcoming_shows_count = 0
  now = datetime.now()
  for show in artist.shows:
    if show.start_time > now:
      upcoming_shows_count += 1
      upcoming_shows.append({
        "venue_id" : show.venue_id,
        "venue_name" : show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": format_datetime(str(show.start_time))
      })

      if show.start_time < now:
        past_shows_count += 1
        past_shows.append({
        "venue_id" : show.venue_id,
        "venue_name" : show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": format_datetime(str(show.start_time))
      })
  
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
  }
  return render_template('pages/show_artist.html', artist=data)

  
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
   # Populated form with fields from artist with ID <artist_id>
  form = ArtistForm(
    name = artist.name,
    city = artist.city,
    state = artist.state,
    phone = artist.phone,
    genres = artist.genres,
    image_link = artist.image_link,
    facebook_link = artist.facebook_link,
    website_link = artist.website_link,
    seeking_venue = artist.seeking_venue,
    seeking_description = artist.seeking_description
  )

  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

  
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Values from the form submitted used to update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  error = False
  try:
    if form.validate_on_submit():
      artist = Artist.query.get(artist_id)
      artist.name=form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.image_link=form.image_link.data
      artist.genres=form.genres.data
      artist.facebook_link=form.facebook_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data
      artist.website_link=form.website_link.data
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully Edited!')
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be Edited.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))  
  
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  # Populated form with values from venue with ID <venue_id>
  form = VenueForm(
    name = venue.name,
    city = venue.city,
    state = venue.state,
    phone = venue.phone,
    address = venue.address,
    genres = venue.genres,
    image_link = venue.image_link,
    facebook_link = venue.facebook_link,
    website_link = venue.website_link,
    seeking_talent = venue.seeking_talent,
    seeking_description = venue.seeking_description
  )
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Values from the form submitted used to update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  error = False
  try:
    if form.validate_on_submit():
      venue = Venue.query.get(venue_id)
      venue.name=form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.phone=form.phone.data
      venue.address=form.address.data
      venue.image_link=form.image_link.data
      venue.genres=form.genres.data
      venue.facebook_link=form.facebook_link.data
      venue.seeking_talent=form.seeking_talent.data
      venue.seeking_description=form.seeking_description.data
      venue.website_link=form.website_link.data
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully Edited!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be Edited.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

  
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  error=False
  try:
    if form.validate_on_submit():
      artist = Artist(name=form.name.data,
                      city=form.city.data,
                      state=form.state.data,
                      phone=form.phone.data,
                      image_link=form.image_link.data,
                      genres=form.genres.data,
                      facebook_link=form.facebook_link.data,
                      seeking_venue=form.seeking_venue.data,
                      seeking_description=form.seeking_description.data,
                      website_link=form.website_link.data)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        for field, errors in form.errors.items():
          for error in errors:
            flash('Error in {}: {}'.format(getattr(form, field).label.text, error), 'error')
            abort(400)
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  shows = Show.query.order_by(db.desc(Show.start_time))
  venue = Venue.query.all()
 # db.session.query(Show).order_by("id").all()
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  return render_template('pages/shows.html', shows=data)
  

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  error = False
  try:
    if form.validate_on_submit():
      create_show= Show(artist_id=form.artist_id.data,
                  venue_id=form.venue_id.data,
                  start_time=form.start_time.data)
      db.session.add(create_show)
      db.session.commit()
      flash('Show was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
