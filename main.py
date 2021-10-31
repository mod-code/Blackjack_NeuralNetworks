from random import shuffle
from time import sleep
from datetime import datetime


class Colors:
	red = '\u001b[31m'
	green = '\u001b[32m'
	yellow = '\u001b[33m'
	blue = '\u001b[34m'
	magenta = '\u001b[35m'
	cyan = '\u001b[36m'
	white = '\u001b[0m'


class Deck:
	def __init__(self, nr):     # nr = the number of standard card decks in the deck
		self.cards = []
		deck_type = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
		deck_val = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
		for _ in range(nr):
			for t in deck_type:
				for v in deck_val:
					self.cards.append(v + ' ' + t)

	def __str__(self):
		for card in self.cards:
			print(card)
		print('Number of cards:', len(self.cards))

	def shuffle_deck(self):
		shuffle(self.cards)


class Entity:
	def __init__(self):
		self.score = 0
		self.score_alt = 0
		self.score_variants = 1
		self.final_score = 0
		self.hand = []
		self.name = 'Entity'
		self.color = Colors.white

	def info(self):
		print(f'{self.color}Current {self.name}\'s hand:\n', str(self.hand)[1:-1])
		if self.score_variants == 1:
			print(f'{self.name}\'s score: {self.score}')
		else:
			print(f'{self.name}\'s score:', end=' ')
			for i in range(self.score_variants):
				print(f'or {self.score + i * 10}', end=' ')
			print('')

	def give_card(self, card):
		print('')
		print(f'{self.color}{self.name} gets a card:', card)
		self.hand.append(card)
		value = card.split(' ')[0]
		# print('Value:', value)
		if value not in 'JQKA':
			self.score += int(value)
		elif value in 'JQK':
			self.score += 10
		else:
			self.score += 1
			self.score_variants += 1
		self.info()

	def clean(self):
		self.score = 0
		self.score_alt = 0
		self.score_variants = 1
		self.hand.clear()


class Player(Entity):
	def __init__(self, money_base, name, color):
		super().__init__()
		self.money = money_base
		self.name = name
		self.current_bet = 0
		self.is_split = False
		# STATISTICS:
		self.highest_bet = 0
		self.highest_money = money_base
		self.wins = 0
		self.loses = 0
		self.draws = 0
		self.busts = 0
		self.blackjacks = 0
		self.color = color


class House(Entity):
	def __init__(self):
		super().__init__()
		self.name = 'House'
		self.color = Colors.red


