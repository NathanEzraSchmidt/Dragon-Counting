import math
import pickle
##d_list = get_outcome_lists()[-2]

def choose(n, k):
    p = 1
    for i in range(k):
        p *= (n-i) / (i+1)
    return int(round(p))



def get_starting_hands():
    y = []
    for i in range(10):
        for j in range(10):
            for k in range(10):
                for h in range(10):
                    y.append([[i,j],[k,h]])
    return y

def get_player_completed_hands():
    a = get_starting_hands()
    y = []
    for i in a:
        x1 = sum(i[0]) % 10
        x2 = sum(i[1]) % 10
        if x1 > 7 or x2 > 7:
            y.append(i)
            continue
        if x1 < 6:
            z = i[:]
            for j in range(10):
                y.append([z[0]+[j], z[1]])
        else:
            y.append(i[:])
    return y

def get_banker_completed_hands():
    a = get_player_completed_hands()
##    print(len(a))
    y = []
    for i in a:
        x1 = sum(i[0]) % 10
        x2 = sum(i[1]) % 10

##        print(i, x1, x2)
        

        p = i[0]
        n = len(p)

        z = i[:]

        hit = False
        
        if (x1 > 7 and n == 2) or x2 > 7:
            y.append(z)
            continue
        if x2 < 3:
            hit = True
        if n == 2 and x2 < 6:
            hit = True
        elif n == 3:
            c = z[0][2]
            if x2 == 3:
                if c != 8:
                    hit = True
            if x2 == 4:
                if c in [2,3,4,5,6,7]:
                    hit = True
            if x2 == 5:
                if c in [4,5,6,7]:
                    hit = True
            if x2 == 6:
                if c in [6,7]:
                    hit = True
        if hit == False:
            y.append(z)
        else:
            for j in range(10):
                y.append([z[0], z[1]+[j]])
    return y

def get_results_lists():
    a = get_banker_completed_hands()
    player, banker, tie, panda, dragon = [], [], [], [], []

    for i in a:
        x1, x2 = sum(i[0])%10, sum(i[1])%10
        if x1 == x2:
            tie.append(i)
        elif x1 > x2:
            if len(i[0]) == 3 and x1 == 8:
                panda.append(i)
            else:
                player.append(i)
        elif x2 > x1:
            if len(i[1]) == 3 and x2 == 7:
                dragon.append(i)
            else:
                banker.append(i)
    return player, banker, tie, dragon, panda

def get_prob(player, d=[16*8] + [32]*9):
    s = sum(d)
    print(s)
    total = 0
    for i in player:
        d2 = d[:]
        s2 = s
        p = 1
        for j in i[0] + i[1]:
            p *= d2[j] / s2
            s2 -= 1
            d2[j] -= 1
        total += p
    return total

def get_probs():
    player, banker, tie, dragon, panda = get_results_lists()

    p = get_prob(player)
    b = get_prob(banker)
    t = get_prob(tie)
    d = get_prob(dragon)
    n = get_prob(panda)

    return p,b,t,d,n

def output_outcomes():
    player, banker, tie, dragon, panda = get_results_lists()
    n = player, banker, tie, dragon, panda
    names = 'player','banker', 'tie', 'dragon', 'panda'
    for i,j in zip(names, n):
        file = open(i+'.bin', 'wb')
        pickle.dump(j, file)
        file.close()

def get_outcome_lists():
    names = 'player','banker', 'tie', 'dragon', 'panda'
    y = []
    for i in names:
        file = open(i+'.bin', 'rb')
        a = pickle.load(file)
        y.append(a)
        file.close()
    return y

d_list = get_outcome_lists()[-2]

def dragon_freq(hand_num=40, m=20):
    p = 0.022533820860378088
    q = 1 - p
    y = []
    for i in range(m+1):
        x = choose(hand_num, i)
        y.append(round(math.pow(q, hand_num-i)*x*pow(p, i),6))
    y2 = list(reversed(y))
    z = [sum(y2[:i]) for i in range(1,len(y2))]
    return y, [round(i,6) for i in z]

def get_prob_from_groups(dragon_list=[], groups=[7*32, 4*32, 2*32]):
    # tags = 0,1,2,3: 0; 4,5,6,7: -1; 8,9: +2;

    """
    returns the probability of the dragon occuring given the number of cards in each tagged group
    for example, if goups = [20,10,30], then with 20 cards in the group of neutral cards, 10 cards in the group of -1 cards,
    and 30 cards in the group of +2 cards, returns the probability of the dragon occuring

    """

    total = 0

    if dragon_list == []:
        dragon_list = d_list

    for i in dragon_list:
        x = i[0] + i[1]
        p = 1
        _groups = groups[:]
        _cards = [16*8] + [32]*9

        groups_original = [7*32, 4*32, 2*32]

        groups_sum = sum(_groups)
        cards_sum = sum(_cards) 

        for card in x:
            w = 0
            if card in [4,5,6,7]:
                w = 1
            elif card in [8,9]:
                w = 2
            if _groups[w] == 0 or groups_original[w] == 0:
                p = 0
                break
            group_prob = _groups[w] / groups_sum
            
            card_prob = _cards[card] / groups_original[w]
            z = _cards[card] / groups_sum

            _groups[w] -= 1
            groups_original[w] -=1
            groups_sum -= 1
            _cards[card] -= 1

            p *= group_prob * card_prob
            
        total += p
    return total


