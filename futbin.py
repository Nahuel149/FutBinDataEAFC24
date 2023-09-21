import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
import MySQLdb

# Define your MySQL database connection parameters
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Drac0456149!',
    'database': 'FUTBIN'
}

# Initialize an empty list to store the data
data = []

fifa = {
    '24': 'FIFA24'
}

cardColumns = ['ID', 'Name', 'Rating', 'Price', 'SkillsMoves', 'WeakFoot',
               'Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending',
               'Physicality', 'Height', 'Popularity', 'Inches', 'Unknown', 'Totalsum',
               'Ingamesum', 'Nothing', 'Position', 'Club',
               'Country', 'League', 'NationPic', 'ClubPic', 'PlayerPic']

C = open('FutBinCards24.csv', 'w')  # Change the output file name if needed
C.write(','.join(cardColumns) + '\n')
C.close()

for key, value in fifa.items():
    id = 0
    ID = 0
    print('Doing ' + value)
    FutBin = requests.get('https://www.futbin.com/' + key + '/players', headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'})
    bs = BeautifulSoup(FutBin.text, 'html.parser')
    try:
        TotalPages = str(bs.findAll('li', {'class': 'page-item '})[-1].text).strip()
    except IndexError:
        TotalPages = str(bs.findAll('li', {'class': 'page-item'})[-2].text).strip()
    print('Number of pages to be parsed for FIFA ' + key + ' is ' + TotalPages + ' Pages')
    for page in range(1, int(TotalPages) + 1):
        FutBin = requests.get('https://www.futbin.com/' + key + '/players?page=' + str(page), headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'})
        bs = BeautifulSoup(FutBin.text, 'html.parser')
        table = (bs.find('table', {'id': 'repTb'}))
        tbody = table.find('tbody')
        extracted = tbody.findAll('tr', {'class': re.compile('player_tr_\d+')})
        Card = []
        for cardDetails in extracted:
            teamLeague = [i['data-original-title'] for i in cardDetails.findAll('a', {'href': re.compile('^/24/players\?page=')}) if 'data-original-title' in i.attrs]

            # Extract player's full name
            player_name_element = cardDetails.find('a', {'class': 'player_name_players_table get-tp'})
            if player_name_element:
                player_full_name = player_name_element.text.strip()
            else:
                player_full_name = 'N/A'  # Set a default value if player name is not found

            # Extract skills and weak foot ratings
            skills_weak_foot = cardDetails.findAll('td')[7].text.strip().split()
            if len(skills_weak_foot) >= 2:
                SkillsMoves = skills_weak_foot[0]
                WeakFoot = skills_weak_foot[1]
            else:
                SkillsMoves = 'N/A'  # or any default value you prefer
                WeakFoot = 'N/A'  # or any default value you prefer

            # Extract WorkRate and split it into two values
            work_rates = cardDetails.findAll('td')[8].text.strip().split()
            HighWorkRate = work_rates[0]
            LowWorkRate = work_rates[2] if len(work_rates) >= 3 else 'N/A'

            # Extract revision and body type
            split_result = cardDetails.text.strip().replace(' \\ ', '\\').replace(' | ', '|').split('       ')
            if len(split_result) > 1:
                revision = split_result[1]
            else:
                revision = ''  # Set a default value or an empty string if data is not present

            matches = re.findall("\s(\D*\s\D+)", cardDetails.text.strip(), re.IGNORECASE)
            if len(matches) > 1:
                body = [matches[1].split()[0]]
            else:
                body = ['N/A']  # Set a default value if data is not present

            cardDetails = re.sub("\s\D*\s\D+", " ", cardDetails.text.strip()).split()
            cardDetails.insert(0, id)
            cardDetails.extend([' '.join(revision.split()[1:])])
            cardDetails.extend(body)
            cardDetails.extend(teamLeague)

            # Store the player's full name and other information in 'Card' list
            cardDetails[1] = player_full_name
            Card.append(cardDetails)
            print(cardDetails)
            id += 1

        webpages = ['https://www.futbin.com' + str(i['data-url']).replace(' ', '%20') for i in extracted]
        overall = {}
        for webpage in webpages:
            d = {}
            json_data = ''
            profile = requests.get(webpage, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'})
            bs = BeautifulSoup(profile.text, 'html.parser')
            images = [i['src'] for i in bs.findAll('img', id=re.compile('player_nation|player_club|player_pic'))[0:3]]
            Card[webpages.index(webpage)].extend(images)

            # Error handling for 'info_content' element
            info = bs.find('div', {'id': 'info_content'})
            if info:
                d.update(dict(zip([str(i.text).replace('Name', 'Fullname').strip() for i in info.findAll('th')], [str(i.text).strip() for i in info.findAll('td')])))
                overall[ID] = d
                json_data += json.dumps(overall, indent=4, separators=(',', ': '), sort_keys=True)
                ID += 1
            else:
                print("Element with id 'info_content' not found on the page.")

        df = pd.DataFrame(Card, columns=cardColumns)
        print(df)
        df.to_csv('FutBinCards24.csv', mode='a', header=False, sep=',', encoding='utf-8', index=False)

        # After collecting the data in the 'Card' list
        # Initialize a pandas DataFrame with the collected data
        df = pd.DataFrame(Card, columns=cardColumns)

        # Establish a connection to the MySQL database
        conn = MySQLdb.connect(**mysql_config)

        # Create a MySQL cursor
        cursor = conn.cursor()

        # Iterate through the DataFrame and insert rows into the MySQL table
        for _, row in df.iterrows():
            # Create a dictionary to store the column values
            insert_values = {}

            # Iterate over the columns you want to check for empty values
            for column_name in cardColumns:
                if column_name in ('Nothing', 'Unknown'):
                    if row[column_name] == '':
                        insert_values[column_name] = None  # Set to NULL if the data is empty
                    else:
                        try:
                            insert_values[column_name] = int(row[column_name])  # Convert the valid integer value
                        except ValueError:
                            insert_values[column_name] = None  # Set to NULL if the value can't be converted to an integer
                else:
                    if row[column_name] == '':
                        insert_values[column_name] = None  # Set to NULL if the data is empty
                    else:
                        if column_name in ('SkillsMoves', 'WeakFoot', 'Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending', 'Physicality'):
                            insert_values[column_name] = int(row[column_name])  # Convert the valid integer value
                        else:
                            insert_values[column_name] = row[column_name]

            # Define your INSERT statement based on your table structure
            insert_sql = """
            INSERT INTO EAFC24 (Name, Rating, Price, SkillsMoves, WeakFoot, Pace, Shooting, Passing, Dribbling, Defending, Physicality, Height, Popularity, Inches, Unknown, Totalsum, Ingamesum, Nothing, Position, Club, Country, League, NationPic, ClubPic, PlayerPic)
            VALUES (%(Name)s, %(Rating)s, %(Price)s, %(SkillsMoves)s, %(WeakFoot)s, %(Pace)s, %(Shooting)s, %(Passing)s, %(Dribbling)s, %(Defending)s, %(Physicality)s, %(Height)s, %(Popularity)s, %(Inches)s, %(Unknown)s, %(Totalsum)s, %(Ingamesum)s, %(Nothing)s, %(Position)s, %(Club)s, %(Country)s, %(League)s, %(NationPic)s, %(ClubPic)s, %(PlayerPic)s)
            """
            
            # Execute the INSERT statement with the insert_values dictionary
            cursor.execute(insert_sql, insert_values)

        # Commit the changes and close the cursor and connection
        conn.commit()
        cursor.close()
        conn.close()