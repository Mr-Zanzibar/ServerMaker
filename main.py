# my biggest project
import json
import os
import pymysql
import string
import random
import shutil
import subprocess
import errno
import shlex
from flask import Flask, request, session
from flask_session import Session


app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super secret key'

Session(app)

connection = pymysql.connect(host='127.0.0.1', user='root', password='', db='app')


# for facebook and google login
@app.route('/session', methods=['POST'])
def session_route():
	print('[*] Got a message from client on route session !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')


# set data there.. form db to global arrays
@app.route('/session/start', methods=['POST'])
def session_start_route():
	print('[*] Got a message from client on route session/start !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	# user default data

	# user sent data #
	email_form = request.form['email']
	password_form = request.form['password']
	language_form = request.form['language']

	session['language'] = language_form
	session['email'] = email_form

	if 'email' not in session:
		return

	# get data from database if exists
	try:
		with connection.cursor() as cursor:
			if email_form != '' or password_form != '':

				cursor.execute("SELECT password FROM userdata WHERE email=" + "'" + email_form + "'")
				connection.commit()
				password_saved = cursor.fetchone()

				if password_saved is None:
					print('empty password')
					return
				else:
					print('password on database: ' + password_saved[0])

					# login system
					if password_saved[0] == password_form:
						print('right password, logged in as: ' + session['email'])

						# servers
						cursor.execute("SELECT servers FROM userdata WHERE email=" + "'" + email_form + "'")
						connection.commit()
						servers_data = cursor.fetchone()
						if servers_data[0] is not "[]":
							session['servers'] = json.loads(servers_data[0])
							print(session['servers'])
						else:
							session['servers'] = []

						cursor.execute("SELECT domains FROM userdata WHERE email=" + "'" + email_form + "'")
						connection.commit()
						domains_data = cursor.fetchone()
						if domains_data[0] is not "[]":
							session['domains'] = json.loads(domains_data[0])
						else:
							session['domains'] = []

						# donations
						cursor.execute("SELECT donations FROM userdata WHERE email=" + "'" + email_form + "'")
						connection.commit()
						donations_data = cursor.fetchone()
						if donations_data[0] is not "[]":
							session['donations'] = json.loads(donations_data[0])
						else:
							session['donations'] = []

						# credits
						cursor.execute("SELECT credits FROM userdata WHERE email=" + "'" + email_form + "'")
						connection.commit()
						credits_data = cursor.fetchone()
						session['credits'] = json.loads(credits_data[0])
						print(session['credits'])

						# referCode
						cursor.execute("SELECT referCode FROM userdata WHERE email=" + "'" + email_form + "'")
						connection.commit()
						referral_data = cursor.fetchone()
						session['referCode'] = referral_data[0]

						# get this data from the database
						data = {
							'session_key': None,
							'credits': session['credits']['credits'],
							'daily_usage': session['credits']['creditUsage'],
							'refer_code': 'a refer'
						}

						data_obj = [data]
						return json.dumps(data_obj)
					else:
						print('wrong email or password')
						# return
			else:
				print('empty mail or password')
				# return
	finally:
		if email_form != '' or password_form != '':
			# connection.close()
			print('servers saved')

	# i dont have to return them, it is sent to the server.. from app
	# return 'type=2&access_token=atoken&device_key=devicename' FACEBOOK LOGIN
	# 'type=3&access_token=acesstokenchangehere&device_key=devicename&id_token=unknownidtoken' GOOGLE LOGIN


# server stuff #

@app.route('/servers/list', methods=['GET'])
def servers_list_route():
	print('[*] Got a message from client on route servers/list !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	server_list = []

	if 'servers' in session:
		for server in session['servers']:
			server_list.append(server)

	if 'email' not in session:
		return

	print(session['email'])

	try:
		with connection.cursor() as cursor:

			if session['email'] is not None:
				sql = "UPDATE userdata SET servers = ('" + json.dumps(session['servers']) + "') WHERE email=" + "'" + session['email'] + "'"
				cursor.execute(sql)
				connection.commit()
			else:
				if session['email'] is None:
					print('mail error: password is null')
	finally:
		if session['email'] is not None:
			# connection.close()
			print('servers saved')

	return json.dumps(server_list)


@app.route('/servers/backup/list/<string:server_id>', methods=['GET'])
def servers_backup_list_route(server_id):
	print('[*] Got a message from client on route servers/backups/list !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	rollbacks_list = []

	return json.dumps(rollbacks_list)


@app.route('/servers/resetdata', methods=['POST'])
def servers_resetdata_route():
	print('[*] Got a message from client on route servers/resetdata !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	return '', 204


@app.route('/servers/delete', methods=['POST'])
def servers_delete_route():
	print('[*] Got a message from client on route servers/delete !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	for server in session['servers']:
		if request.form['server_id'] in server['id']:
			session['servers'].remove(server)

	return '', 204  # nothing to send, just run script


@app.route('/servers/versions', methods=['GET'])
def servers_versions_route():
	print('[*] Got a message from client on route servers/versions !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	versions = {
		'versions': ['1.0.9', '1.9.1']
	}

	# global versions

	versions_obj = [versions]

	return json.dumps(versions_obj)


# it return version, new version and server_id, the server id
@app.route('/servers/game/version', methods=['POST'])
def servers_game_version_route():
	print('[*] Got a message from client on route servers/versions !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	return '', 204


@app.route('/servers/gamemode/change', methods=['POST'])
def servers_gamemode_change_route():
	print('[*] Got a message from client on route servers/gamemode/change !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	for server in session['servers']:
		if server['id'] == request.form['server_id']:
			if server['gameMode'] != request.form['mode']:
				server['gameMode'] = request.form['mode']

	return '', 204

@app.route('/servers/donations/logs', methods=['GET'])
def servers_donations_log_route():
	print('[*] Got a message from client on route servers/donationslog !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	# donation1 = {}
	# donation1['credits'] = 200
	# donation2 = {}
	# donation2['credits'] = 200
	# arr = [donation1, donation2]

	donation_log = []

	for donation in session['donations']:
		donation_log.append(donation)

	return json.dumps(donation_log)


# change map type, it return server_id and mapType (standard = 0, flat 1)
@app.route('/servers/maps/type', methods=['POST'])
def servers_maps_type_route():
	print('[*] Got a message from client on route servers/maps/type !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	return '', 204


# state on server deploy
@app.route('/servers/deploymentstate', methods=['GET'])
def server_deployment_state_route():
	print('[*] Got a message from client on route servers/deploymentstate !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


# it returns a id and a server_id.. all undefined
@app.route('/servers/donations/message/enable', methods=['POST'])
def servers_donations_message_route():
	print('[*] Got a message from client on route servers/donations/message/enable !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204

@app.route('/servers/language/set', methods=['POST'])
def servers_language_set_route():
	print('[*] Got a message from client on route servers/language/set !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	for server in session['servers']:
		if server['id'] == request.form['server_id']:
			if server['language'] != request.form['language']:
				server['language'] = request.form['language']
	return 'done'


# it returns motd = motd to set, ip = server ip, port = server port, server_id = server id
@app.route('/servers/motd/set', methods=['POST'])
def servers_motd_set_route():
	print('[*] Got a message from client on route servers/motd/set !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


# after admindata there is server name.. idk how to add them from app maybe i have idea
@app.route('/servers/admindata/<string:server_id>', methods=['GET'])
def servers_admindata_servername_route(server_id):
	print('[*] Got a message from client on route servers/admindata/servername !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	# server_Id = request.form['server_Id']
	return '', 204


# it returns ip = ip of server, port = server port, name = server name, server_id = server id
@app.route('/servers/op/add', methods=['POST'])
def servers_op_add_route():
	print('[*] Got a message from client on route servers/op/add !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


# it return slots = int of slots, server_id = destination server
@app.route('/servers/slots', methods=['POST'])
def servers_slots_route():
	print('[*] Got a message from client on route servers/slots !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204
	# need to return current slots


@app.route('/servers/maps', methods=['GET'])
def servers_map_route():
	print('[*] Got a message from client on route servers/maps !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


# it return server_id
@app.route('/servers/console/reset', methods=['POST'])
def servers_console_reset_route():
	print('[*] Got a message from client on route servers/console/reset !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


# servers plugins #


# it return server_id = server id or name
@app.route('/servers/plugins/pushlogin/enable', methods=['POST'])
def servers_plugin_pushlogin_enable_route():
	print('[*] Got a message from client on route servers/plugins/pushlogin/enable !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


# it return server_id
@app.route('/servers/plugins/pushlogin/disable', methods=['POST'])
def servers_plugin_pushlogin_disable_route():
	print('[*] Got a message from client on route servers/plugins/pushlogin/disable !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


# it return id and server_id
@app.route('/servers/plugins/pushlogin/reset', methods=['POST'])
def servers_plugin_pushlogin_reset_route():
	print('[*] Got a message from client on route servers/plugins/pushlogin/reset !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


# it returns server_id and featureId = int
@app.route('/servers/plugins/purchase', methods=['POST'])
def servers_plugin_purchase_route():
	print('[*] Got a message from client on route servers/purchase !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	return '', 204


# it return server_id
@app.route('/servers/plugins/factions/enable', methods=['POST'])
def servers_plugin_factions_enable_route():
	print('[*] Got a message from client on route servers/plugins/factions/enable !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


@app.route('/servers/plugins/factions/disable', methods=['POST'])
def servers_plugin_factions_disable_route():
	print('[*] Got a message from client on route servers/plugins/factions/disable !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


@app.route('/v2/servers/name', methods=['POST'])
def v2_servers_name_route():
	print('[*] Got a message from client on route v2/servers/name !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	for server in session['servers']:
		if server['id'] == request.form['server_id']:
			if server['serverName'] != request.form['name']:
				server['serverName'] = request.form['name']
				return '', 204 
			else:
				return 
		else:
			return  # idk how to return error if server bugs lmao


@app.route('/v2/servers/create', methods=['POST'])
def v2_servers_create_route():
	print('[*] Got a message from client on route v2/servers/create !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	# GET a random url from freenom, and set the url name without .tk as server name
	# data_send = {}
	# data_send['forward_url'] = 'forward_url=<151.49.142.173>&email=<erryjet@gmail.com>&password=<0a7617d9>'
	# domain = requests.post('https://api.freenom.com/v2/domain/register.xml', json=data_send['forward_url'])
	# print('response from server:', domain.text)

	if 'servers' not in session:
		session['servers'] = []

	domain = randomString(5)

	base_url = 'https://api.freenom.com/v2/domain/register.xml'
	to_shorten = '151.49.142.173'
	params = {'forward_url': to_shorten,
				'email': 'Cuda@gmail.com',
				'password': 'MrCuda'}

	# r = requests.post(base_url, params=params)

	# print('domain: ' + r.text)

	# Default server data #
	server = dict()
	server['host'] = domain + '.pesv.tk'
	server['motd'] = 'amotd'
	server['port'] = 19132
	server['id'] = request.form['server_name']
	server['slots'] = 5
	server['theUrl'] = ''
	server['version'] = '1.0.9'
	server['serverName'] = request.form['server_name']

	server['whitelisted'] = False
	server['customDomain'] = False
	server['gameMode'] = request.form['game_mode']
	server['mapType'] = 0  # 0 = standard, 1 = flat
	server['language'] = 'eng'
	server['donateMessage'] = False
	server['pvp'] = False
	server['alwaysDay'] = False
	server['redstone'] = 0
	server['nether'] = 0
	server['mobs'] = 0
	server['weather'] = 0
	server['userLogin'] = False
	server['spawnProtection'] = False
	server['landProtection'] = 0
	server['customRanks'] = False
	server['modifyRanks'] = 0
	server['serverStatus'] = 1  # 0 offline, 1 online

	# plugins data #
	server['economy'] = 0
	server['worldEdit'] = 0
	server['unlimitedWorld'] = 0
	server['factions'] = 0
	server['unbanItems'] = 0
	server['alwaysSpawn'] = 0
	server['playerKits'] = 0
	server['adminFun'] = 0
	server['pvpArena'] = 0
	server['statusSigns'] = 0
	server['itemDisplay'] = 0
	server['lightningStrike'] = 0
	server['vipSlots'] = 0
	server['chatFilter'] = 0
	server['resetMine'] = 0
	server['moreCommands'] = 0
	server['killRate'] = 0
	server['basicHud'] = 0
	server['iControlU'] = 0
	server['healthStats'] = 0
	server['slapper'] = 0
	server['serverLove'] = 0
	server['tap2do'] = 0
	server['chestLocker'] = 0
	server['chestShop'] = 0
	server['clearLagg'] = 0
	server['afkkick'] = 0
	server['invsee'] = 0
	server['snowballPearl'] = 0
	server['bloodfx'] = 0
	server['bounceBlocks'] = 0
	server['serverMail'] = 0
	server['timerBan'] = 0
	server['timerCreative'] = 0
	server['autoDoor'] = 0
	server['autoSmelt'] = 0
	server['walkTrail'] = 0
	server['jail'] = 0
	server['antiChatSpam'] = 0
	server['friends'] = 0
	server['netherChests'] = 0
	server['sitting'] = 0
	server['rainbow'] = 0
	server['serverChannels'] = 0
	server['plots'] = 0
	server['broadcast'] = 0
	server['consoleAccess'] = 0
	server['luckyblock'] = 0
	server['combatLogger'] = 0
	server['autoCommand'] = 0
	server['voteReward'] = 0
	server['keepInventory'] = 0
	server['customAlert'] = 0
	server['voidTeleport'] = 0
	server['dedicatedIp'] = 0
	server['voiceServer'] = 0
	server['serverForum'] = 0
	server['networkTransfer'] = 0
	server['skywars'] = 0
	server['pushOnLogin'] = 0
	server['skyblock'] = 0
	server['hungerGames'] = 0
	server['monsterHunt'] = 0
	server['chestRefill'] = 0
	server['crateKeys'] = 0
	server['customCommands'] = 0
	server['pets'] = 0
	server['customEvents'] = 0
	server['lastSeen'] = 0
	server['popups'] = 0
	server['lightningStick'] = 0
	server['blockLogger'] = 0
	server['noSleep'] = 0
	server['hideAndSeek'] = 0
	server['monsterArena'] = 0

	session['servers'].append(server)

	if not os.path.isdir(os.path.join('servers') + '/' + domain):
		# os.mkdir(os.path.join('servers') + '/' + domain)

		# Copy pmmp template to new created server
		src_files = os.path.join('templates') + '/' + server['version'] + '/'

		copy(src_files, os.path.join('servers') + '/' + domain + '/')
		#s = Screen(domain, True)
		#s.enable_logs()
		#print(list_screens())

	try:
		with connection.cursor() as cursor:

			if session['email'] is not None:
				sql = "UPDATE userdata SET servers = ('" + json.dumps(session['servers']) + "') WHERE email=" + "'" + session['email'] + "'"
				cursor.execute(sql)
				connection.commit()
			else:
				if session['email'] is None:
					print('mail error: password is null')
	finally:
		if session['email'] is not None:
			# connection.close()
			print('servers saved from create')

	# os. make folder name with random freedom

	return '', 204


def start_server(domain):
	process = subprocess.Popen("C:/Users/Enrico/PycharmProjects/untitled1/servers/" + domain + '/start.cmd',  shell=True, stdout=subprocess.PIPE)
	stdout = process.communicate()[0]
	print('STDOUT:{}'.format(stdout))


def run_command(command):
	process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
	while True:
		output = process.stdout.readline()
		if output == '' and process.poll() is not None:
			break
		if output:
			print(output.strip())
	rc = process.poll()
	return rc


def copy(src, dest):
	try:
		shutil.copytree(src, dest)
	except OSError as e:
		# If the error was caused because the source wasn't a directory
		if e.errno == errno.ENOTDIR:
			shutil.copy(src, dest)
		else:
			print('Directory not copied. Error: %s' % e)


# user stuff data #


# WORKING
@app.route('/user/credits', methods=['GET'])
def user_credits_route():
	print('[*] Got a message from client on route user/credits !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	if 'credits' not in session:
		return '', 204

	credits = session['credits']

	credits_obj = [credits]
	return json.dumps(credits_obj)


@app.route('/user/domains', methods=['GET'])
def user_domains_route():
	print('[*] Got a message from client on route user/domains !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	domain_list = []

	for domain in session['domains']:
		domain_list.append(domain)

	return json.dumps(domain_list)


# faq for each language.. emh yes
@app.route('/user/faq', methods=['GET'])
def user_faq_route():
	print('[*] Got a message from client on route user/faq !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	# print(language)
	# not sure
	domain = dict()
	domain['question'] = 'Question Here'
	domain['answer'] = 'Response Here'
	array = [domain]
	return json.dumps(array)


# it return serverId and domain to link
@app.route('/domains/link', methods=['POST'])
def user_domains_link_route():
	print('[*] Got a message from client on route /domains/link !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


@app.route('/user/device/create', methods=['POST'])
def user_device_create_route():
	print('[*] Got a message from client on route user/device/create !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	uuid = 'auuid'
	device = 'adevice'
	return 'uuid=' + uuid + '&device=' + device


@app.route('/user/password/set', methods=['POST'])
def user_password_set_route():
	print('[*] Got a message from client on route user/password/set !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	password = 'apassword'
	serverIdString = 'serverid'
	return 'password='+password+'&'+serverIdString


# it return credits = int amount, server_id = server name or id, ip = server ip
@app.route('/users/gift', methods=['POST'])
def user_gift_route():
	print('[*] Got a message from client on route users/gift !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
    
	return '', 204


# it returns a input that contains the mail
@app.route('/user/forgotten', methods=['POST'])
def user_forgotten_route():
	print('[*] Got a message from client on route user/forgotten !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


@app.route('/user/create', methods=['POST'])
def user_create_route():
	print('[*] Got a message from client on route user/create !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	# default values
	servers = []
	domains = []
	credits = {
		'creditUsage': 10,
		'credits': 100
	}
	donations = []

	try:
		with connection.cursor() as cursor:

			# Read a single record
			sql = "INSERT INTO userdata (email, password, device, referCode, donations, servers, domains, credits) VALUES ('" + request.form['email'] + "','" + request.form['password'] + "','" + request.form['device'] + "','" + request.form['referCode'] + "','" + json.dumps(donations) + "','" + json.dumps(servers) + "','" + json.dumps(domains) + "','" + json.dumps(credits) + "')"
			cursor.execute(sql)
			connection.commit()
	finally:
		# connection.close()
		print('data saved test json')
		return "Saved successfully."

# earnings #


# it returns server_id
@app.route('/earning/social/youtube', methods=['POST'])
def earning_social_youtube_route():
	print('[*] Got a message from client on route earning/social/youtube !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	response = [[False]]
	return json.dumps(response)


# it returns server_id
@app.route('/earning/social/<string:platform>', methods=['POST'])
def earning_social_facebook_route(platform):
	print('[*] Got a message from client on route earning/social/' + platform + ' !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	response = [[None]]
	return json.dumps(response)


@app.route('/user/key', methods=['POST'])
def user_key_route():
	print('[*] Got a message from client on route user/key !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')


# .com domain
# it returns ip = ip of server, port = port of server, domain = new domain, server_id = id of server
@app.route('/servers/domain/real', methods=['POST'])
def real_domain_route():
	print('[*] Got a message from client on route real domain !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')
	return '', 204


@app.route('/servers/domains/set', methods=['POST'])
def servers_domains_set_route():
	print('[*] Got a message from client on route servers/domains/set !')

	for key in request.form:
		print(f'{key}: {request.form[key]}')

	global servers
	for server in servers:
		if server['id'] == request.form['server_id']:
			if server['address'] != request.form['domain']:
				server['address'] = request.form['domain']

	return '', 204


def randomString(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))


if __name__ == '__main__':
	app.run(port=80, host='0.0.0.0', debug=False)
