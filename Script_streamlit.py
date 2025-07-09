import streamlit as st
import requests
import os
import json
from datetime import datetime
import webbrowser
import warnings
import time
import subprocess
from io import BytesIO
import zipfile



warnings.filterwarnings("ignore", message=".*missing ScriptRunContext!*")

Api = st.secrets['API'] 

API_KEY = Api['API_KEY']

URL_LIST = 'https://api.grid.gg/central-data/graphql'
headers = {"x-api-key": API_KEY}


team_id_dict = {
'T1': {'id': '47494', 'name': 'T1'},
'DRX': {'id': '47961', 'name': 'DRX'},
'DK': {'id': '48179', 'name': 'Dplus KIA'},
'BRO': {'id': '52817', 'name': 'OKSavingsBank BRION'},
'GEN': {'id': '47558', 'name': 'Gen.G'},
'HLE': {'id': '406', 'name': 'Hanwha Life Esports'},
'KT': {'id': '407', 'name': 'KT Rolster'},
'KDF': {'id': '3483', 'name': 'KWANGDONG FREECS'},
'FOX': {'id': '4035', 'name': 'FearX'},
'NS': {'id': '52747', 'name': 'NongShim REDFORCE'},
'TH': {'id': '47435', 'name': 'Team Heretics'},
'BDS':  {'id': '52661', 'name': 'Team BDS'},
'VIT': {'id': '47370', 'name': 'Team Vitality'},
'JL': {'id': '48125', 'name': 'Joblife'},
'M8': {'id': '53189', 'name': 'Gentle Mates'},
'IJC': {'id': '53154', 'name': 'Ici Japon Corp'},
'KCB': {'id': '48007', 'name': 'Karmine Corp Blue'},
'GL': {'id': '20297', 'name': 'Galions'},
'BKR': {'id': '20306', 'name': 'BK ROG Esports'},
'SLY': {'id': '48331', 'name': 'Solary'},
'VITB': {'id': '3972', 'name': 'Vitality.Bee'},
'GW': {'id': '4133', 'name': 'GameWard'},
'BDSA': {'id': '3985', 'name': 'Team BDS Academy'},
'KC': {'id': '53165', 'name': 'Karmine Corp'},
"AL": {'id': '20483', 'name': "Anyone's Legend"},
'BLG': {'id': '356', 'name': 'Bilibili Gaming'},
'EDG': {'id': '47509', 'name': 'EDward Gaming'},
'FPX': {'id': '47514', 'name': 'FunPlus Phoenix'},
'IG': {'id': '47472', 'name': 'Invictus Gaming'},
'JDG': {'id': '52796', 'name': 'Beijing JDG Intel Esports Club'},
'LGD': {'id': '368', 'name': 'LGD Gaming'},
'LNG': {'id': '52726', 'name': 'Suzhou LNG Esports'},
'OMG': {'id': '369', 'name': 'Oh My God'},
'RA': {'id': '47922', 'name': 'Rare Atom'},
'RNG': {'id': '47319', 'name': 'Royal Never Give Up'},
"WE": {'id': '52910', 'name': "Xi'an Team WE"},
'TT': {'id': '52606', 'name': 'THUNDER TALK GAMING'},
'TES': {'id': '375', 'name': 'Top Esports'},
'UP': {'id': '3113', 'name': 'Ultra Prime'},
'NIP': {'id': '52905', 'name': 'Shenzhen NINJAS IN PYJAMAS'},
'WBG': {'id': '52822', 'name': 'WeiboGaming FAW AUDI'},
'RGE': {'id': '106', 'name': 'Rogue'},
'G2': {'id': '47380', 'name': 'G2 Esports'},
'GX': {'id': '53168', 'name': 'GIANTX'},
'MAD': {'id': '47619', 'name': 'MAD Lions'},
'SK': {'id': '353', 'name': 'SK Gaming'},
'FNC': {'id': '47376', 'name': 'Fnatic'}
}

def get_query_scrim(start_time, end_time):
    return f"""  
    {{
        allSeries (
            first: 50,
            filter: {{
                titleId: 3
                types: SCRIM
                startTimeScheduled: {{
                    gte: "{start_time}"
                    lte: "{end_time}"
                }}
            }}
            orderBy: StartTimeScheduled
            orderDirection: DESC
        ) {{
            edges {{
                node {{
                    id
                    startTimeScheduled
                    teams {{ baseInfo {{ id name }} }}
                }}
            }}
        }}
    }}"""

def get_query_competitive(start_time, end_time, team_id):
    return f"""  
    {{
        allSeries (
            first: 50,
            filter: {{
                titleId: 3
                types: ESPORTS
                startTimeScheduled: {{
                    gte: "{start_time}"
                    lte: "{end_time}"
                }}
                teamIds: {{ in: "{team_id}" }}
            }}
            orderBy: StartTimeScheduled
            orderDirection: DESC
        ) {{
            edges {{
                node {{
                    id
                    startTimeScheduled
                    teams {{ baseInfo {{ id name }} }}
                    format {{ id name }}
                }}
            }}
        }}
    }}"""

