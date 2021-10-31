import re


def open_file(file_name):
    f = open(f'logs/{file_name}.txt', 'r')

    file_count = open(f'logs/{file_name}_C.txt', 'w')
    file_bet = open(f'logs/{file_name}_B.txt', 'w')
    file_money = open(f'logs/{file_name}_M.txt', 'w')

    cont_list = f.readlines()
    for line in cont_list:
        if line[0] == 'R':
            c = r'c[-+]?[0-9]*'
            b = r'b[0-9]*'
            m = r'm[0-9]*'
            count = re.search(c, line)
            bet = re.search(b, line)
            money = re.search(m, line)
            c_value = count.group()[1:]
            b_value = bet.group()[1:]
            m_value = money.group()[1:]
            print(c_value)
            print(b_value)
            print(m_value)
            file_count.write(f'{c_value}\n')
            file_bet.write(f'{b_value}\n')
            file_money.write(f'{m_value}\n')

    file_count.close()
    file_bet.close()
    file_money.close()
    f.close()


def main():
    file_name = input('Enter file name:\n')
    open_file(file_name)


main()
