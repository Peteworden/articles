import numpy as np
import matplotlib.pyplot as plt

def print_qr(cells):
    N = len(cells[0])
    for i in range(N):
        line = ''
        for j in range(N):
            if cells[i, j] % 2 == 0:
                line += '□'
            else:
                line += '■'
        print(line)

def finder(i, j, cells):
    for m in range(j, j+7):
        for n in range(i, i+7):
            cells[m, n] = 3
    for m in range(j+1, j+6):
        for n in range(i+1, i+6):
            cells[m, n] = 2
    for m in range(j+2, j+5):
        for n in range(i+2, i+5):
            cells[m, n] = 3
    return cells

def timing(cells):
    N = len(cells[0])
    for i in range(7, N-7):
        if i % 2 == 0:
            cells[6, i] = 3
            cells[i, 6] = 3
        else:
            cells[6, i] = 2
            cells[i, 6] = 2
    return cells

def patterns(version):
    N = 17 + 4 * version
    cells = np.zeros((N, N))
    cells = finder(0, 0, cells)
    cells = finder(0, N-7, cells)
    cells = finder(N-7, 0, cells)
    for i in range(8):
        cells[i, 7] = 2
        cells[7, i] = 2
        cells[N-i-1, 7] = 2
        cells[N-8, i] = 2
        cells[7, N-i-1] = 2
        cells[i, N-8] = 2
    if 2 <= version and version <= 6:
        for i in range(5):
            for j in range(5):
                cells[N-9+i, N-9+j] = 3
        for i in range(3):
            for j in range(3):
                if i != 1 or j != 1:
                    cells[N-8+i, N-8+j] = 2
    
    # とりあえず黒
    for i in range(8):
        cells[8, i] = 2
        cells[i, 8] = 2
        cells[8, N-i-1] = 2
        cells[N-i-1, 8] = 2
    cells[8, 8] = 2

    cells = timing(cells)
    return cells

