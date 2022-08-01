import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

#元データの処理
df = pd.read_csv('/Users/suzukifumiya/Desktop/Python_advanced/stats.csv',encoding='UTF-8')
df = df.rename(columns={' first_name': 'first_name'})
df["first_name"]= df["first_name"].str.replace(' ', '')
df.insert(0,'full_name',df['first_name'].str.cat(df['last_name'],sep=' '))
df = df.set_index('full_name')
df=df.fillna(0)
df["ff_avg_speed"] = df["ff_avg_speed"]*1.60934
df["sl_avg_speed"] = df["sl_avg_speed"]*1.60934
df["ch_avg_speed"] = df["ch_avg_speed"]*1.60934
df["cu_avg_speed"] = df["cu_avg_speed"]*1.60934
df["si_avg_speed"] = df["si_avg_speed"]*1.60934
df["fc_avg_speed"] = df["fc_avg_speed"]*1.60934
df["fs_avg_speed"] = df["fs_avg_speed"]*1.60934
df["kn_avg_speed"] = df["kn_avg_speed"]*1.60934
df["K9"] = df["p_strikeout"]*9/df["p_formatted_ip"]
df["WHIP"] = (df["p_total_hits"]+df["p_walk"])/df["p_formatted_ip"]
df["KBB"] = df["p_strikeout"]/df["p_walk"]
df["PIP"] = df["pitch_count"]/df["p_formatted_ip"]
df["fastball_avg_speed"] = df[["ff_avg_speed","si_avg_speed","fc_avg_speed"]].max(axis=1)
df = df.round({"ff_avg_speed" : 2,"sl_avg_speed" : 2,"ch_avg_speed" : 2,"cu_avg_speed" : 2,"si_avg_speed" : 2,"fc_avg_speed" : 2,"fs_avg_speed" : 2,"kn_avg_speed" : 2,'K9': 2,"WHIP" : 2,"KBB" : 2,"PIP" : 2,"fastball_avg_speed" : 2})

#①シリーズの選択
year = [2022,2021]
option1 = st.sidebar.selectbox('シリーズを選択してください',year)
#DF1
df_year = df[df['year'] == option1]

#② 先発数の選択
#先発数をユニーク、ソートする＊0からだとエラーになる為、0を排除する為、1以上で設定
df_year_startingp_more1 = df_year[df_year['p_starting_p']>= 1]
startingps = df_year_startingp_more1['p_starting_p'].unique()
startingps = np.sort(startingps)
startingp  = []
for num in startingps:
    startingp.append(num)

#大谷翔平の現時点での登板数
df_year_SO = df_year.loc[['Shohei Ohtani']]
df_year_SO_StartNum = int(df_year_SO['p_starting_p'])
#セレクトボックスを利用
option2 = st.sidebar.selectbox('最低先発登板数を選択してください',startingp,index = df_year_SO_StartNum-1 )
st.sidebar.write('参考：大谷翔平の先発登板数は'+str(df_year_SO_StartNum) +'です。')
#DF2
df_year_startingp = df_year[df_year['p_starting_p']>= int(option2)]

#③ 対象投手の選択
#選手リストを作成

#複数選択可能なマルチセレクトを利用、デフォルトで大谷翔平を選択
player = st.sidebar.multiselect('選手を選択してください＊複数可',df_year_startingp.index,default='Shohei Ohtani')
for playername in player:
    player_name = playername

#DF3〜DF5までの処理
#DF3＊8つに絞った項目をランキングにし、その中の５つを元に総合値並びに総合値ランキングを作成
df_year_startingp_rank_false = df_year_startingp[["p_win","p_strikeout","K9","KBB","fastball_avg_speed"]].rank(ascending=False,method='min').astype(int)
df_year_startingp_rank_true = df_year_startingp[["p_era","WHIP","PIP"]].rank(ascending=True,method='min').astype(int)
df_year_rank = pd.concat([df_year_startingp_rank_false,df_year_startingp_rank_true],axis=1)
df_year_rank = df_year_rank.loc[:, ["p_win","p_era","p_strikeout","K9","WHIP","KBB","PIP","fastball_avg_speed"]]
df_year_rank.columns = ("p_win_rank","p_era_rank","p_strikeout_rank","K9_rank","WHIP_rank","KBB_rank","PIP_rank","fb_avg_speed_rank")
df_year_rank["ranking_point"] = df_year_rank["p_era_rank"]+df_year_rank["K9_rank"]+df_year_rank["WHIP_rank"]+df_year_rank["KBB_rank"]+df_year_rank["PIP_rank"]
df_year_rank["ranking_point_rank"] = df_year_rank[["ranking_point"]].rank(ascending=True,method='min').astype(int)
#DF4 DF2とDF3を結合　df_year_KeyItem_More_startingp_rank
df_year_KeyItem_More_startingp_rank = pd.concat([df_year_startingp,df_year_rank],axis=1)
df_year_KeyItem_More_startingp_rank = df_year_KeyItem_More_startingp_rank.loc[:, ["p_win","p_era","p_strikeout","K9","WHIP","KBB","PIP","fastball_avg_speed","ranking_point","p_win_rank","p_era_rank","p_strikeout_rank","K9_rank","WHIP_rank","KBB_rank","PIP_rank","fb_avg_speed_rank","ranking_point_rank"]]
#DF5 選択投手とトップランカーの結合
df_selected_player = df_year_KeyItem_More_startingp_rank.loc[player]
ranking_point_top = df_year_KeyItem_More_startingp_rank[['ranking_point']].sort_values(by='ranking_point',ascending=True).head(1)
ranking_point_top = ranking_point_top.index.astype(str)
Top_ranker = df_year_KeyItem_More_startingp_rank.loc[ranking_point_top]
df_selected_player_ranker = pd.concat([df_selected_player,Top_ranker],axis=0)

