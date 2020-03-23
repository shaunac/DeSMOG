import re
import pandas as pd
import os

def regularize_title(t):
    return re.sub("[^A-Za-z0-9.,']+", ' ', t.lower().strip()).strip()

def d_l_dist(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1,lenstr1+1):
        d[(i,-1)] = i+1
    for j in range(-1,lenstr2+1):
        d[(-1,j)] = j+1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i,j)] = min(
                           d[(i-1,j)] + 1, # deletion
                           d[(i,j-1)] + 1, # insertion
                           d[(i-1,j-1)] + cost, # substitution
                          )
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost) # transposition

    return d[lenstr1-1,lenstr2-1]

def is_same(u1,u2):
    #Djk ≤ 0.2 × Min.[|Tj|,|Tk|]
    # determine Damerau-Levensthtein edit distance
    D_jk = d_l_dist(u1,u2)
    t_j = len(u1)
    t_k = len(u2)
    min_ = min(t_j,t_k)
    return D_jk < 0.2*min_



if __name__ == "__main__":
    combined_df_ft = pd.read_pickle('temp_combined_df_with_fulltext.pkl')
    outlet_groups = combined_df_ft.groupby('domain')
    print(combined_df_ft.shape)

    for outlet in outlet_groups.first().index:
        outlet_df = outlet_groups.get_group(outlet)
        print('Processing {} with {} URLS'.format(outlet,len(outlet_df)))
        for ix1 in range(len(outlet_df.index)-1):
            for ix2 in range(ix1+1,len(outlet_df.index)):
                index1 = outlet_df.index[ix1]
                index2 = outlet_df.index[ix2]
                #print('Comparing titles of {} and {}...'.format(index1,index2))
                t1 = regularize_title(outlet_df.loc[index1].title)
                t2 = regularize_title(outlet_df.loc[index2].title)
                #print('Titles: {}, {}'.format(t1,t2))
                if is_same(t1,t2):
                    print('Match found!')
                    combined_df_ft.at[index1,'title'] = t2
                    print('New df title values:{}, {}'.format(combined_df_ft.loc[index2].title,
                         combined_df_ft.loc[index1].title))

        combined_df_ft.to_pickle('temp_combined_df_with_fulltext.pkl')

    print('Finished! Saving...')
    combined_df_ft.to_pickle('temp_combined_df_with_fulltext.pkl')