class Blackjack:
	def __init__(self, deck, money_pool, nr_of_players):
		self.deck = deck
		self.money_pool = money_pool
		self.nr_of_players = nr_of_players
		# Statistics:
		self.card_nr = 0
		self.house_blackjacks = 0
		self.house_busts = 0

	def info(self):
		if self.nr_of_players == 1:
			print('Game for 1 player.')
		else:
			print(f'Game for {self.nr_of_players} players.')
		print(f'{len(self.deck.cards)} cards in the deck.')
		print(f'Starting money pool: ${self.money_pool}\n')

	def next_card(self):
		card = self.deck.cards[self.card_nr]
		self.card_nr += 1
		return card

	@staticmethod
	def can_split(player):
		if not len(player.hand) == 2:
			return False
		v1 = player.hand[0].split(' ')[0]
		if v1 not in 'JQKA':
			v1 = int(v1)
		elif v1 in 'JQK':
			v1 = 10
		else:
			v1 = 11
		v2 = player.hand[1].split(' ')[0]
		if v2 not in 'JQKA':
			v2 = int(v2)
		elif v2 in 'JQK':
			v2 = 10
		else:
			v2 = 11
		if v1 == v2:
			return True
		else:
			return False

	@staticmethod
	def make_bet(p):
		bet = 0
		while True:
			try:
				bet = int(input(f'\nPlace your bet! Your current cash: ${p.money}\n...or bet 0 to leave.\n'))
				if bet == 0:
					print(f'You leave with ${p.money}!\nSee you next time!')
					break
			except ValueError:
				print('Sorry, I didn\'t understand that.')
				continue
			if not 0 < bet <= p.money:
				print('Inncorrect value!')
				continue
			else:
				break
		if bet == p.money:
			print('ALL IN!')
		print(f'Your bet is: ${bet}! GOOD LUCK!\n')
		return bet

	@staticmethod
	def translate_color(clr):
		if clr == 'G':
			return Colors.green
		elif clr == 'Y':
			return Colors.yellow
		elif clr == 'B':
			return Colors.blue
		elif clr == 'M':
			return Colors.magenta
		elif clr == 'C':
			return Colors.cyan
		elif clr == 'R':
			return Colors.red
		elif clr == 'W':
			return Colors.white

	def start_game(self):
		players_list = []
		dead_list = []
		for i in range(self.nr_of_players):
			print(f'{Colors.yellow}Please set the name of the player number', str(i+1))
			player_name = input('')
			print(f'{Colors.white}Please choose a text color for {player_name}:')
			print(f'{Colors.green}[G]reen{Colors.white}, {Colors.yellow}[Y]ellow{Colors.white}, {Colors.blue}[B]lue'
				f'{Colors.white}, {Colors.magenta}[M]agenta{Colors.white}, {Colors.cyan}[C]yan{Colors.white}')
			chosen_color = 'x'
			while chosen_color not in 'GYBMC':
				print('Select the color by typing the first letter of the color.')
				chosen_color = input('').upper()
			players_list.append(Player(self.money_pool, player_name, self.translate_color(chosen_color)))
		h = House()
		while self.card_nr < len(self.deck.cards) and players_list:
			try:
				h.clean()
				new_dead = 0
				print(f'\n{Colors.white}=======BETTING=======')
				for p in players_list:
					p.clean()
					print(f'{p.color}{p.name}\'s betting turn...')
					p.current_bet = self.make_bet(p)
					if p.current_bet == 0:
						self.game_over(p, 1)
						dead_list.append(p)
						new_dead = 1
					elif p.current_bet > p.highest_bet:
						p.highest_bet = p.current_bet
						p.highest_bet_player = p.name
				if new_dead == 1:
					for dead_player in dead_list:
						players_list.remove(dead_player)
				sleep(2)
				if players_list:
					print(f'\n{Colors.red}====ROUND=STARTS=====')
				for p in players_list:
					p.give_card(self.next_card())
					sleep(2)
				if players_list:
					h.give_card(self.next_card())
				else:
					break
				for p in players_list:
					sleep(1)
					print(f'\n{p.color}{p.name}\'s turn...')
					self.play_round(p)

				sleep(1)
				print(f'\n{Colors.red}===HOUSE\'S=TURN===')
				sleep(2)
				# HOUSE TURN
				self.play_house(h)

				sleep(2)
				# RESULTS
				self.results(players_list, h)

				sleep(1)
				for p in players_list:
					if p.money == 0:
						self.game_over(p, 0)
						players_list.remove(p)
			except IndexError:
				print('Could not finish the round. Out of cards!')
				break
		if not players_list:
			self.out_of(1, dead_list)
		else:
			self.out_of(0, dead_list)

	@staticmethod
	def check_score_alt(player):
		if player.score_variants > 1:
			player.score_alt = player.score + 10

	def play_round(self, player):
		player.give_card(self.next_card())
		sleep(1)
		self.check_score_alt(player)
		if player.score == 21 or player.score_alt == 21:
			print(f'BLACKJACK! {player.name} wins!')
		else:
			ask = True
			if 2 * player.current_bet > player.money:
				double = False
			else:
				double = True
			if self.can_split(player) and not player.is_split:
				split = True
			else:
				split = False
			while ask:
				print('What do you want to do?\n[HIT]\n[STAND]')
				if double:
					print('[DOUBLE]')
					if split and not player.is_split:
						print('[SPLIT]')
				action = input('').upper()
				if action == 'HIT':
					print('You have chosen to HIT!\n')
					player.give_card(self.next_card())
				elif action == 'STAND':
					print('You have chosen to STAND!\n')
					ask = False
				elif action == 'DOUBLE' and double:
					print('You have chosen to DOUBLE!\n')
					player.current_bet *= 2
					if player.current_bet > player.highest_bet:
						player.highest_bet = player.current_bet
					print(f'Your current bet is: ${player.current_bet}')
					if player.current_bet == player.money:
						print('A L L   I N !')
					player.give_card(self.next_card())
					ask = False
				elif action == 'SPLIT' and split:
					print('You have chosen to SPLIT!\n')
					card_1 = player.hand[0]
					card_2 = player.hand[1]
					bet = player.current_bet
					player.clean()
					player.is_split = 1
					player.current_bet = bet
					player.give_card(card_1)
					self.play_round(player)
					sleep(2)
					player.clean()
					player.is_split = 2
					player.current_bet = bet
					player.give_card(card_2)
					self.play_round(player)
					player.is_split = 3
					break
				self.check_score_alt(player)
				if player.score == 21 or player.score_alt == 21:
					print('BLACKJACK! YOU WIN!')
					ask = False
				elif player.score > 21:
					print('BUST! YOU LOSE!')
					ask = False

		# THE PLAYER SCORE:
		self.check_score_alt(player)
		if 0 < player.score_alt < 21:
			player_score = player.score_alt
		else:
			player_score = player.score
		if not player.is_split:
			player.final_score = player_score
		elif player.is_split == 1:
			player.final_score = player_score
		elif player.is_split == 2:
			player.final_score += player_score*100

	def play_house(self, h):
		while True:
			h.give_card(self.next_card())
			sleep(2)
			self.check_score_alt(h)
			if h.score == 21 or h.score_alt == 21:
				print('HOUSE BLACKJACK!')
				self.house_blackjacks += 1
				h.final_score = 21
				break
			elif h.score > 21:
				print('HOUSE BUSTS!')
				self.house_busts += 1
				h.final_score = h.score
				break

			elif h.score > 16:
				self.check_score_alt(h)
				if 0 < h.score_alt < 21:
					h.final_score = h.score_alt
				else:
					h.final_score = h.score
				break

	def results(self, players_list, h):
		print(f'\n{Colors.white}=======RESULTS======={Colors.red}')
		if h.final_score > 21:
			print(f'HOUSE BUSTED!')
		elif h.final_score == 21:
			print(f'HOUSE GOT BLACKJACK!')
		else:
			print(f'House scored {h.final_score}!')
		for p in players_list:
			if not p.is_split:
				self.check_score(p, h)
			else:
				p.is_split = False
				score = str(p.final_score)
				spl_score1 = score[0] + score[1]
				spl_score2 = score[2] + score[3]
				spl_score1 = int(spl_score1)
				spl_score2 = int(spl_score2)
				p.final_score = int(spl_score1)
				self.check_score(p, h)
				p.final_score = int(spl_score2)
				self.check_score(p, h)
		print('')
		for p in players_list:
			print(f'{p.color}{p.name} now has: ${p.money}!')

	@staticmethod
	def check_score(p, h):
		if p.final_score > 21:
			print(f'{p.color}{p.name} BUSTED and lost ${p.current_bet}!')
			p.loses += 1
			p.busts += 1
			p.money -= p.current_bet
		elif p.final_score == 21:
			print(f'{p.color}{p.name} GOT BLACKJACK and won ${p.current_bet}!')
			p.wins += 1
			p.blackjacks += 1
			p.money += p.current_bet
		elif p.final_score > h.final_score or h.final_score > 21:
			print(f'{p.color}{p.name} scored {p.final_score} and won ${p.current_bet}!')
			p.wins += 1
			p.money += p.current_bet
		elif p.final_score < h.final_score:
			print(f'{p.color}{p.name} scored {p.final_score} and lost ${p.current_bet}!')
			p.loses += 1
			p.money -= p.current_bet
		elif p.final_score == h.final_score:
			print(f'{p.color}{p.name} scored {p.final_score} and drew with the house!')
			p.draws += 1

		if p.money > p.highest_money:
			p.highest_money = p.money

	def out_of(self, cause, dead_list):
		print(f'{Colors.white}========================')
		if cause == 0:
			print('OUT OF CARDS! GAME OVER!')
		else:
			print('OUT OF PLAYERS! GAME OVER!')
		print('========================')
		print('Statistics:')
		print(f'Starting money pool: ${self.money_pool}')
		print(f'Cards played: {self.card_nr}')
		print(f'House Blackjacks: {self.house_blackjacks}')
		print(f'House Busts: {self.house_busts}')
		for p in dead_list:
			print(f'Player "{p.name}" ended up with ${p.money}.')
		print('========================')

	def game_over(self, player, cause):
		print('=========================================')
		if cause == 0:
			print(f'{player.name} is out of money!')
		if cause == 1:
			print(f'{player.name} leaves!')
		print('=========================================')
		print(f'Statistics for {player.name}:')
		print(f'Starting money pool: ${self.money_pool}')
		print(f'Cards played until now: {self.card_nr}')
		print(f'Final money score: ${player.money}')
		print(f'Highest money: ${player.highest_money}')
		print(f'Highest bet: ${player.highest_bet}')
		print(f'Wins: {player.wins}')
		print(f'Loses: {player.loses}')
		print(f'Draws: {player.draws}')
		print(f'Blackjacks: {player.blackjacks}')
		print(f'Busts: {player.busts}')
		print('')