def qrcode(version, ecl, mode, text, mask='000'):
    if version > 2:
        return
    N = 17 + 4 * version
    cells = patterns(version)

    num_of_datacode = np.array([[19, 16, 13, 9], [34, 28, 22, 16]])
    # jump to p.39
    num_of_error_correction_codes = np.array([[7, 10, 13, 17], [10, 16, 22, 28]])
    num_of_error_correction_blocks = np.array([[1, 1, 1, 1], [1, 1, 1, 1]])
    # jump to p.73
    seiseitakosiki = { ## αのべき乗の指数
        '7': [0, 87, 229, 146, 149, 238, 102, 21],
        '10': [0, 251, 67, 46, 61, 118, 70, 64, 94, 32, 45],
        '17': [0, 43, 139, 206, 78, 43, 239, 123, 206, 214, 147, 24, 99, 150, 39, 243, 163, 136]
    }
    #  0  00000000 0 便宜的にa^-1としたほうがいい？
    # a^0 00000001 1
    # a^1 00000010 2
    # a^2 00000100 4
    # ...
    # a^254 10001110 142
    #(a^255 00000001 1)
    sisuus = np.concatenate([np.array([-1]), np.arange(255, dtype=np.int64)])
    decs = np.zeros(256, dtype=np.int64)
    decs[1] = 1
    for i in range(2, 256):
        decs[i] = decs[i-1] * 2
        if decs[i] > 255:
            decs[i] ^= int('100011101', 2)

    data = ''
    if mode == '8bit':
        data += '0100'

        if version < 10:
            data += format(len(text), '08b')
        for i in range(len(text)):
            data += format(ord(text[i]), '08b')

        data += '0000'

        for i in range(-len(data) % 8):
            data += '0'
        filler_count = 0
        for i in range(num_of_datacode[version-1, ecl] - len(data) // 8):
            if filler_count % 2 == 0:
                data += '11101100'
            else:
                data += '00010001'
            filler_count += 1
        print(data)
    elif mode == 'eisuji':
        data += '0010'
        data += format(len(text), '09b')
        text_length = len(text)
        eisuji_fugo = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'Y', 'U', 'V', 'W', 'X', 'Y', 'Z', ' ', '$', '%', '*', '+', '-', '.', '/', ':']
        for i in range(0, text_length, 2):
            if i + 1 < text_length:
                try:
                    data += format(eisuji_fugo.index(text[i]) * 45 + eisuji_fugo.index(text[i+1]), '011b')
                    print(eisuji_fugo.index(text[i]) * 45 + eisuji_fugo.index(text[i+1]), '011b')
                except:
                    print('英数字でない')
                    return
            else:
                try:
                    data += format(eisuji_fugo.index(text[i]), '06b')
                except:
                    print('英数字でない')
                    return

        data += '0000'

        for i in range(-len(data) % 8):
            data += '0'
        filler_count = 0
        for i in range(num_of_datacode[version-1, ecl] - len(data) // 8):
            if filler_count % 2 == 0:
                data += '11101100'
            else:
                data += '00010001'
            filler_count += 1
        for i in range(0, len(data), 8):
            print(data[i:i+8])
    else:
        raise ValueError('Invalid mode')

    # p.46
    necc = num_of_error_correction_codes[version-1, ecl]
    takosiki_sisuu = seiseitakosiki[str(necc)]
    f = [data[k:k+8] for k in range(0, len(data), 8)] + ['00000000' for i in range(necc)]
    f_dec = np.array([int(n, 2) for n in f])
    print(f_dec)
    for j in range(num_of_datacode[version-1, ecl]):
        # len(takosiki_sisuu['n']) = n+1 に注意
        if f_dec[j] == 0:
            print(j, f_dec[j-2:j+2])
            continue
        f_sisuu = np.array([sisuus[np.where(decs == dec)[0][0]] for dec in f_dec])
        g_sisuu = np.array([(takosiki_sisuu[i]+f_sisuu[j])%255 for i in range(necc+1)])
        g_dec = np.array([decs[np.where(sisuus == sisuu)[0][0]] for sisuu in g_sisuu])
        for i in range(necc+1):
            f_dec[j+i] ^= g_dec[i]
        print(j, g_sisuu)
        print(f_dec)
        print(j, [format(f_dec[j+1+k], '08b') for k in range(necc)])
    f_sisuu = np.array([sisuus[np.where(decs == dec)[0][0]] for dec in f_dec])
    for i in range(j+1, j+necc+1):
        data += format(f_dec[i], '08b')
    print([data[i:i+8] for i in range(0, len(data), 8)])

    # 残余ビット
    if version in [2, 3, 4, 5, 6]:
        data += '0000000'

    i = N - 1
    j = N - 1
    order0 = [0] * (N*N-N)
    for k in range(N*N-N):
        order0[k] = [i, j]
        if j > 6:
            if j % 2 == 0:
                j -= 1
            else:
                if j % 4 == 3:
                    if i == 0:
                        if j > 7:
                            j -= 1
                        else:
                            j = 5
                    else:
                        i -= 1
                        j += 1
                else:
                    if i == N-1:
                        j -= 1
                    else:
                        i += 1
                        j += 1
        else:
            if j % 2 == 1:
                j -= 1
            else:
                if j % 4 == 2:
                    if i == 0:
                        j -= 1
                    else:
                        i -= 1
                        j += 1
                else:
                    if i == N-1:
                        j -= 1
                    else:
                        i += 1
                        j += 1
    order = []
    i = 0
    for k in range(N*N-N):
        if cells[order0[k][0], order0[k][1]] < 2:
            order.append(order0[k])
            cells[order0[k][0], order0[k][1]] = int(data[i])
            i += 1
    print_qr(cells)

    for i in range(N):
        for j in range(N):
            if cells[i, j] < 2:
                if (mask == '000' and (i + j) % 2 == 0) or (mask == '001' and i % 2 == 0) or (mask == '010' and j % 3 == 0) or (mask == '011' and (i + j) % 3 == 0) :
                    cells[i, j] = (cells[i, j] + 1) % 2
    print_qr(cells)

    keisiki = ['01', '00', '11', '10'][ecl] + mask
    takosiki_sisuu = ['10100110111'[i] for i in range(11)]
    f = [(keisiki + '0000000000')[i] for i in range(15)]
    for i in range(5):
        if f[i] == '1':
            for j in range(11):
                if takosiki_sisuu[j] == f[i+j]:
                    f[i+j] = '0'
                else:
                    f[i+j] = '1'
        print(f)
    keisiki = [int(keisiki[i]) for i in range(5)] + [int(f[i]) for i in range(5, 15)]
    keisiki_mask = [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
    for i in range(15):
        keisiki[i] ^= keisiki_mask[i]
    print(keisiki)
    keisiki.reverse()
    for i in range(6):
        cells[i, 8] = keisiki[i]
        cells[8, N-i-1] = keisiki[i]
    for i in range(6, 8):
        cells[i+1, 8] = keisiki[i]
        cells[8, N-i-1] = keisiki[i]
    cells[8, 7] = keisiki[8]
    cells[N-8, 8] = 1
    cells[N-6, 8] = keisiki[8]
    for i in range(9, 15):
        cells[8, 14-i] = keisiki[i]
        cells[N+i-15, 8] = keisiki[i]
    
    cells_quiet = np.zeros((N+8, N+8))
    cells_quiet[4:-4, 4:-4] = cells

    return cells_quiet

cells = qrcode(1, 0, 'eisuji', 'KUALA 2025 /*QR CODE*/', '010')
plt.figure(figsize=(5, 5))
plt.imshow(np.array(cells) % 2, cmap='binary', interpolation='nearest')
plt.axis('off')
plt.show()
