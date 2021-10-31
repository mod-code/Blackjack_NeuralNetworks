import random
from random import shuffle
from time import sleep
from datetime import datetime
import math
import numpy as np
import pickle


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
		# print('')
		# print(f'{self.color}{self.name} gets a card:', card)
		self.hand.append(card)
		value = card.split(' ')[0]
		# print('Value:', value)
		if value not in 'JQKA':
			self.score += int(value)
		elif value in 'JQK':
			self.score += 10
		else:
			self.score += 1
			self.score_alt = self.score + 10
			self.score_variants += 1
		# self.info()

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


class LayerNetwork:
	def __init__(self, n_inputs, n_neurons):
		self.weights = 0.10 * np.random.randn(n_inputs, n_neurons)
		self.biases = 0.10 * np.random.randn(1, n_neurons)

	def forward(self, inputs):
		self.output = np.dot(inputs, self.weights) + self.biases


class NeuralNetwork:
	def __init__(self, n_input_neu, n_hidden_neu, n_output_neu):
		self.layer_h1 = LayerNetwork(n_input_neu, n_hidden_neu)
		self.layer_h2 = LayerNetwork(n_hidden_neu, n_hidden_neu)
		self.layer_out = LayerNetwork(n_hidden_neu, n_output_neu)
		self.layers = [self.layer_h1, self.layer_h2, self.layer_out]

	def calculate(self, x):
		self.layer_h1.forward(x)
		self.layer_h2.forward(self.layer_h1.output)
		self.layer_out.forward(self.layer_h2.output)
		for output in self.layer_out.output:
			if output == 0:
				return 0
			else:
				result = math.tanh(output/5) * 2
				# print(f'RESULT: {result}')   # info
				return result  # Output: <-2, 2>

	@staticmethod
	def check_error(count, result):   # count: <-10, 10>; result <-1; 0; 1>
		error = math.fabs((count/10 - result)/2)
		print(f'Count: {count}, Result: {result}, Error: {error}')   # info
		return error    # error: <0, 1>

	@staticmethod
	def acceleration(value):
		return math.tanh(value/5)   # <-1, 1>

	def teach(self, error):
		if error:
			for i in range(10):
				for j in range(10):
					new_value = error * random.uniform(-5, 5) + self.layer_h1.weights[i][j]
					self.layer_h1.weights[i][j] = self.acceleration(new_value)
			for i in range(10):
				for j in range(10):
					new_value = error * random.uniform(-5, 5) + self.layer_h2.weights[i][j]
					self.layer_h2.weights[i][j] = self.acceleration(new_value)
			for i in range(10):
				new_value = error * random.uniform(-5, 5) + self.layer_out.weights[i][0]
				self.layer_out.weights[i][0] = self.acceleration(new_value)
				new_value = error * random.uniform(-5, 5) + self.layer_out.biases[0][0]
				self.layer_out.biases[0][0] = self.acceleration(new_value)

			for layer in self.layers:
				for biases in layer.biases:
					for bias in biases:
						new_value = error * random.uniform(-5, 5) + bias
						bias = self.acceleration(new_value)

	'''
		def teach_old1(self, error):
			for layer in self.layers:
				for all_weights in layer.weights:
					for weight_set in all_weights:
						for weight in weight_set:
							weight += error * random.uniform(-1, 1)
				for biases in layer.biases:
					biases += error * random.uniform(-1, 1)
					
		def teach_old2(self, error):
			for layer in self.layers:
				for weights, biases in zip(layer.weights, layer.biases):
					for w, b in zip(weights, biases):
						ran1 = error * random.uniform(-1, 1)
						w += ran1
						ran2 = error * random.uniform(-1, 1)
						print('===RAN2: B+', ran2)
						print(b)
						b += ran2
						print(b)
	'''

	def save_network(self):
		f = open(f'neural_network.txt', 'w')
		f.write(f'H1:\n')
		f.write(f'W:{self.layer_h1.weights}\n')
		f.write(f'B:{self.layer_h1.biases}\n')
		f.write(f'\n')
		f.write(f'H2:\n')
		f.write(f'W:{self.layer_h2.weights}\n')
		f.write(f'B:{self.layer_h2.biases}\n')
		f.write(f'\n')
		f.write(f'OUT:\n')
		f.write(f'W:{self.layer_out.weights}\n')
		f.write(f'B:{self.layer_out.biases}\n')
		f.close()


