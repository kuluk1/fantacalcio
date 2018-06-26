from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, socketio
from flask_socketio import SocketIO, emit
from app.forms import LoginForm, RegisterForm, BidForm
from app.models import User, Player, Bid
import sys
import random
from sqlalchemy.sql import text
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = None
    bids = Bid.query.filter_by(active=1).order_by(Bid.time.desc())
    if current_user.is_anonymous:
        return render_template('index.html', title='Main screen', bids=bids)
    player_id = None
    max_bid=1
    if bids.count() > 0:
        player_id = bids[0].player_id
        max_bid = bids[0].bid + 1
    form = BidForm(bid=max_bid, user_id=current_user.get_id(), player_id=player_id)
    if form.validate_on_submit():
        latest_bid = Bid.query.filter_by(active=1).order_by(Bid.time.desc()).first()
        user = User.query.filter_by(id=form.user_id.data).first()
        if form.bid.data <= user.money:
            sql = """select CURRENT_TIMESTAMP from users""" #stupido hack
            result = db.engine.execute(sql)
            names = []
            for row in result:
                names.append(row[0])
            #flash('latest bid time ' + str(latest_bid.time) + '  current time ' + names[0])
            #datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')   2018-06-25 14:03:39
            datetime_object = datetime.strptime(names[0], '%Y-%m-%d %H:%M:%S')            
            #flash('differenza ' + str(datetime_object - latest_bid.time))
            if (datetime_object - latest_bid.time).total_seconds() < 31:
                if form.bid.data > latest_bid.bid:
                    #flash('ultimo user id ' + str(latest_bid.user_id) + '  il tuo invece ' + str(form.user_id.data) + '  la espressione ' + form.user_id.data != latest_bid.user_id)
                    if int(form.user_id.data) != int(latest_bid.user_id):
                        new_bid = Bid(bid=form.bid.data, active=1, user_id=form.user_id.data, player_id=form.player_id.data)
                        db.session.add(new_bid)
                        db.session.commit()
                        #flash('Good luck on your bid')
                        latest_bid = Bid.query.filter_by(active=1).order_by(Bid.time.desc()).first()
                        str_new_bid = r'<li class="list-group-item d-flex justify-content-between align-items-center">    <span> '+ str(latest_bid.player.name) + r' </span>    <span>'+ str(latest_bid.player.surname) + r'</span>    <span> '+ str(latest_bid.user.name) + r' </span>    <span class="badge badge-primary badge-pill">'+ str(latest_bid.bid) + r'</span>    <span>'+ str(latest_bid.time) + r'</span></li>'
                        socketio.emit('my_response', {'data': str_new_bid}, namespace='/test')
                    else:
                        flash('You are already the best bidder')
                else:
                    flash('You must offer more')
            else:
                flash('Too late :(')
        else:
            flash('Not enough money')
    return render_template('index.html', title='Main screen', bids=bids, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm(money=800)
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is not None:
            flash('Name alredy taken')
            return redirect(url_for('register'))
        user = User(name=form.name.data, money=form.money.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(name=username).first_or_404()
    return render_template('user.html', user=user)


@app.route('/team/<username>')
@login_required
def team(username):
    user = User.query.filter_by(name=username).first_or_404()
    players = Player.query.filter_by(assigned_user_id=user.id)
    return render_template('team.html', title=username + ' Team!', players=players, user=user)

@app.route('/not_assigned_players')
@login_required
def not_assigned_players():
    players = Player.query.filter(Player.assigned_user_id.is_(None))
    return filter_players('Not assigned', players)

@app.route('/assigned_players')
@login_required
def assigned_players():
    players = Player.query.filter(Player.assigned_user_id.isnot(None))
    return filter_players('Assigned', players)

@app.route('/all_player')
@login_required
def all_player():
    players = Player.query.all()
    return filter_players('All', players)


def filter_players(title, players):
    return render_template('all_players.html', filter_players=title, players=players)

@app.route('/new_player')
@login_required
def new_player():
    bids = Bid.query.filter_by(active=1)
    if bids.count() > 0:
        flash('Alredy an auction in action')
        return redirect(url_for('index'))
    players = Player.query.filter_by(assigned=0)
    rand = random.randrange(0, players.count()) 
    rand_player = players[rand]
    rand_player.assigned=1
    bid = Bid(bid=0, active=1, user_id=-1, player_id=rand_player.id)
    db.session.add(rand_player)
    db.session.add(bid)
    db.session.commit()
    str_new_bid = r'<li class="list-group-item d-flex justify-content-between align-items-center">    <span> '+ str(bid.player.name) + r' </span>    <span>'+ str(bid.player.surname) + r'</span>    <span> '+ str(bid.user.name) + r' </span>    <span class="badge badge-primary badge-pill">'+ str(bid.bid) + r'</span>    <span>'+ str(bid.time) + r'</span></li>'
    socketio.emit('new_player', {'data': str_new_bid}, namespace='/test')
    return redirect(url_for('index'))

@app.route('/close_auction')
@login_required
def new_acution():
    bid = Bid.query.filter_by(active=1).order_by(Bid.time.desc()).first()
    bids = Bid.query.filter_by(active=1)
    if bids.count() > 0:
        player = Player.query.filter_by(id=bid.player_id).first_or_404()
        player.assigned = 1
        if bid.bid > 0:
            player.assigned_user_id=bid.user_id
            player.assigned_value = bid.bid
            user = User.query.filter_by(id=bid.user_id).first()
            user.money -= bid.bid
            db.session.add(user)
            db.session.add(player)
            db.session.commit()
        for bbid in bids:
            bbid.active=0
            db.session.add(bbid)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/all_users')
@login_required
def all_users():
    users = User.query.all()
    return render_template('all_users.html', users=users)
