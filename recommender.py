import math
import time
import sys


#load 1M user and songs for training
f = open('train_triplets.txt', 'r')

print 'Extracting info from training data....\n'
sys.stdout.flush()

song_to_count = dict()  ## dictionary of songs and its count 
song_to_users = dict()  ## dictionary of songs and its users
unique_users = set([])  ## a list of unique users
user_play_count = dict()  ## dictionary of user and his play count
user_to_songs = dict()  ## dictionary of user and their songs

#n = float(len(f.readlines()))

#f.seek(0,0)

for line in f:
    user, song, count = line.strip().split('\t')
    
    if song in song_to_count:
        song_to_count[song]+=1
    else:
        song_to_count[song]=1
        
    if user not in unique_users:
        unique_users.add(user)
        user_play_count[user] = int(count)
    else:
        user_play_count[user] += int(count)
    
    if song in song_to_users:
        song_to_users[song].add(user)
    else:
        song_to_users[song]=set([user])
        
    if user in user_to_songs:
        user_to_songs[user].add(song)
    else:
        user_to_songs[user]=set([song])
        
    
#    if not i%30:    
#        sys.stdout.write("\r"+str(int(i/n*100))+" percent loaded")
#        sys.stdout.flush()
#    i+=1
#    
#print '100 percent loaded'
  #  print count
  #  if count == '':
  #      print user+'\t\t'+song
  #
                        
f.close()


#loading users list
print 'Creating user list....\n'
f = open('kaggle_users.txt')
users_list = list(map(lambda l: l.strip(), f.readlines()))
f.close()

#order song according to popualrity
songs_ordered = sorted( song_to_count.keys(), key = lambda s:song_to_count[s], reverse=True)


##changing song_to_user from songs to user mapping to songs to indices mapping

#creating users to indices mapping
user_to_index={}
for i,u in enumerate(unique_users):
    user_to_index[u]=i
    
#changing song_to_users
for song in song_to_users:
    indices_set=set()
    for user in song_to_users[song]:
        indices_set.add(user_to_index[user])
    song_to_users[song] = indices_set
    
del user_to_index

unique_users = list(unique_users)
##creating user_to_song mapping from testing data

print 'Extracting info from testing set....\n'
f = open('year1_test_triplets_visible.txt','r')

for line in f:
    user, song, _ = line.strip().split('\t')
    if user in user_to_songs:
        user_to_songs[user].add(song)
    else:
        user_to_songs[user]=set([song])

u2s=dict()        
f = open('year1_test_triplets_hidden.txt','r')
for line in f:
    user, song, _ = line.strip().split('\t')
    if user in u2s:
        u2s[user].add(song)
    else:
        u2s[user]=set([song])

tf_user_song = dict() # dictionary to store term frequency of user and song

def Score(user, song):
    #print 'Scoring for user- ',user,'and song-',song
    s = 0.4
    w_u = calculate_most_similiar(user, song_to_users[song])
    #print 'Max score is',w_u
    score_ui = 0.0
    for v in song_to_users[song]:
        w_u_v = similarity_user(user, v)
        #print 'Score for',user,'and',v,'is',w_u_v
        if w_u_v > w_u * s : 
            score_ui += ( w_u_v * 1/rating(v, song) ) 
    return score_ui
        

def calculate_most_similiar(user, user_list):
    w_max = 0
    for v in user_list:
        w_u_v = similarity_user(user, v)
        if w_max < w_u_v:
            w_max = w_u_v
    return w_max

def similarity_user(user,v) :
    w_u_v = 0.0
    for song in user_to_songs[user]:
        if song in user_to_songs[unique_users[v]]:
            w_u_v += calculate_idf(song)
    return w_u_v

#def calculate_tf(user, song):
#    if (user,song) in tf_user_song:
#        return tf_user_song[(user,song)]
#        
#    tf = 0.5
#    max_count = 0
#    
#    for s in user_to_songs[unique_users[user]]:
#        if max_count < int(user_song_count[(user,s)]) :
#            max_count = int(user_song_count[(user,s)])
#    
#    tf += ( 0.5 * int(user_song_count[(user,song)]) / max_count )
#    tf_user_song[(user,song)] = tf
#    return tf
#           

def calculate_idf( song ):
    n = len(unique_users)
    df = len( song_to_users[song])
    if df<>0:
        return math.log(n/df)
    else:
        return 0

def rating( user, song):
    if song in user_to_songs[user]:
        return user_play_count[user]
    else:
        return math.inf
        

def RecommendToUser(user):
    #print 'Creating recommendation for user- ',user
    score_song = dict()
    for song in songs_ordered:
        score_song[song] = Score(user, song)
        
    songs_sorted = sorted(score_song.keys(), key = lambda s : score_song[s], reverse=True)
    
    #for i in xrange(50):
    #    print score_song[songs_sorted[i]],
    #print '\n'
    
    cleaned_song = []
    for song in songs_sorted:
        if len(cleaned_song)>=tau:
            break
        if song not in user_to_songs[user]:
            cleaned_song += [song]
            
    #for i in xrange(3):
    #    print '(',cleaned_song[i],score_song[cleaned_song[i]],')',
    #print '\n\n'
    
    return cleaned_song
    
def RecommendToUsers(user_list):
    print 'Recommending to users...\n'
    sti=time.clock()
    rec4users = []
    for i,user in enumerate(user_list):
        rec4users.append(RecommendToUser(user))
        cti=time.clock()-sti
        if not (i+1)%10:
            print '%d]  user %s with %d songs tot secs: %f (%f)'%((i+1),user,len(user_to_songs[user]),cti,cti/(i+1))
    print
    return rec4users
    
def SaveRecommendation(r,songs_file,output_file):
    print 'Saving recommendation saved to', output_file
    f = open(songs_file, 'r')
    song_to_index = dict(map(lambda line: line.strip().split(' '),f.readlines()))
    f.close()
    f = open(output_file,'w')
    for r_s in r:
        indices = map(lambda s: song_to_index[s], r_s)
        f.write(" ".join(indices)+'\n')
        
        
    f.close()
    print 'Saved indices of songs instead of song_ids.'
    print 'Done \n'
    
    
def AP(rsong_list , songs_user):
    nu = len(rsong_list)
    n_s_c = 0.0
    ap = 0.0
    for i,song in enumerate(rsong_list):
        if i>=tau:
            break
        if song in songs_user:
            n_s_c+=1.0
            ap+=(n_s_c/(i+1))
            #print int(n_s_c),
        #else:
            #print 0,
    print
    nu = min(nu,tau)
    return ap/nu
    
def mAP(user_list, rec_songs_list):
    mAp = 0.0
    n = len(user_list)
    for i,u in enumerate(user_list):
        if u in user_to_songs:
            mAp+=AP(rec_songs_list[i], u2s[u])
    return mAp/n
    
if __name__=='__main__':
    global tau ##no of songs to be recommended per user
    
    print 'There are 1500 users in the training set and 150 in testing set as a subset of original dataset.\n'
    
    tau = input('Enter the maximum number of recommendation to make (<=500) - ')
    no = input('Enter no of user to recommended out of 1500 - ')
    print
    
    users = users_list[1:no]
    
    recommended_songs = RecommendToUsers(users)

    SaveRecommendation(recommended_songs,"kaggle_songs.txt","recommended_songs.txt")       

    x = mAP(users, recommended_songs)
    print 'mean Average Precision obtained is', x 