class Blackjack:
	def __init__(self, nr_of_decks, money_pool, nr_of_players):
		deck = Deck(nr_of_decks)
		deck.shuffle_deck()
		self.nr_of_decks = nr_of_decks
		self.deck = deck
		self.nr_of_decks = nr_of_decks
		self.money_pool = money_pool
		self.nr_of_players = nr_of_players
		# Statistics:
		self.card_nr = 0
		self.house_blackjacks = 0
		self.house_busts = 0
		self.ai_count = 0
		self.ai_mode = ''
		self.ai_counting_on = False
		try:
			self.NN = pickle.load(open('neural_network.dat', 'rb'))
		except:
			self.NN = NeuralNetwork(10, 10, 1)

	def check_card_call(self, card):
		X = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		if card not in 'JQKA':
			X[int(card) - 2] = 1
			count_value = self.NN.calculate(X)
			return count_value
		elif card in 'JQK':
			X[8] = 1
			count_value = self.NN.calculate(X)
			return count_value
		elif card in 'A':
			X[9] = 1
			count_value = self.NN.calculate(X)
			return count_value

	def info(self):
		if self.nr_of_players == 1:
			print('Game for 1 player.')
		else:
			print(f'Game for {self.nr_of_players} players.')
		print(f'{len(self.deck.cards)} cards in the deck.')
		print(f'Starting money pool: ${self.money_pool}\n')

	def next_card(self):
		try:
			card = self.deck.cards[self.card_nr]
			self.card_nr += 1
			return card
		except IndexError:
			deck = Deck(self.nr_of_decks)
			deck.shuffle_deck()
			self.deck = deck
			self.card_nr = 0
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

	@staticmethod
	def ai_define_unit(true_roll):
		print(f'TRUE_ROLL: {true_roll}')  # info
		# 12 unit spread
		# 1-[-10/9] 2-[-8/7] 3-[-6/5] 4-[-4/3] 5-[-2/1] 6-[0] 7-[1/2] 8-[3/4] 9-[2/4] 10-[4/6] 11-[6/8] 12-[8/10]
		if true_roll <= -8:
			return 1
		elif -8 < true_roll <= -6:
			return 2
		elif -6 < true_roll <= -4:
			return 3
		elif -4 < true_roll <= -3:
			return 4
		elif -3 < true_roll <= -1:
			return 5
		elif -1 < true_roll <= 0:
			return 6
		elif 0 < true_roll <= 1:
			return 7
		elif 1 < true_roll <= 2:
			return 8
		elif 2 < true_roll <= 4:
			return 9
		elif 4 < true_roll <= 6:
			return 10
		elif 6 < true_roll <= 8:
			return 11
		elif 8 < true_roll:
			return 12

	def ai_decision(self, ai, house, true_count):
		# print(f'Variants: {ai.score_variants}')  # info

		if ai.score_variants == 1:  # HARD TOTALS

			if self.can_split(ai):  # PAIRS (CAN SPLIT)
				# print(f'CAN SPLIT, {ai.score}/{house.score}')  # info

				if ai.score == 2 or ai.score == 16:   # TWO ACES or 16
					return 3    # SPLIT
				elif ai.score <= 18:
					if 2 <= house.score <= 6 or 8 <= house.score <= 9:
						return 3    # SPLIT
				elif ai.score == 14 and 2 <= house.score <= 7:
					return 3    # SPLIT
				elif ai.score == 12 and 2 <= house.score <= 6:
					return 3    # SPLIT
				elif ai.score == 8 and 5 <= house.score <= 6:
					return 3    # SPLIT
				elif ai.score == 6 and 2 <= house.score <= 7:
					return 3    # SPLIT
				elif ai.score == 4 and 2 <= house.score <= 7:
					return 3    # SPLIT

			# print(f'NO SPLIT, {ai.score}/{house.score}')  # info

			if ai.score > 16:
				return 0    # STAND
			elif 13 <= ai.score <= 16:
				if 2 <= house.score <= 6:
					return 0  # STAND
				elif ai.score == 16:
					if house.score == 9 or house.score == 10 or house.score == 1:
						return 4  # SURRENDER
					else:
						return 1    # HIT
				elif ai.score == 15 and house.score == 10:
					return 4  # SURRENDER
				else:
					return 1    # HIT
			elif ai.score == 12:
				if 4 <= house.score <= 6:
					return 0  # STAND
				else:
					return 1  # HIT
			elif ai.score == 11:
				return 2    # DOUBLE
			elif ai.score == 10:
				if 2 <= house.score <= 9:
					return 2    # DOUBLE
				else:
					return 1  # HIT
			elif ai.score == 9:
				if 3 <= house.score <= 6:
					return 2    # DOUBLE
				else:
					return 1  # HIT
			elif ai.score < 9:
				return 1  # HIT

		elif ai.score_variants == 2:  # SOFT TOTALS (ONE ACE)
			# print(f'ONE ACE, {ai.score}/{house.score}')  # info
			if ai.score > 9:
				return 0    # STAND
			elif ai.score == 9:
				if house.score == 6:
					if true_count > 0:
						return 2    # DOUBLE
					else:
						return 0    # STAND
				else:
					return 0    # STAND
			elif ai.score == 8:
				if 2 <= house.score <= 6:
					if true_count > 0:
						return 2    # DOUBLE
					else:
						return 0    # STAND
				elif house.score >= 9:
					return 1    # HIT
				else:
					return 0  # STAND
			elif ai.score == 7:
				if 3 <= house.score <= 6:
					return 2    # DOUBLE
				else:
					return 1    # HIT
			elif ai.score == 5 or ai.score == 6:
				if 4 <= house.score <= 6:
					return 2    # DOUBLE
				else:
					return 1    # HIT
			elif ai.score == 4 or ai.score == 3:
				if 5 <= house.score <= 6:
					return 2    # DOUBLE
				else:
					return 1    # HIT

		elif ai.score_variants == 3:  # DOUBLE ACES
			return 3    # SPLIT

		else:
			print('Decision error')

		#  return 0    # STAND
		#  return 1    # HIT
		#  return 2    # DOUBLE
		#  return 3    # SPLIT
		#  return 4    # SURRENDER

	def ai_count_func(self, entity):  # L - Hi-Lo, K - KO, O - Omega II, 7 - Red 7, H - Halves, Z - Zen Count
		count = 0
		card_value = entity.hand[-1].split(' ')[0]  # COUNT LAST CARD FROM HAND

		if self.ai_mode in 'TU':  # NEURAL NETWORK AI
			X = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			if card_value not in 'JQKA':
				X[int(card_value)-2] = 1
				count_value = self.NN.calculate(X)
				# print('>>CALC:', count_value)      # info
				return count_value
			elif card_value in 'JQK':
				X[8] = 1
				count_value = self.NN.calculate(X)
				# print('>>CALC:', count_value)      # info
				return count_value
			elif card_value in 'A':
				X[9] = 1
				count_value = self.NN.calculate(X)
				# print('>>CALC:', count_value)      # info
				return count_value

		elif self.ai_mode == 'L':  # Hi-Lo
			if card_value not in 'JQKA':
				if int(card_value) <= 6:
					return 1
				elif 6 < int(card_value) <= 9:
					return 0
				elif int(card_value) == 10:
					return -1
			elif card_value in 'JQKA':
				return -1

		elif self.ai_mode == 'K':  # KO*
			if card_value not in 'JQKA':
				if int(card_value) <= 7:
					return 1
				elif 7 < int(card_value) <= 8:
					return 0
				elif 8 < int(card_value) <= 10:
					return -1
			elif card_value in 'JQKA':
				return -1

		elif self.ai_mode == 'O':  # Omega II
			if card_value not in 'JQKA':
				if int(card_value) <= 3 or int(card_value) == 7:
					return 1
				elif 3 < int(card_value) <= 6:
					return 2
				elif int(card_value) == 8:
					return 0
				elif int(card_value) == 9:
					return -1
				elif int(card_value) == 10:
					return -2
			elif card_value in 'JQK':
				return -2
			elif card_value in 'A':
				return 0

		elif self.ai_mode == '7':  # Red 7
			if card_value not in 'JQKA':
				if int(card_value) <= 6:
					return 1
				elif int(card_value) == 7:
					return 0.5
				elif 7 < int(card_value) <= 9:
					return 0
				elif int(card_value) == 10:
					return -1
			elif card_value in 'JQK':
				return -1
			elif card_value in 'A':
				return -1.5

		elif self.ai_mode == 'H':  # Halves
			if card_value not in 'JQKA':
				if int(card_value) == 2 or int(card_value) == 7:
					return 0.5
				elif 2 < int(card_value) <= 4 or int(card_value) == 6:
					return 1
				elif int(card_value) == 5:
					return 1.5
				elif int(card_value) == 8:
					return 0
				elif int(card_value) == 9:
					return -0.5
				elif int(card_value) == 10:
					return -1
			elif card_value in 'JQKA':
				return -1

		elif self.ai_mode == 'Z':  # Zen Count
			if card_value not in 'JQKA':
				if int(card_value) <= 3 or int(card_value) == 7:
					return 1
				elif 3 < int(card_value) <= 6:
					return 2
				elif 7 < int(card_value) <= 9:
					return 0
				elif int(card_value) == 10:
					return -2
			elif card_value in 'JQK':
				return -2
			elif card_value in 'A':
				return -1

		elif self.ai_mode == 'X':  # test
			if card_value not in 'JQKA':
				if int(card_value) == 2:
					return 0.8586825
				elif int(card_value) == 3:
					return 1.0584007
				elif int(card_value) == 4:
					return 1.3148266
				elif int(card_value) == 5:
					return 1.3958523
				elif int(card_value) == 6:
					return 1.3423453
				elif int(card_value) == 7:
					return 0.6676482
				elif int(card_value) == 8:
					return 0.0240855
				elif int(card_value) == 9:
					return -0.4367939
				elif int(card_value) == 10:
					return -1.3561552
			elif card_value in 'JQK':
				return -1.3561552
			elif card_value in 'A':
				return -0.8004264

	def start_ai(self, mode, count_on_off):  # MAIN AI!
		self.ai_mode = mode  # Counting Mode
		self.ai_counting_on = count_on_off
		rounds = 1000

		h = House()
		ai = Player(self.money_pool, 'AI', Colors.magenta)
		self.ai_count = 0
		bet_spread = 12
		log_string = f'============ BLACKJACK AI LOG ============\n'
		log_string += f'1 Player, 2 Decks, Rounds: {rounds}, Mode: {self.ai_mode}\n'
		log_string += f'MoneyPool: {self.money_pool}, BetSpread: {bet_spread}' \
					f'\n====================================================\n'
		log_string += f'[AI True Count] || Current Bet / Current Money ' \
					f'\n====================================================\n'
		log_string_c = ''
		log_string_b = ''
		log_string_m = ''
		round_counter = 1
		while round_counter <= rounds:
			print(f'\ni: {round_counter}')
			log_string += f'\nR{round_counter}'
			try:
				h.clean()
				ai.clean()

				# print('ai betting...')  # info
				# AI BETTING

				if ai.money < 10:
					print(f'{ai.money}')
					log_string += f'\nOUT OF MONEY!'
					break

				money_unit = math.ceil(ai.money / 100)
				ai_true_count = self.ai_count / self.nr_of_decks
				if self.ai_counting_on:  # COUNTING == ON
					# print(f'ADU: {self.ai_define_unit(ai_true_count)}')  # info
					units = int(self.ai_define_unit(ai_true_count))
					ai.current_bet = money_unit * units
					log_string += f' c{int(ai_true_count)} b{ai.current_bet} m{ai.money} '
					log_string_c += f'{ai_true_count}\n'
					log_string_b += f'{ai.current_bet}\n'
					log_string_m += f'{ai.money}\n'
				else:  # COUNTING == OFF
					if self.ai_mode == 'R':  # RANDOM BET
						ai.current_bet = money_unit * random.randint(1, bet_spread)
						log_string += f' c0 b{ai.current_bet} m{ai.money} '
						log_string_c += f'0\n'
						log_string_b += f'{ai.current_bet}\n'
						log_string_m += f'{ai.money}\n'
					elif self.ai_mode == 'S':  # STATIC BET
						ai.current_bet = money_unit * 6
						log_string += f' c0 b{ai.current_bet} m{ai.money} '
						log_string_c += f'0\n'
						log_string_b += f'{ai.current_bet}\n'
						log_string_m += f'{ai.money}\n'

				if ai.current_bet > ai.highest_bet:
					ai.highest_bet = ai.current_bet

				# ================ ROUND STARTS ================
				# ======== CARDS GIVING AND AI COUNTING ========
				# print('cards giving...')  # info

				ai.give_card(self.next_card())
				if self.ai_counting_on:
					self.ai_count += self.ai_count_func(ai)

				h.give_card(self.next_card())
				if self.ai_counting_on:
					self.ai_count += self.ai_count_func(h)


				ai_victory = self.ai_play_round(ai, h)

				# =============== HOUSE TURN ===============
				# print('house turn...')  # info
				if ai_victory == 0:  # PLAY HOUSE
					while True:
						h.give_card(self.next_card())
						if self.ai_counting_on:
							self.ai_count += self.ai_count_func(h)
						if h.score == 21 or h.score_alt == 21:
							self.house_blackjacks += 1
							h.final_score = 21
							ai_victory = -3
							break
						elif h.score > 21:
							self.house_busts += 2
							h.final_score = h.score
							ai_victory = 2
							break

						elif h.score > 16 or h.score_alt > 16:
							if 0 < h.score_alt < 21:
								h.final_score = h.score_alt
							else:
								h.final_score = h.score
							break

				# print(f'AI_V: {ai_victory}')  # info
				# ============= CHECK SCORE ==============
				# print('checking score...')  # info
				if ai_victory == 0:
					if ai.final_score > h.final_score:
						ai_victory = 1
					elif ai.final_score < h.final_score:
						ai_victory = -1
					elif ai.final_score == h.final_score:
						ai_victory = 0

				# print(f'AI_V: {ai_victory} -- {ai.final_score}/{h.final_score}')  # info

				# ============== FINISH ROUND ==============
				# print('finish round...')  # info

				if ai_victory == 3:  # BLACKJACK
					ai.money += math.ceil(1.5 * ai.current_bet)
					log_string += 'rJ'  # J == Blackjack
					print('Blackjack')
				elif ai_victory == 2:  # HOUSE BUST
					ai.money += ai.current_bet
					log_string += 'rU'  # U == HOUSE BUST
					print('HOUSE BUST')
				elif ai_victory == 1:  # WIN
					ai.money += ai.current_bet
					log_string += 'rW'  # W == WIN
					print('WIN')
				elif ai_victory == 0:  # DRAW
					log_string += 'rD'  # D == DRAW
					print('DRAW')
				elif ai_victory == -1:  # LOSE
					ai.money -= ai.current_bet
					log_string += 'rL'  # L == LOSE
					print('LOSE')
				elif ai_victory == -2:  # BUST
					ai.money -= ai.current_bet
					log_string += 'rB'  # B == BUST
					print('BUST')
				elif ai_victory == -3:  # HOUSE BJ
					ai.money -= ai.current_bet
					log_string += 'rH'  # H == HOUSE BJ
					print('HOUSE BJ')
				elif ai_victory == -4:  # SURR
					ai.current_bet /= 2
					ai.money -= ai.current_bet
					log_string += 'rS'  # S == SURR
					print('SURRENDER')
				else:
					log_string += f'?{ai_victory}'  # ?
					print('ERROR')

				# ============== NETWORK LEARNING ==============
				if self.ai_counting_on == 2 or self.ai_mode in '7K':
					if self.ai_count > 20:
						self.ai_count = 20
					elif self.ai_count < -20:
						self.ai_count = -20

				if self.ai_counting_on == 2 and self.ai_mode == 'T':
					ai_true_count = self.ai_count / self.nr_of_decks
					if ai_victory < 0:
						result = -1
					elif ai_victory > 0:
						result = 1
					else:
						result = 0
					error = self.NN.check_error(ai_true_count, result)  # error: <0, 1>
					self.NN.teach(error)

				round_counter += 1

			except IndexError:
				print('Out of cards!')
				break

		self.NN.save_network()
		pickle.dump(self.NN, open('neural_network.dat', 'wb'))
		log_name = input('FILE NAME:\n')
		save_log(log_string, log_name, '')
		save_log(log_string_c, log_name,  '_C')
		save_log(log_string_b, log_name,  '_B')
		save_log(log_string_m, log_name,  '_M')

	def ai_play_round(self, ai, h):

		ai.give_card(self.next_card())
		if self.ai_counting_on:
			self.ai_count += self.ai_count_func(ai)

		ai_true_count = self.ai_count / self.nr_of_decks

		# ========= CHECKING BlackJacks + AI PLAYING =========
		# print('ai playing...')  # info

		ai_victory = 0
		while True:
			if ai.score == 21 or ai.score_alt == 21:  # BLACKJACK
				ai.final_score = 21
				ai_victory = 3
				break
			elif ai.score > 21:
				ai.final_score = ai.score
				ai_victory = -2
				break
			else:
				# print(f'ATC: {ai_true_count}')  # info
				decision = self.ai_decision(ai, h, ai_true_count)
				print(f'Decision: {decision}')  # info
				if decision == 0:  # STAY
					break
				elif decision == 1:  # HIT
					ai.give_card(self.next_card())
					if self.ai_counting_on:
						self.ai_count += self.ai_count_func(ai)
				elif decision == 2:  # DOUBLE
					ai.current_bet *= 2
					ai.give_card(self.next_card())
					break
				elif decision == 3:  # SPLIT
					ai.is_split = True
					card_1 = ai.hand[0]
					card_2 = ai.hand[1]
					bet = ai.current_bet
					ai.clean()
					ai.is_split = 1
					ai.current_bet = bet
					ai.give_card(card_1)
					self.ai_play_round(ai, h)
					ai.clean()
					ai.is_split = 2
					ai.current_bet = bet
					ai.give_card(card_2)
					self.ai_play_round(ai, h)
					ai.is_split = 3
					break
				elif decision == 4:  # SURRENDER
					ai_victory = -4
					break

		if ai.score_variants == 1:
			ai.final_score = ai.score
		else:
			if ai.score + 10 > 21:
				ai.final_score = ai.score
			else:
				ai.final_score = ai.score + 10

		#if not ai.is_split:
		#	ai.final_score = player_score
		#elif ai.is_split == 1:
		#	ai.final_score = player_score
		#elif ai.is_split == 2:
		#	ai.final_score += player_score*100

		return ai_victory

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

	def play_round(self, player):
		player.give_card(self.next_card())
		sleep(1)
		# self.check_score_alt(player)
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
				# self.check_score_alt(player)
				if player.score == 21 or player.score_alt == 21:
					print('BLACKJACK! YOU WIN!')
					ask = False
				elif player.score > 21:
					print('BUST! YOU LOSE!')
					ask = False

		# THE PLAYER SCORE:
		# self.check_score_alt(player)
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
			# self.check_score_alt(h)
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
				# self.check_score_alt(h)
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