#streamlitの記述
st.title('MLB投手成績')

st.write('項目別TOP5')
left_column,center_column,right_column = st.columns(3)
rank_items = ["p_win","p_era","p_strikeout","K9","WHIP","KBB","PIP","fastball_avg_speed","ranking_point"]
for rank_item,i in zip(rank_items,range(len(rank_items))):
    
    if rank_item == "p_win" or rank_item == "p_strikeout" or rank_item == "p_strikeout" or rank_item == "K9" or rank_item == "KBB" or rank_item == "fastball_avg_speed":
        first_sort = False
    else:
        first_sort = True
    
    target = df_year_KeyItem_More_startingp_rank[[rank_item]].sort_values(by=rank_item,ascending=first_sort).head(5)
    target = target.reset_index()
    #altairに適用させるため、indexからカラムに変更しY軸として利用
    data = alt.Chart(target).mark_bar().encode(
        x=alt.X(rank_item,sort = None),
        y=alt.Y('full_name',axis=alt.Axis(title=None),sort = None)
        )#sort=Noneとしないと何故かチャートが反映しない/以下の構文は本来st.altair_chart(data, use_container_width=True)
    if (i+1)%3 == 1:left_column.altair_chart(data, use_container_width=True)
    elif (i+1)%3 == 2:center_column.altair_chart(data, use_container_width=True)
    else:right_column.altair_chart(data, use_container_width=True)

#streamlitのDataFrame用
df_data = df_selected_player_ranker[["p_win","p_era","p_strikeout","K9","WHIP","KBB","PIP","fastball_avg_speed","ranking_point"]]
df_rank = df_selected_player_ranker[["p_win_rank","p_era_rank","p_strikeout_rank","K9_rank","WHIP_rank","KBB_rank","PIP_rank","fb_avg_speed_rank","ranking_point_rank"]]
for Topranker in Top_ranker.index.astype(str):
    Topranker_name = Topranker

st.sidebar.write(player_name +'と'+ Topranker_name + '項目比較')
df_data = df_data.transpose()
st.sidebar.table(df_data.style.format('{:.1f}'))
st.sidebar.write(player_name +'と'+ Topranker_name + 'ランク比較')
df_rank = df_rank.transpose()
st.sidebar.table(df_rank)

left_column,right_column = st.columns(2)

left_column.write(player_name + "　詳細")
right_column.write(Topranker_name + "　詳細")
#DF6　円グラフ用データの処理(plotlyで作成)
pi_num_items = ["n_ff_formatted","n_sl_formatted","n_ch_formatted","n_cukc_formatted","n_sift_formatted","n_fc_formatted","n_fs_formatted","n_kn_formatted"]
df_pi_num = df_year_startingp[pi_num_items]

pi_ratio1 = []
for ratio in df_pi_num.loc[player].iloc[0]:#multiselectで返されるとリストの形になるので、locでDFの形から→ilocでシリーズの形に変換して取り出す
    pi_ratio1.append(ratio)
fig1 = px.pie(df_pi_num, values=pi_ratio1,names = pi_num_items,title='pitch ratio')
fig1.update_traces(textposition='inside', textinfo='percent+label')
left_column.plotly_chart(fig1, use_container_width=True)

pi_ratio2 = []
for ratio in df_pi_num.loc[Topranker]:
    pi_ratio2.append(ratio)
fig2 = px.pie(df_pi_num, values=pi_ratio2,names = pi_num_items,title='pitch ratio')
fig2.update_traces(textposition='inside', textinfo='percent+label')
right_column.plotly_chart(fig2, use_container_width=True)

#DF7 matplotlibで処理
pi_speed_items = ["ff_avg_speed","sl_avg_speed","ch_avg_speed","cu_avg_speed","si_avg_speed","fc_avg_speed","fs_avg_speed","kn_avg_speed"]
pi_spin_items = ["ff_avg_spin","sl_avg_spin","ch_avg_spin","cu_avg_spin","si_avg_spin","fc_avg_spin","fs_avg_spin","kn_avg_spin"]
df_pi_speed =df_year_startingp[pi_speed_items]
df_pi_spin =df_year_startingp[pi_spin_items]

#avarage_speed
fig = plt.figure(figsize=(10,6))
plt.barh(pi_speed_items,df_pi_speed.loc[player].iloc[0])
plt.xlabel('avarage_speed',fontsize=18)
plt.tick_params(labelsize=10)
plt.tight_layout()
plt.legend()
left_column.pyplot(fig)

fig = plt.figure(figsize=(10,6))
plt.barh(pi_speed_items,df_pi_speed.loc[Topranker])
plt.xlabel('avarage_speed',fontsize=18)
plt.tick_params(labelsize=10)
plt.tight_layout()
plt.legend()
right_column.pyplot(fig)

#avarage_spin
fig = plt.figure(figsize=(10,6))
plt.barh(pi_speed_items,df_pi_spin.loc[player].iloc[0])
plt.xlabel('avarage_spin',fontsize=18)
plt.tick_params(labelsize=10)
plt.tight_layout()
plt.legend()
left_column.pyplot(fig)

fig = plt.figure(figsize=(10,6))
plt.barh(pi_spin_items,df_pi_spin.loc[Topranker])
plt.xlabel('avarage_spin',fontsize=18)
plt.tick_params(labelsize=10)
plt.tight_layout()
plt.legend()
right_column.pyplot(fig)