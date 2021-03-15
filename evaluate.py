import pandas
import numpy as np
import matplotlib.pyplot as plt
import sys

def networkEv(d, dt):
    sequence = d.iloc[:,0]
    chunkSize = 253 # no 0,1,255

    # show graph of sequence
    # plt.plot(d.iloc[:,0], '.')
    # plt.title('sequence of packet')

    # show tx rate. (in another file)
    dt = np.array(dt).reshape(-1)
    print(dt.shape, sum(dt), len(dt))
    print(dt)
    plt.plot(1000./dt, '.-')
    plt.title('average frequency: %.2f'%(len(dt)*1000/sum(dt)) )
    plt.figure()


    # show correct data rate.
    # show correct-ratio by seq.
    chunkGood = []
    pre = sequence[0]
    good = 1   
    for i in sequence[1:]:
        if i == pre+1:
            good += 1
        elif i < pre:
            chunkGood += [good]
            good = 1
            if i !=2 :
                print('[dbg] loss %d packet at chunk %d-%d: '%(i-2, len(chunkGood), i) )
        else:
            print('[dbg] loss %d packet at chunk %d-%d: '%(i-pre-1, len(chunkGood), i) )
        pre = i
    chunkGood += [good]
    print( 'good/all packets: %d/%d'%(sum(chunkGood), (len(chunkGood)-2)*chunkSize + chunkGood[-1] + chunkGood[0]) )
    print( 'packets in each chunk:', chunkGood)
    plt.plot(chunkGood, 'o')
    plt.ylim(0,chunkSize)
    plt.title('Good packets received')
    plt.show()

    return 


def repeatEv(d):
    # plot raw sensors
    # ids = [3,4,10,11]
    ids = [19,20,26,27]
    press = d.iloc[:,ids]
    plt.plot(press, '.')
    plt.figure()

    # plot stats 
    avg = press.sum(axis = 1)
    plt.plot(avg)

    plt.show()
    return


def loadData(path):
    d = pandas.read_csv(path, header = None, prefix="col")
    # print(d.describe())
    # print(d.columns)
    # print(d.describe())
    return d

if __name__ == '__main__':
    if len(sys.argv) > 1:
        f = sys.argv[1]
    else:
        f = './data/03_11_single.txt'

    d = loadData(f)
    # dt = loadData('./data/03_11_time.txt')
    # networkEv(d, dt)
    repeatEv(d)