def save_log(log_content, log_name, add):
	if log_name == '':
		log_name = create_log_name()
	f = open(f'logs/{log_name}{add}.txt', 'w')
	f.write(log_content)
	f.close()


if __name__ == '__main__':
	ai_on = input('AI_Mode?\n'
	              'R - Random, S - Static Bet\n'
	              'L - Hi-Lo, K - KO, O - Omega II, 7 - Red 7, H - Halves, Z - Zen Count\n'
	              'T - Train AI-Network, U - Use AI-Network\n'
	              'C - Check Network Count Value\n'
	              'Anything else - Player game\n')
	if ai_on in 'RSLKO7HZTUX':
		if ai_on in 'RS':
			ai_count_on_off = 0
		elif ai_on in 'RSLKO7HZ':
			ai_count_on_off = 1
		else:
			ai_count_on_off = 2
		print('STARTING AI')
		game0 = Blackjack(2, 10000, 1)  # 2 DECKS, 10 000 credits, 1 PLAYER
		game0.start_ai(ai_on, ai_count_on_off)
	elif ai_on == 'C':
		game0 = Blackjack(2, 10000, 1)
		for i in range(2, 11):
			print(f'Value for card {i}:', Blackjack.check_card_call(game0, str(i)))
		print(f'Value for card A:', Blackjack.check_card_call(game0, 'A'))
	else:
		print('STARTING NOT AI')
		print(f'\n{Colors.red}=======SETTING=PHASE=======')
		# Deck size
		decks_amount = ask_deck_size()
		# Money pool
		money = ask_money_pool()
		# Number of players
		players = ask_number_players()

		game1 = Blackjack(decks_amount, money, players)
		game1.start_game()