def get_list(query):
    response = requests.post(URL_LIST, json={'query': query}, headers=headers)
    response.raise_for_status()
    return response.json()

def get_tag_by_team_id(team_id):
    for tag, data in team_id_dict.items():
        if data['id'] == team_id:
            return tag
    return None

def get_url_download(series_id, sequence_number):
    return f'https://api.grid.gg/file-download/replay/riot/series/{series_id}/games/{sequence_number}'

"""def get_rofl(series_id, sequence_number, team_code):
    url = get_url_download(series_id, sequence_number)
    res = requests.get(url, headers={'x-api-key': API_KEY})
    if res.status_code == 200:
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{team_code}.rofl")
        with open(file_path, 'wb') as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)
        return f"✅ Saved: {file_path}"
    else:
        return f"❌ Failed to download: {url} (Status {res.status_code})"""
    


def get_rofl(series_id, sequence_number, team_code):
    url = get_url_download(series_id, sequence_number)
    res = requests.get(url, headers={'x-api-key': API_KEY})
    if res.status_code == 200:
        buffer = BytesIO(res.content)
        return buffer, team_code  # return as a tuple
    else:
        return None, f"❌ Failed to download: {url} (Status {res.status_code})"


def Listgames_download_EMH(start_date, end_date, team_tag, game_type):
    query = (get_query_competitive(start_date, end_date, team_id_dict[team_tag]['id'])
             if game_type == 'competitive' else
             get_query_scrim(start_date, end_date))
    
    result = get_list(query)
    nodes = result['data']['allSeries']['edges']
    status_list = []

    for node in nodes:
        node_data = node['node']
        gamedate = datetime.strptime(node_data['startTimeScheduled'], "%Y-%m-%dT%H:%M:%SZ")
        series_id = node_data['id']
        format_id = node_data.get('format', {}).get('id', '1')
        num_games = {'1': 1, '3': 3, '4': 5}.get(format_id, 1)

        for i in range(num_games):
            try:
                t1 = get_tag_by_team_id(node_data['teams'][0]['baseInfo']['id']) or node_data['teams'][0]['baseInfo']['name']
                t2 = get_tag_by_team_id(node_data['teams'][1]['baseInfo']['id']) or node_data['teams'][1]['baseInfo']['name']
                if game_type == 'competitive':
                    name = f"{gamedate.strftime('%m-%d')}_{t1}_vs_{t2}_{i+1}"
                else:
                    name = f"{gamedate.strftime('%m-%d-T%H-%M')}_{t1}_vs_{t2}"
                result_msg = get_rofl(series_id, i+1, name)
                if isinstance(result_msg, tuple):
                    st.session_state.replay_buffers.append(result_msg)
                else:
                    st.session_state.replay_errors.append(result_msg)
            except Exception as e:
                status_list.append(f"❌ Error downloading game {i+1}: {e}")
    return status_list

# === STREAMLIT UI ===
st.set_page_config(page_title="LoL Replay Downloader", layout="centered")
st.title("🎮 LoL Competitive Replay Downloader")

# Session state to store download buffers and errors
if "replay_buffers" not in st.session_state:
    st.session_state.replay_buffers = []
if "replay_errors" not in st.session_state:
    st.session_state.replay_errors = []

team_tag = st.selectbox("Select Team", list(team_id_dict.keys()))
game_type = st.selectbox("Select Type", ['competitive', 'scrim'])

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date")
with col2:
    end_date = st.date_input("End Date")

if st.button("Download Replays"):
    st.session_state.replay_buffers.clear()
    st.session_state.replay_errors.clear()

    start = start_date.strftime("%Y-%m-%dT00:00:00Z")
    end = end_date.strftime("%Y-%m-%dT00:00:00Z")

    with st.spinner("Downloading..."):
        _ = Listgames_download_EMH(start, end, team_tag, game_type)

# Show all available replays for download
if st.session_state.replay_buffers:
    st.success(f"{len(st.session_state.replay_buffers)} replays ready:")

    # 🔁 Download individual buttons
    for buffer, name in st.session_state.replay_buffers:
        st.download_button(
            label=f"Download {name}.rofl",
            data=buffer,
            file_name=f"{name}.rofl",
            mime="application/octet-stream",
            key=name  # Unique key
        )

    # 📦 Build zip archive in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for buffer, name in st.session_state.replay_buffers:
            buffer.seek(0)
            zip_file.writestr(f"{name}.rofl", buffer.read())
    zip_buffer.seek(0)

    # 🔘 Single download button for ZIP
    st.download_button(
        label="📦 Download All as ZIP",
        data=zip_buffer,
        file_name="all_replays.zip",
        mime="application/zip"
    )

# Show any download errors
if st.session_state.replay_errors:
    for error in st.session_state.replay_errors:
        st.error(error)

# Optional: Clear all results manually
if st.session_state.replay_buffers or st.session_state.replay_errors:
    if st.button("Clear Downloads"):
        st.session_state.replay_buffers.clear()
        st.session_state.replay_errors.clear()


# Launch streamlit