def ask_deck_size():
	used_decks = 0
	while True:
		try:
			used_decks = int(input(f'\n{Colors.blue}How many decks do you want to play with? (Standard is 2)\n'))
		except ValueError:
			print('Sorry, I didn\'t understand that.')
			continue
		if not 0 < used_decks <= 50:
			print('Incorrect value!')
			continue
		else:
			break
	if used_decks == 1:
		print(f'You have chosen to use only 1 deck of cards.')
	else:
		print(f'You have chosen to use {used_decks} decks of cards.')
	return used_decks


def ask_money_pool():
	money_pool = 0
	while True:
		try:
			money_pool = int(input(f'\n{Colors.green}What should be the starting money pool?\n'))
		except ValueError:
			print('Sorry, I didn\'t understand that.')
			continue
		if not 0 < money_pool <= 1000000:
			print('Inncorrect value!')
			continue
		else:
			break
	print(f'The starting money pool is ${money_pool}')
	return money_pool


def ask_number_players():
	player_number = 1
	while True:
		try:
			player_number = int(input(f'\n{Colors.cyan}How many players want to play? (1-6)\n'))
		except ValueError:
			print('Sorry, I didn\'t understand that.')
			continue
		if not 0 < player_number <= 6:
			print('Inncorrect value!')
			continue
		else:
			break
	if player_number == 1:
		print(f'The game has been set to single-player.')
	else:
		print(f'The game has been set to {player_number} players.\n')
	return player_number


def create_log_name():
	full_date = str(datetime.now()).split()
	n_date = full_date[0]
	n_time = full_date[1].split('.')
	name = 'log_' + n_date.replace('-', '_') + '_' + n_time[0].replace(':', '-')
	return name


def save_log():
	log_name = create_log_name()
	f = open(f'{log_name}.txt', 'w')
	f.close()


def ai():
	deck = Deck(2)
	D.shuffle_deck()

	game0 = Blackjack(deck, 10000, 1)
	game0.start_game()


if __name__ == '__main__':
	ai_on = input('AI_Mode? 1 == YES\n')
	if ai_on == 1:
		ai()
	else:
		print(f'\n{Colors.red}=======SETTING=PHASE=======')
		# Deck size
		decks = ask_deck_size()
		D = Deck(decks)
		D.shuffle_deck()
		# Money pool
		money = ask_money_pool()
		# Number of players
		players = ask_number_players()

		game1 = Blackjack(D, money, players)
		game1.start_game()