def get_groups_from_count(cards_left=400, count_spec=None):
    g = [224, 128, 64]

    d = {}

    # d[0] = [comb_totals, d_prob]

    for i in range(g[0]+1):
##        print(i)
        for j in range(g[1]+1):
            k = cards_left - i - j
            if k < 0 or k > 64:
                continue
##            print(i,j,k)
            count = -j + 2*k
            if type(count_spec) == int and count != count_spec:
                continue
            if not count in d:
                d[count] = [0,0,0]
            comb_total = choose(g[0], i) * choose(g[1], j) * choose(g[2], k)
            d[count][0] += comb_total
            prob = get_prob_from_groups([], [i,j,k])
            d[count][1] += comb_total * prob
    d2 = {}
    for i in d:
        d2[i] = round(d[i][1] / d[i][0], 6)
    y = []
    for i in d2:
        x = d2[i]
        y.append([-i,d2[i], round(x*40-1+x,6)])
    y = sorted(y, key=lambda f:f[0])
    return y

def get_groups_from_count(cards_left=400, count_spec=None):

    g = [224, 128, 64]

    d = {}

    for i in range(g[0]+1):
        for j in range(g[1]+1):
            k = cards_left - i - j
            if k < 0 or k > 64:
                continue
            count = -j + 2*k
            if type(count_spec) == int and count != count_spec:
                continue
            if not count in d:
                d[count] = [0,0,0]
            comb_total = choose(g[0], i) * choose(g[1], j) * choose(g[2], k)
            d[count][0] += comb_total
            prob = get_prob_from_groups([], [i,j,k])
            d[count][1] += comb_total * prob
    d2 = {}
    for i in d:
        d2[i] = [d[i][0], round(d[i][1] / d[i][0], 6)]
    y = []
    for i in d2:
        x = d2[i][1]
        y.append([-i, round(d2[i][0]/choose(416,cards_left), 6), round(x*40-1+x,6)])
    y = sorted(y, key=lambda f:f[0])
    return y

def output_counts():
    d = {}
    for i in range(1,13):
        print(i*26)
        d[i*26] = get_groups_from_count(cards_left=i*26)
    file = open("cards left.bin", 'wb')
    pickle.dump(d, file)
    file.close()
        

def analyze(k, pr=1):
    file = open('cards left.bin', 'rb')
    a = pickle.load(file)
    file.close()
##    k = [26, 52, 78, 104, 130, 156, 182, 208, 234, 260, 286, 312]
    a = a[k]
    freq = 0
    freq_ev = 0
    trigger = False
    for i in a:
        if i[-1] > 0:
            freq += i[1]
            freq_ev += i[1]*i[2]
            if not trigger:
                trigger = i[0]
    if pr:
        print("Cards left:", '\t', k)
        print("Tigger count:", '\t', trigger)
        print("Trigger true:", '\t', trigger*52/k)
        print("+EV frequency:", '\t',freq)
        print("Total EV:", '\t',freq_ev)
        print("Average +EV:", '\t',freq_ev/freq)
        print("#############")
    else:
        return trigger, trigger*52/k, freq, freq_ev, freq_ev/freq
def analyze_2():
    k = [26, 52, 78, 104, 130, 156, 182, 208, 234, 260, 286, 312]
    y = [analyze(i, pr=0) for i in k]
    z = [i[-2] for i in y]
    return z

def load_data():
    file = open('cards left.bin', 'rb')
    d = pickle.load(file)
    file.close()
    return d

def lengthen(s, n=8):
    while len(s) < n:
        s = s + ' '
        
    return s[:n]

def output_stats():
    d = load_data()
    k = list(d.keys())
    k = sorted(k)
    p = lengthen
    for i in k:
        file = open(str(i)+'.txt', 'w')
        file.write('cards unseen: ' + str(i) + '\n')
        file.write('running count	true count		frequency       EV\n')
        x = d[i]
        for line in x:
            if line[1]:
                tc = round(line[0]*52/i, 4)
                s = str(line[0]) + '\t\t' + lengthen(str(tc)) + '\t\t' + lengthen(str(line[1])) + '\t' + str(line[2]) + '\n'
                file.write(s)
        file.close()
##        return
                
            
    
                

            
            
        
    
        


    

